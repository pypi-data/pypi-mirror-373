from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union, List

from .object import Object
from .link import Link
from ..types import Undefined

@dataclass
class Collection(Object):
    type: Union[str, Undefined] = field(default="Collection", kw_only=True)

    totalItems: Union[int, Undefined] = field(default_factory=Undefined)
    current: Union[str, dict, Link, Undefined] = field(default_factory=Undefined)
    first: Union[str, dict, Link, Undefined] = field(default_factory=Undefined)
    last: Union[str, dict, Link, Undefined] = field(default_factory=Undefined)
    items: Union[List[Union[Object, Link]], Undefined] = field(default_factory=Undefined)
    orderedItems: Union[List[Union[Object, Link]], Undefined] = field(default_factory=Undefined)

    def __post_init__(self):
        if isinstance(self.totalItems, int) and self.totalItems < 0:
            raise ValueError("totalItems must be non-negative integer.")

@dataclass
class CollectionPage(Collection):
    type: Union[str, Undefined] = field(default="CollectionPage", kw_only=True)

    partOf: Union[str, Collection, Link, Undefined] = field(default_factory=Undefined)

    next: Union[str, CollectionPage, Link, Undefined] = field(default_factory=Undefined)
    prev: Union[str, CollectionPage, Link, Undefined] = field(default_factory=Undefined)

@dataclass
class OrderedCollection(Collection):
    type: Union[str, Undefined] = field(default="OrderedCollection", kw_only=True)

@dataclass
class OrderedCollectionPage(CollectionPage):
    type: Union[str, Undefined] = field(default="OrderedCollectionPage", kw_only=True)

    startIndex: Union[int, Undefined] = field(default_factory=Undefined)
    
    def __post_init__(self):
        if isinstance(self.startIndex, int) and self.startIndex < 0:
            raise ValueError("startIndex must be non-negative integer.")