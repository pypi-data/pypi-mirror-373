import ast
import re
from dataclasses import dataclass
from pathlib import Path

from src.entities.block import Block
from src.entities.file import File
from src.types.block_type import BlockType


def ast2blocktype(node: ast.AST) -> BlockType:
    if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
        return BlockType.IMPORT
    if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
        return BlockType.FUNCTION
    if isinstance(node, ast.ClassDef):
        return BlockType.CLASS
    if isinstance(node, ast.Assign) or isinstance(node, ast.Constant):
        return BlockType.VALUE
    return BlockType.OTHER


@dataclass(frozen=True)
class LoadFileService:
    file_path: Path

    class ParseError(Exception):
        pass

    def execute(self) -> File:
        """Read the file and split it into classes, functions, and others"""
        assert self.file_path.is_file(), f"Error: File '{self.file_path}' does not exist."
        with self.file_path.open(mode="r") as file:
            lines = file.readlines()
        blocks: list[Block] = []
        tree = ast.parse("".join(lines))
        number = 0
        for node in ast.iter_child_nodes(tree):
            if not isinstance(
                node,
                (
                    ast.AsyncFunctionDef,
                    ast.FunctionDef,
                    ast.ClassDef,
                    ast.Module,
                    ast.Import,
                    ast.ImportFrom,
                    ast.Assign,
                    ast.Constant,
                ),
            ):
                continue
            if name := getattr(node, "name", None):
                pass
            elif isinstance(node, ast.Assign) or isinstance(node, ast.Constant):
                pattern = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*=")
                for line in lines[number : node.end_lineno]:
                    if match := pattern.match(line):
                        name = match and match.groups()[0]
            if name is None:
                name = "other"
            blocks.append(
                Block(
                    lines=lines[number : node.end_lineno],
                    name=name,
                    type=ast2blocktype(node=node),
                )
            )
            number = node.end_lineno
        if number < len(lines):
            blocks.append(
                Block(
                    lines=lines[number:],
                    name="other",
                    type=BlockType.OTHER,
                )
            )
        # Check if the total number of lines in the split blocks matches the original number of lines
        assert len(lines) == sum([len(block.lines) for block in blocks])
        return File(path=self.file_path, blocks=blocks)
