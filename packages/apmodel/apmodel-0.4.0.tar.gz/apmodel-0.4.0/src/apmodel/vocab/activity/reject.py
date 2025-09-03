from dataclasses import dataclass, field
from typing import Union

from ...types import Undefined
from ...core.activity import Activity

@dataclass
class Reject(Activity):
    type: Union[str, Undefined] = field(default="Reject")

@dataclass
class TentativeReject(Reject):
    type: Union[str, Undefined] = field(default="TentativeReject")
