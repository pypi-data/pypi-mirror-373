from datetime import datetime
from dataclasses import field, dataclass
from typing import Union

from ...context import LDContext
from ...types import ActivityPubModel, Undefined
from ...dumper import _serialize_model_to_json # Import the helper


@dataclass
class DataIntegrityProof(ActivityPubModel):
    _context: LDContext = field(
        default_factory=lambda: LDContext(
            [
                "https://www.w3.org/ns/activitystreams",
                "https://w3id.org/security/data-integrity/v1",
            ]
        ),
        kw_only=True,
    )

    type: Union[str, Undefined] = field(default="DataIntegrityProof", kw_only=True)
    cryptosuite: str
    proofValue: str
    proofPurpose: str
    verificationMethod: str
    created: Union[str, datetime]
    _extra: dict = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.created, str):
            self.created = datetime.fromisoformat(self.created.replace('Z', '+00:00'))

    def to_json(self):
        data = _serialize_model_to_json(self) # Use the generic serializer

        # Apply DataIntegrityProof-specific serialization for 'created' field
        if "created" in data and isinstance(data["created"], datetime):
            time_formatted = data["created"].isoformat(timespec='seconds')
            if time_formatted.endswith('+00:00'):
                data["created"] = time_formatted.replace('+00:00', 'Z') # Convert datetime to ISO string with Z
            elif time_formatted.endswith('Z'):
                data["created"] = time_formatted
            else:
                data["created"] = time_formatted + "Z"

        return data
