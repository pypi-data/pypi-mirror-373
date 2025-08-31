from dataclasses import dataclass

from src.entities.file import File
from src.services.generate_import_statement_service import (
    GenerateImportStatementService,
)


@dataclass(frozen=True)
class AttachImportStatementsService:
    moved_files: list[File]
    init_file: File

    def execute(self) -> None:
        for moved_file in self.moved_files:
            import_statement = GenerateImportStatementService(
                moved_files=self.moved_files,
                init_file=self.init_file,
                exclude_file=moved_file,
            ).execute()
            text = moved_file.path.read_text()
            text = "".join(import_statement) + text
            moved_file.path.write_text(text)
