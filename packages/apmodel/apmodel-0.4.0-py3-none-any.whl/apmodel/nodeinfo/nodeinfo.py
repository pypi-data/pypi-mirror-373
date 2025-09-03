from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import List, Literal
import re
import json

from ..types import ActivityPubModel, Undefined
from ..exceptions import MissingField, InvalidField

class NodeinfoProtocol(Enum):
    ACTIVITYPUB = "activitypub"
    BUDDYCLOUD = "buddycloud"
    DFRN = "dfrn"
    DIASPORA = "diaspora"
    LIBERTREE = "libertree"
    OSTATUS = "ostatus"
    PUMPIO = "pumpio"
    TENT = "tent"
    XMPP = "xmpp"
    ZOT = "zot"

class NodeinfoInbound(Enum):
    ATOM1_0 = "atom1.0"
    GNUSOCIAL = "gnusocial"
    IMAP = "imap"
    PNUT = "pnut"
    POP3 = "pop3"
    PUMPIO = "pumpio"
    RSS2_0 = "rss2.0"
    TWITTER = "twitter"

class NodeinfoOutbound(Enum):
    ATOM1_0 = "atom1.0"
    GNUSOCIAL = "gnusocial"
    BLOGGER = "blogger"
    DIASPORA = "diaspora"
    BUDDYCLOUD = "buddycloud"
    DREAMWIDTH = "dreamwidth"
    DRUPAL = "drupal"
    FACEBOOK = "facebook"
    FRIENDICA = "friendica"
    GOOGLE = "google"
    INSANEJOURNAL = "insanejournal"
    LIBERTREE = "libertree"
    LINKEDIN = "linkedin"
    LIVEJOURNAL = "livejournal"
    MEDIAGOBLIN = "mediagoblin"
    MYSPACE = "myspace"
    PINTEREST = "pinterest"
    PNUT = "pnut"
    POSTEROUS = "posterous"
    PUMPIO = "pumpio"
    REDMATRIX = "redmatrix"
    RSS2_0 = "rss2.0"
    SMTP = "smtp"
    TENT = "tent"
    TUMBLR = "tumblr"
    TWITTER = "twitter"
    WORDPRESS = "wordpress"
    XMPP = "xmpp"

@dataclass
class NodeinfoServices(ActivityPubModel):
    inbound: List[NodeinfoInbound | str] = field(kw_only=True)
    outbound: List[NodeinfoOutbound | str] = field(kw_only=True)

    @classmethod
    def from_json(cls, data: dict) -> "NodeinfoServices":
        inbound = [
            NodeinfoInbound(i) if isinstance(i, str) and i in [e.value for e in NodeinfoInbound] else i
            for i in data.get("inbound", [])
        ]
        outbound = [
            NodeinfoOutbound(o) if isinstance(o, str) and o in [e.value for e in NodeinfoOutbound] else o
            for o in data.get("outbound", [])
        ]
        return cls(
            inbound=inbound,
            outbound=outbound,
        )

    def to_json(self) -> dict:
        return {
            "inbound": [item.value if isinstance(item, Enum) else item for item in self.inbound],
            "outbound": [item.value if isinstance(item, Enum) else item for item in self.outbound],
        }

@dataclass
class NodeinfoUsageUsers(ActivityPubModel):
    total: int | Undefined = field(default_factory=Undefined)
    activeHalfyear: int | Undefined = field(default_factory=Undefined)
    activeMonth: int | Undefined = field(default_factory=Undefined)

    @classmethod
    def from_json(cls, data: dict) -> "NodeinfoUsageUsers":
        return cls(
            total=data.get("total", Undefined()),
            activeHalfyear=data.get("activeHalfyear", Undefined()),
            activeMonth=data.get("activeMonth", Undefined()),
        )

    def to_json(self) -> dict:
        data = asdict(self)
        return {k: v for k, v in data.items() if not isinstance(v, Undefined)}

