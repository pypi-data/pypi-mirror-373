from dataclasses import field
from typing import Union

from ..types import Undefined
from ..core.link import Link

class Mention(Link):
    type: Union[str, Undefined] = field(default="Mention")