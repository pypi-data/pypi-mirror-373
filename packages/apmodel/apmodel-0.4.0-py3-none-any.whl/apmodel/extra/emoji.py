from dataclasses import dataclass, field
from typing import Union

from ..core import Object
from ..types import Undefined

@dataclass
class Emoji(Object):
    type: Union[str, Undefined] = field(default="Emoji", kw_only=True)
    