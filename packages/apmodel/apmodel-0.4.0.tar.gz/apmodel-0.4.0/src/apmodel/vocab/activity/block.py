from dataclasses import dataclass, field
from typing import Union

from ...types import Undefined
from .ignore import Ignore

@dataclass
class Block(Ignore):
    type: Union[str, Undefined] = field(default="Block")
