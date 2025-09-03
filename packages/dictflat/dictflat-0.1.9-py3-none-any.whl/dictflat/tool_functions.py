
import re
from typing import Final
from uuid import uuid4

__RE_UPPER_LETTER: Final[re.Pattern[str]] = re.compile(r'(?<!^)(?=[A-Z])')
__RE_MULTIPLE_UNDERSCORE: Final[re.Pattern[str]] = re.compile(r'_+')


def str_2_snakecase(s: str) -> str:
    return __RE_MULTIPLE_UNDERSCORE.sub(
        '_',
        __RE_UPPER_LETTER.sub('_', s)
        .lower()
        .replace('._', '.')
    )


def get_uuid() -> str:
    return str(uuid4())
