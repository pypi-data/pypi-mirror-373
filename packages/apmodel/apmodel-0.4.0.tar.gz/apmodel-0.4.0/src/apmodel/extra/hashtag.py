from dataclasses import dataclass, field
from typing import Union

from ..core.link import Link
from ..types import Undefined

@dataclass
class Hashtag(Link):
    type: Union[str, Undefined] = field(default="Hashtag", kw_only=True)
