from dataclasses import dataclass, field
from typing import Union

from ...types import Undefined
from ...core.activity import Activity

@dataclass
class Accept(Activity):
    type: Union[str, Undefined] = field(default="Accept")

@dataclass
class TentativeAccept(Accept):
    type: Union[str, Undefined] = field(default="TentativeAccept")