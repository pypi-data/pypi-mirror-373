# This is a sample file for testing.
"""
This is a sample file for testing.
"""

import sys
from dataclasses import dataclass
from typing import (
    Callable
)
from pathlib import Path

StrAlias = str
# This is very important value
FunctionAlias = Callable[[], None]


class KlassWithMetaKlass:
    class Meta:
        abstract = True


class _KlassNameStartWithUnderScore:
    pass


"""
 - Do not delete this comment.
"""


class KlassWithComment1:
    pass


'''
"""
 - Do not delete this comment.
'''


class KlassWithComment2:
    pass


# This is very important comment for KlassWithComment3
# This is sample class
class KlassWithComment3:
    pass


@dataclass(frozen=True)
class KlassWithDecorator:
    pass


"""
    class with comment and decorator
from this import is dummy
def this_is_comment():
    pass
"""


@dataclass(frozen=True)
class KlassWithCommentAndDecorator:
    pass


class_value1 = "default1"
class_value2 = "default2"


class KlassWithMember:
    value: StrAlias
    meta: KlassWithMetaKlass


class KlassWithFunction(KlassWithComment1):
    def hoge(self):
        pass


if __name__ == "__main__":
    print("Hello, World!")
    sys.exit(0)


def _function_start_with_underscore(klass: KlassWithComment2):
    print(klass)


"""
- Do not delete this comment for function_with_comment1
"""


def function_with_comment1(path: Path):
    pass


'''
"""
    - Do not delete this comment for function_with_comment2
'''


def function_with_comment2():
    pass


# This is very important comment for function_with_comment3
# This is sample class
def function_with_comment3():
    pass


@staticmethod
def function_with_decorator():
    pass


def_value = 1


# this comment for function_with_comment_and_decorator
@staticmethod
def function_with_comment_and_decorator():
    pass


async def function_with_async():
    pass


last_value = 100
