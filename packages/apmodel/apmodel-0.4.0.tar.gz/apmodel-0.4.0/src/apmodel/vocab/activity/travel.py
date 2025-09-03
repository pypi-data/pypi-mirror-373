from dataclasses import dataclass, field
from typing import Union

from ...types import Undefined
from ...core.activity import IntransitiveActivity

@dataclass
class Travel(IntransitiveActivity):
    type: Union[str, Undefined] = field(default="Travel")
