from dataclasses import dataclass

from src.types.block_type import BlockType
from src.types.lines import Lines
from src.utils import to_snake_case


@dataclass(frozen=True)
class Block:
    type: BlockType
    name: str
    lines: Lines

    @property
    def file_name(self):
        if self.type == BlockType.CLASS:
            return f"{to_snake_case(self.name)}.py"
        return f"{self.name}.py"
