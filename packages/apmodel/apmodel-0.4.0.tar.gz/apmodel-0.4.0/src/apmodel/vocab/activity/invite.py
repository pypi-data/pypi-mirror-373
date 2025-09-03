from dataclasses import dataclass, field
from typing import Union

from ...types import Undefined
from .offer import Offer

@dataclass
class Invite(Offer):
    type: Union[str, Undefined] = field(default="Invite")
