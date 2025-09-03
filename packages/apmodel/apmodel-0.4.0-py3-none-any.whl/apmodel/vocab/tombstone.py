import datetime
from dataclasses import dataclass, field
from typing import Union

from ..core.object import Object
from ..types import Undefined

@dataclass
class Tombstone(Object):
    type: Union[str, Undefined] = field(default="Tombstone")
    formerType: str | Object | Undefined = field(default_factory=Undefined)
    deleted: datetime.datetime | str | Undefined = field(default_factory=Undefined)

    def __post_init__(self):
        if isinstance(self.deleted, str):
            self.deleted = datetime.datetime.fromisoformat(self.deleted.replace("Z", "+00:00"))

    def to_json(self):
        data = super().to_json()
        
        # Handle deleted field serialization without modifying instance state
        if isinstance(self.deleted, datetime.datetime):
            data['deleted'] = self.deleted.isoformat(timespec='seconds').replace('+00:00', 'Z')
        # For other types (str, Undefined), super().to_json() should handle them correctly

        return data