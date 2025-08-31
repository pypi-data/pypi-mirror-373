from pathlib import Path

import pytest

from src.entities.block import Block
from src.services.load_file_service import LoadFileService
from src.types.block_type import BlockType


def test_load_file_service():
    service = LoadFileService(file_path=Path("tests/samples/models.py"))
    result = service.execute()
    assert result.path == Path("tests/samples/models.py")
    assert result.blocks[0] == Block(
        type=BlockType.IMPORT,
        name="other",
        lines=[
            "# This is a sample file for testing.\n",
            '"""\n',
            "This is a sample file for testing.\n",
            '"""\n',
            "\n",
            "import sys\n",
        ],
    )
    assert result.blocks[1] == Block(type=BlockType.IMPORT, name="other", lines=["from dataclasses import dataclass\n"])
    assert result.blocks[2] == Block(
        type=BlockType.IMPORT, name="other", lines=["from typing import (\n", "    Callable\n", ")\n"]
    )
    assert result.blocks[3] == Block(type=BlockType.IMPORT, name="other", lines=["from pathlib import Path\n"])
    assert result.blocks[4] == Block(type=BlockType.VALUE, name="StrAlias", lines=["\n", "StrAlias = str\n"])
    assert result.blocks[5] == Block(
        type=BlockType.VALUE,
        name="FunctionAlias",
        lines=["# This is very important value\n", "FunctionAlias = Callable[[], None]\n"],
    )
    assert result.blocks[6] == Block(
        type=BlockType.CLASS,
        name="KlassWithMetaKlass",
        lines=["\n", "\n", "class KlassWithMetaKlass:\n", "    class Meta:\n", "        abstract = True\n"],
    )
    assert result.blocks[7] == Block(
        type=BlockType.CLASS,
        name="_KlassNameStartWithUnderScore",
        lines=["\n", "\n", "class _KlassNameStartWithUnderScore:\n", "    pass\n"],
    )
    assert result.blocks[8] == Block(
        type=BlockType.CLASS,
        name="KlassWithComment1",
        lines=[
            "\n",
            "\n",
            '"""\n',
            " - Do not delete this comment.\n",
            '"""\n',
            "\n",
            "\n",
            "class KlassWithComment1:\n",
            "    pass\n",
        ],
    )
    assert result.blocks[9] == Block(
        type=BlockType.CLASS,
        name="KlassWithComment2",
        lines=[
            "\n",
            "\n",
            "'''\n",
            '"""\n',
            " - Do not delete this comment.\n",
            "'''\n",
            "\n",
            "\n",
            "class KlassWithComment2:\n",
            "    pass\n",
        ],
    )
    assert result.blocks[10] == Block(
        type=BlockType.CLASS,
        name="KlassWithComment3",
        lines=[
            "\n",
            "\n",
            "# This is very important comment for KlassWithComment3\n",
            "# This is sample class\n",
            "class KlassWithComment3:\n",
            "    pass\n",
        ],
    )
    assert result.blocks[11] == Block(
        type=BlockType.CLASS,
        name="KlassWithDecorator",
        lines=["\n", "\n", "@dataclass(frozen=True)\n", "class KlassWithDecorator:\n", "    pass\n"],
    )
    assert result.blocks[12] == Block(
        type=BlockType.CLASS,
        name="KlassWithCommentAndDecorator",
        lines=[
            "\n",
            "\n",
            '"""\n',
            "    class with comment and decorator\n",
            "from this import is dummy\n",
            "def this_is_comment():\n",
            "    pass\n",
            '"""\n',
            "\n",
            "\n",
            "@dataclass(frozen=True)\n",
            "class KlassWithCommentAndDecorator:\n",
            "    pass\n",
        ],
    )
    assert result.blocks[13] == Block(
        type=BlockType.VALUE, name="class_value1", lines=["\n", "\n", 'class_value1 = "default1"\n']
    )
    assert result.blocks[14] == Block(type=BlockType.VALUE, name="class_value2", lines=['class_value2 = "default2"\n'])
    assert result.blocks[15] == Block(
        type=BlockType.CLASS,
        name="KlassWithMember",
        lines=[
            "\n",
            "\n",
            "class KlassWithMember:\n",
            "    value: StrAlias\n",
            "    meta: KlassWithMetaKlass\n",
        ],
    )
    assert result.blocks[16] == Block(
        type=BlockType.CLASS,
        name="KlassWithFunction",
        lines=[
            "\n",
            "\n",
            "class KlassWithFunction(KlassWithComment1):\n",
            "    def hoge(self):\n",
            "        pass\n",
        ],
    )
    assert result.blocks[17] == Block(
        type=BlockType.FUNCTION,
        name="_function_start_with_underscore",
        lines=[
            "\n",
            "\n",
            'if __name__ == "__main__":\n',
            '    print("Hello, World!")\n',
            "    sys.exit(0)\n",
            "\n",
            "\n",
            "def _function_start_with_underscore(klass: KlassWithComment2):\n",
            "    print(klass)\n",
        ],
    )
    assert result.blocks[18] == Block(
        type=BlockType.FUNCTION,
        name="function_with_comment1",
        lines=[
            "\n",
            "\n",
            '"""\n',
            "- Do not delete this comment for function_with_comment1\n",
            '"""\n',
            "\n",
            "\n",
            "def function_with_comment1(path: Path):\n",
            "    pass\n",
        ],
    )
    assert result.blocks[19] == Block(
        type=BlockType.FUNCTION,
        name="function_with_comment2",
        lines=[
            "\n",
            "\n",
            "'''\n",
            '"""\n',
            "    - Do not delete this comment for function_with_comment2\n",
            "'''\n",
            "\n",
            "\n",
            "def function_with_comment2():\n",
            "    pass\n",
        ],
    )
    assert result.blocks[20] == Block(
        type=BlockType.FUNCTION,
        name="function_with_comment3",
        lines=[
            "\n",
            "\n",
            "# This is very important comment for function_with_comment3\n",
            "# This is sample class\n",
            "def function_with_comment3():\n",
            "    pass\n",
        ],
    )
    assert result.blocks[21] == Block(
        type=BlockType.FUNCTION,
        name="function_with_decorator",
        lines=["\n", "\n", "@staticmethod\n", "def function_with_decorator():\n", "    pass\n"],
    )
    assert result.blocks[22] == Block(type=BlockType.VALUE, name="def_value", lines=["\n", "\n", "def_value = 1\n"])
    assert result.blocks[23] == Block(
        type=BlockType.FUNCTION,
        name="function_with_comment_and_decorator",
        lines=[
            "\n",
            "\n",
            "# this comment for function_with_comment_and_decorator\n",
            "@staticmethod\n",
            "def function_with_comment_and_decorator():\n",
            "    pass\n",
        ],
    )
    assert result.blocks[24] == Block(
        type=BlockType.FUNCTION,
        name="function_with_async",
        lines=["\n", "\n", "async def function_with_async():\n", "    pass\n"],
    )
    assert result.blocks[25] == Block(type=BlockType.VALUE, name="last_value", lines=["\n", "\n", "last_value = 100\n"])


def test_load_file_service_non_existent_file():
    with pytest.raises(AssertionError):
        service = LoadFileService(file_path=Path("tests/non_existent_file.py"))
        service.execute()


def test_load_file_service_empty_file(tmp_path):
    empty_file = tmp_path / "empty.py"
    empty_file.touch()
    service = LoadFileService(file_path=empty_file)
    result = service.execute()
    assert len(result.blocks) == 0
