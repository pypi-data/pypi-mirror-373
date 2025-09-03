from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union, TYPE_CHECKING, TypeVar

from ..context import LDContext
from ..types import Undefined, ActivityPubModel
from ..dumper import _serialize_model_to_json

if TYPE_CHECKING:
    from .object import Object

T = TypeVar("T", bound="Link")

@dataclass
class Link(ActivityPubModel):
    _context: LDContext = field(default_factory=lambda: LDContext(["https://www.w3.org/ns/activitystreams"]), kw_only=True)

    type: Union[str, Undefined] = field(default="Link", kw_only=True)
    id: Union[str, "Object", Link, Undefined] = field(default_factory=Undefined, kw_only=True)
    name: Union[str, Undefined] = field(default_factory=Undefined, kw_only=True)
    href: Union[str, Undefined] = field(default_factory=Undefined)
    hreflang: Union[str, Undefined] = field(default_factory=Undefined)
    mediaType: Union[str, Undefined] = field(default_factory=Undefined)
    
    _extra: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.type is Undefined:
            self.type = self.__class__.__name__

    def to_json(self):
        return _serialize_model_to_json(self)