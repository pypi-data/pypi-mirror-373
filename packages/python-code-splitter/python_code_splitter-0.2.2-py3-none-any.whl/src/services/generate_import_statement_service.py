from dataclasses import dataclass
from typing import Optional

from src.entities.file import File
from src.types.block_type import BlockType
from src.types.lines import Lines
from src.utils import to_snake_case


@dataclass(frozen=True)
class GenerateImportStatementService:
    moved_files: list[File]
    init_file: File
    exclude_file: Optional[File] = None

    def execute(self) -> Lines:
        # Generate import statements for moved and non-moved blocks
        new_dir_path = str(self.init_file.path.parent).replace("/", ".")
        import_statement = []
        # Add import statements from the original file
        for non_moved_block in filter(lambda block: block.type == BlockType.IMPORT, self.init_file.blocks):
            import_statement += non_moved_block.lines
        # Add import statements for moved blocks
        for moved_file in filter(lambda file: file != self.exclude_file, self.moved_files):
            for block in moved_file.blocks:
                import_statement.append(f"from {new_dir_path}.{to_snake_case(block.name)} import {block.name}\n")
        # Add import statements for non-moved blocks
        for non_moved_block in filter(
            lambda block: block.type not in [BlockType.IMPORT, BlockType.OTHER], self.init_file.blocks
        ):
            import_statement.append(f"from {new_dir_path} import {non_moved_block.name}\n")
        return import_statement
