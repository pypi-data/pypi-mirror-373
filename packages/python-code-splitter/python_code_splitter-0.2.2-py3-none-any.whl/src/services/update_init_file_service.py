from dataclasses import dataclass

from src.entities.file import File
from src.services.generate_import_statement_service import (
    GenerateImportStatementService,
)


@dataclass(frozen=True)
class UpdateInitFileService:
    init_file: File
    moved_files: list[File]

    def execute(self) -> str:
        # Generate import statements for the moved Blocks
        original_init_file_text = self.init_file.path.read_text()
        import_statement = GenerateImportStatementService(
            init_file=self.init_file, moved_files=self.moved_files
        ).execute()
        all_text = (
            '\n__all__ = [\n    "'
            + '",\n    "'.join([block.name for file in self.moved_files for block in file.blocks])
            + '"\n]'
        )
        # Update __init__.py file
        new_init_file_text = "".join(import_statement) + original_init_file_text + all_text
        self.init_file.path.write_text(new_init_file_text)
        return new_init_file_text
