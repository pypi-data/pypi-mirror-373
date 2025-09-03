from dataclasses import dataclass, field
from typing import Union

from ...types import Undefined, ActivityPubModel

@dataclass
class PropertyValue(ActivityPubModel):
    type: Union[str, Undefined] = field(default="PropertyValue", kw_only=True)

    name: Union[str, Undefined] = field(default_factory=Undefined)
    value: Union[str, Undefined] = field(default_factory=Undefined)

    _extra: dict = field(default_factory=dict)