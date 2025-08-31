from dataclasses import dataclass
from typing import Callable, Optional, Tuple

from src.entities.file import File
from src.types.block_type import BlockType


@dataclass
class MoveBlocksToNewFilesService:
    original_file: File
    target_block_types: list[BlockType]
    handler_for_each_move: Optional[Callable] = None

    def execute(self) -> Tuple[File, list[File]]:
        # Move each class (function) from the input file to individual new files
        # Create new Module Directory
        new_dir_path = self.original_file.path.parent / self.original_file.path.stem
        new_dir_path.mkdir(parents=True, exist_ok=True)
        new_files = []
        skipped_blocks = []

        blocks = self.original_file.blocks
        while blocks:
            block = blocks.pop()
            if block.type.value not in self.target_block_types:
                skipped_blocks.append(block)
                continue
            # Create the destination file
            new_file = File(path=new_dir_path / block.file_name, blocks=[block])
            old_file = File(path=self.original_file.path, blocks=blocks + list(reversed(skipped_blocks)))
            new_files.append(new_file)
            # Write
            new_file.write()
            old_file.write()
            if self.handler_for_each_move:
                self.handler_for_each_move(new_file=new_file, old_file=old_file, block=block)
        return old_file, new_files