@dataclass
class NodeinfoUsage(ActivityPubModel):
    users: NodeinfoUsageUsers
    localPosts: int | Undefined = field(default_factory=Undefined)
    localComments: int | Undefined = field(default_factory=Undefined)

    @classmethod
    def from_json(cls, data: dict) -> "NodeinfoUsage":
        users = NodeinfoUsageUsers.from_json(data.get("users", {}))
        return cls(
            users=users,
            localPosts=data.get("localPosts", Undefined()),
            localComments=data.get("localComments", Undefined()),
        )

    def to_json(self) -> dict:
        data = {
            "users": self.users.to_json(),
            "localPosts": self.localPosts,
            "localComments": self.localComments,
        }
        return {k: v for k, v in data.items() if not isinstance(v, Undefined)}

@dataclass
class NodeinfoSoftware(ActivityPubModel):
    name: str | Undefined = field(default_factory=Undefined)
    version: str | Undefined = field(default_factory=Undefined)
    repository: str | Undefined = field(default_factory=Undefined)
    homepage: str | Undefined = field(default_factory=Undefined)

    def __post_init__(self):
        if isinstance(self.name, Undefined):
            raise MissingField("The value of software.name is required but undefined")
        elif isinstance(self.version, Undefined):
            raise MissingField("The value of software.version is required but undefined")
        else:
            if not re.match(r"^[a-z0-9-]+$", self.name):
                raise InvalidField("The value of software.name is invalid")

    @classmethod
    def from_json(cls, data: dict) -> "NodeinfoSoftware":
        return cls(
            name=data.get("name", Undefined()),
            version=data.get("version", Undefined()),
            repository=data.get("repository", Undefined()),
            homepage=data.get("homepage", Undefined()),
        )

    def to_json(self) -> dict:
        data = asdict(self)
        return {k: v for k, v in data.items() if not isinstance(v, Undefined)}

@dataclass
class Nodeinfo(ActivityPubModel):
    version: Literal["2.0", "2.1"]
    software: NodeinfoSoftware
    protocols: List[NodeinfoProtocol | str]
    services: NodeinfoServices
    openRegistrations: bool
    usage: NodeinfoUsage
    metadata: dict


    _DETECTION_KEYS = ["version", "software", "protocols", "services", "openRegistrations", "usage", "metadata"]

    @classmethod
    def is_nodeinfo_data(cls, data: dict) -> bool:
        """Checks if the given dictionary data matches Nodeinfo detection criteria."""
        return all(key in data for key in cls._DETECTION_KEYS)

    def __post_init__(self):
        if self.version == "2.0": # Not defined software.homepage and software.repository in 2.0
            self.software.homepage = Undefined()
            self.software.repository = Undefined()

    @classmethod
    def from_json(cls, data: dict) -> "Nodeinfo":
        if isinstance(data, str):
            data = json.loads(data)

        software_instance = NodeinfoSoftware.from_json(data.get('software', {}))
        services_instance = NodeinfoServices.from_json(data.get('services', {}))
        usage_instance = NodeinfoUsage.from_json(data.get('usage', {}))

        protocols_list = [
            NodeinfoProtocol(p) if isinstance(p, str) and p in [e.value for e in NodeinfoProtocol] else p
            for p in data.get('protocols', [])
        ]

        return cls(
            version=data['version'],
            software=software_instance,
            protocols=protocols_list,
            services=services_instance,
            openRegistrations=data['openRegistrations'],
            usage=usage_instance,
            metadata=data.get('metadata', {})
        )
    
    def to_json(self) -> dict:
        data = {
            "version": self.version,
            "software": self.software.to_json(),
            "protocols": [p.value if isinstance(p, Enum) else p for p in self.protocols],
            "services": self.services.to_json(),
            "openRegistrations": self.openRegistrations,
            "usage": self.usage.to_json(),
            "metadata": self.metadata,
        }
        return {k: v for k, v in data.items() if not isinstance(v, Undefined)}
