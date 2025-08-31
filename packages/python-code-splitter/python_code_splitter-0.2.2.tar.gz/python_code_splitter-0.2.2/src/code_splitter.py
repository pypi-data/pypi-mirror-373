from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from src.entities.block import Block
from src.entities.file import File
from src.services.attach_import_statements_service import AttachImportStatementsService
from src.services.load_file_service import LoadFileService
from src.services.move_blocks_to_new_files_service import MoveBlocksToNewFilesService
from src.services.update_init_file_service import UpdateInitFileService
from src.types.block_type import BlockType
from src.utils import git


@dataclass(frozen=True)
class CodeSplitter:
    original_file_path: Path
    git_commit: bool
    target_block_types: Literal[BlockType.CLASS, BlockType.FUNCTION]

    def execute(self):
        # 1. Load the target file
        original_file: File = LoadFileService(file_path=self.original_file_path).execute()

        # 2 Create new git branch
        if self.git_commit:
            branch_name = "split/" + str(self.original_file_path).replace("/", "_").replace(".py", "")
            git(f"checkout -b {branch_name}")

        # 3. Move class and function definitions from the original file to new files one by one
        def git_commit_for_each_move(new_file: File, old_file: File, block: Block):
            if self.git_commit:
                # NOTE: Committed temporarily to avoid creating diffs for reviewers
                git(f"add {new_file.path} {old_file.path}")
                git(f'commit -m "[Auto] Move {block.type} {block.name} to {new_file.path}."')

        original_file, moved_files = MoveBlocksToNewFilesService(
            original_file=original_file,
            target_block_types=self.target_block_types,
            handler_for_each_move=git_commit_for_each_move,
        ).execute()

        # 4. Move the original file to __init__.py
        init_file_path = original_file.path.parent / original_file.path.stem / "__init__.py"
        git(f"mv {original_file.path} {init_file_path}")
        if self.git_commit:
            git(f"add {init_file_path}")
            git(f'commit -m "[Auto] git mv {original_file.path} {init_file_path}"')
        init_file = File(path=init_file_path, blocks=original_file.blocks)

        # 5. Attach import statements for moved files to the __init__.py file
        ## sort by block type and block name
        moved_files = sorted(moved_files, key=lambda file: (file.blocks[0].type.value, file.blocks[0].name))
        UpdateInitFileService(
            init_file=init_file,
            moved_files=moved_files,
        ).execute()
        if self.git_commit:
            git(f"add {init_file.path}")
            git(f'commit -m "[Auto] Attached import statements for moved files to {init_file.path}."')

        # 6. Attache import statements to each file
        AttachImportStatementsService(
            moved_files=moved_files,
            init_file=init_file,
        ).execute()
        if self.git_commit:
            git(f"add {init_file_path.parent}")
            git(f'commit -m "[Auto] Attached import statements for the moved files to {init_file.path.parent}."')
