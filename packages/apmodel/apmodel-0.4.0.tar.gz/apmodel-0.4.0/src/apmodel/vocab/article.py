from dataclasses import dataclass, field
from typing import Union
from ..types import Undefined
from ..core.object import Object

@dataclass
class Article(Object):
    type: Union[str, Undefined] = field(default="Article")
