from dataclasses import dataclass, field
from typing import Union

from ...types import Undefined
from ...core.activity import Activity

@dataclass
class Listen(Activity):
    type: Union[str, Undefined] = field(default="Listen")
