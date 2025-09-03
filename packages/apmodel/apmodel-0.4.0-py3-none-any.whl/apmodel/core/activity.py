from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Union

from ..types import Undefined
from ..vocab.actor import Actor
from .object import Object
from ..context import LDContext

if TYPE_CHECKING:
    from ..vocab.activity.accept import Accept
    from ..vocab.activity.reject import Reject
    from ..vocab.actor import Actor


@dataclass
class Activity(Object):
    type: Union[str, Undefined] = field(default="Activity", kw_only=True)
    actor: Union[str, "Actor", List[Union[str, "Actor"]], Undefined] = field(
        default_factory=Undefined
    )
    object: Union[Object, Undefined] = field(default_factory=Undefined)
    target: Union[str, "Actor", List[Union[str, "Actor"]], Undefined] = field(
        default_factory=Undefined
    )
    result: Union[dict, Undefined] = field(default_factory=Undefined)
    origin: Union[dict, Undefined] = field(default_factory=Undefined)
    instrument: Union[dict, Undefined] = field(default_factory=Undefined)

    def accept(self, id: str, actor: Actor) -> "Accept":
        from ..vocab.activity.accept import Accept

        return Accept(id=id, object=self, actor=actor)

    def reject(self, id: str, actor: Actor) -> "Reject":
        from ..vocab.activity.reject import Reject

        return Reject(id=id, object=self, actor=actor)

    

@dataclass
class IntransitiveActivity(Activity):
    type: Union[str, Undefined] = field(default="IntransitiveActivity", kw_only=True)

    def accept(self, id: str, actor: Actor) -> "Accept":
        from ..vocab.activity.accept import Accept

        return Accept(id=id, object=self, actor=actor)

    def reject(self, id: str, actor: Actor) -> "Reject":
        from ..vocab.activity.reject import Reject

        return Reject(id=id, object=self, actor=actor)
