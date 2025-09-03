from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Union, TypeVar, TYPE_CHECKING

from ..context import LDContext
from ..types import ActivityPubModel, Undefined
from ..dumper import _serialize_model_to_json

if TYPE_CHECKING:
    from .link import Link
    from .collection import Collection
    from ..vocab.actor import Actor
    from ..vocab.document import Image
    from ..extra.schema import PropertyValue

T = TypeVar("T", bound="Object")

@dataclass
class Object(ActivityPubModel):
    _context: LDContext = field(default_factory=lambda: LDContext(["https://www.w3.org/ns/activitystreams"]), kw_only=True)
    id: Union[str, Undefined] = field(default_factory=Undefined)
    type: Union[str, Undefined] = field(default="Object", kw_only=True)
    name: Union[str, Undefined] = field(default_factory=Undefined)
    content: Union[str, Undefined] = field(default_factory=Undefined)
    summary: Union[str, Undefined] = field(default_factory=Undefined)
    url: Union[str, "Link", Undefined] = field(default_factory=Undefined)
    published: Union[str, Undefined] = field(default_factory=Undefined)
    updated: Union[str, Undefined] = field(default_factory=Undefined)
    attributedTo: Union[str, "Actor", List[Union[str, "Actor"]], Undefined] = field(default_factory=Undefined)
    audience: Union[str, "Object", List[Union[str, "Object"]], Undefined] = field(default_factory=Undefined)
    to: Union[str, "Object", List[Union[str, "Object"]], Undefined] = field(default_factory=Undefined)
    bto: Union[str, "Object", List[Union[str, "Object"]], Undefined] = field(default_factory=Undefined)
    cc: Union[str, "Object", List[Union[str, "Object"]], Undefined] = field(default_factory=Undefined)
    bcc: Union[str, "Object", List[Union[str, "Object"]], Undefined] = field(default_factory=Undefined)
    generator: Union["Object", Undefined] = field(default_factory=Undefined)
    icon: Union["Image", Undefined] = field(default_factory=Undefined)
    image: Union["Image", Undefined] = field(default_factory=Undefined)
    inReplyTo: Union["Object", Undefined] = field(default_factory=Undefined)
    location: Union["Object", Undefined] = field(default_factory=Undefined)
    preview: Union["Object", Undefined] = field(default_factory=Undefined)
    replies: Union["Collection", Undefined] = field(default_factory=Undefined)
    scope: Union["Object", Undefined] = field(default_factory=Undefined)
    tag: List["Object"] = field(default_factory=list)
    attachment: List[Union["Object", "PropertyValue"]] = field(default_factory=list)
    _extra: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.type is Undefined:
            self.type = self.__class__.__name__

    def to_json(self):
        return _serialize_model_to_json(self)