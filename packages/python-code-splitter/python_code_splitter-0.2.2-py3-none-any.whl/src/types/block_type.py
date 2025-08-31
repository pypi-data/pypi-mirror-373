import enum


class BlockType(enum.Enum):
    IMPORT = "import"
    FUNCTION = "function"
    CLASS = "class"
    VALUE = "value"
    COMMENT = "comment"
    OTHER = "other"
