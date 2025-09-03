from dataclasses import dataclass, field
from typing import Union

from ..types import Undefined
from ..core.object import Object

@dataclass
class Document(Object):
    type: Union[str, Undefined] = field(default="Document")

@dataclass
class Audio(Document):
    type: Union[str, Undefined] = field(default="Audio")

@dataclass
class Image(Document):
    type: Union[str, Undefined] = field(default="Image")

@dataclass
class Video(Document):
    type: Union[str, Undefined] = field(default="Video")

@dataclass
class Page(Document):
    type: Union[str, Undefined] = field(default="Page")