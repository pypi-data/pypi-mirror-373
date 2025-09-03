from dataclasses import dataclass, field
from typing import Union

from ...types import Undefined
from ...core.activity import IntransitiveActivity

@dataclass
class Arrive(IntransitiveActivity):
    type: Union[str, Undefined] = field(default="Arrive")
