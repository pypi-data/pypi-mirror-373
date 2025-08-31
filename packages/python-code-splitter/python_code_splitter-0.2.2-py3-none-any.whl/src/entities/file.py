from dataclasses import dataclass
from pathlib import Path

from src.entities.block import Block


@dataclass(frozen=True)
class File:
    path: Path
    blocks: list[Block]

    def write(self):
        with self.path.open(mode="w") as f:
            for block in self.blocks:
                f.writelines(block.lines)
