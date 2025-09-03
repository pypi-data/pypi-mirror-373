from dataclasses import dataclass, field
from typing import List, Union

from ..context import LDContext
from ..types import Undefined
from ..core.collection import Collection, OrderedCollection
from ..core.object import Object
from ..extra.schema.propertyvalue import PropertyValue
from ..extra.emoji import Emoji
from ..extra.hashtag import Hashtag

@dataclass
class ActorEndpoints(Object):
    type: Union[str, Undefined] = field(default="as:Endpoints")
    sharedInbox: Union[str, OrderedCollection, Undefined] = field(
        default_factory=Undefined
    )


@dataclass
class Actor(Object):
    inbox: Union[str, OrderedCollection, Undefined] = field(default_factory=Undefined)
    outbox: Union[str, OrderedCollection, Undefined] = field(default_factory=Undefined)
    followers: Union[str, OrderedCollection, Collection, Undefined] = field(
        default_factory=Undefined
    )
    following: Union[str, OrderedCollection, Collection, Undefined] = field(
        default_factory=Undefined
    )
    liked: Union[str, OrderedCollection, Collection, Undefined] = field(
        default_factory=Undefined
    )
    streams: Union[str, Collection, Undefined] = field(default_factory=Undefined)
    preferredUsername: Union[str, Undefined] = field(default_factory=Undefined)
    endpoints: Union[ActorEndpoints, Undefined] = field(default_factory=Undefined)
    discoverable: Union[bool, Undefined] = field(default_factory=Undefined)
    indexable: Union[bool, Undefined] = field(default_factory=Undefined)
    suspended: Union[bool, Undefined] = field(default_factory=Undefined)
    memorial: Union[bool, Undefined] = field(default_factory=Undefined)

    def to_json(self):
        result = super().to_json()

        # Create a new LDContext instance based on the context already in result
        # This ensures we don't modify self._context directly
        dynamic_context = LDContext(result.get("@context", []))

        # Add Actor-specific contexts based on properties
        if result.get("publicKey"):
            dynamic_context.add("https://w3id.org/security/v1")
        if result.get("manuallyApprovesFollowers"):
            dynamic_context.add({"manuallyApprovesFollowers": "as:manuallyApprovesFollowers"})
        if result.get("sensitive"):
            dynamic_context.add({"sensitive": "as:sensitive"})
        if result.get("featured"):
            dynamic_context.add({"toot": "http://joinmastodon.org/ns#", "featured": "toot:featured"})
        if result.get("featuredTags"):
            dynamic_context.add({"toot": "http://joinmastodon.org/ns#", "featured": "toot:featuredTags"})
        if result.get("indexable"):
            dynamic_context.add({"toot": "http://joinmastodon.org/ns#", "indexable": "toot:indexable"})
        if result.get("discoverable"):
            dynamic_context.add({"toot": "http://joinmastodon.org/ns#", "discoverable": "toot:discoverable"})
        if result.get("suspended"):
            dynamic_context.add({"toot": "http://joinmastodon.org/ns#", "suspended": "toot:suspended"})
        if result.get("memorial"):
            dynamic_context.add({"toot": "http://joinmastodon.org/ns#", "memorial": "toot:memorial"})
        
        # Check for specific types within attachment and tag lists
        # Note: This assumes PropertyValue, Emoji, Hashtag are ActivityPubModel instances
        # and their to_json methods would have been called by super().to_json()
        # We are checking the *serialized* result here.
        if any(isinstance(item, dict) and item.get("type") == "PropertyValue" for item in result.get("attachment", [])):
            dynamic_context.add({"schema": "http://schema.org#", "value": "schema:value", "PropertyValue": "schema:PropertyValue"})
        if any(isinstance(item, dict) and item.get("type") == "Emoji" for item in result.get("tag", [])):
            dynamic_context.add({"toot": "http://joinmastodon.org/ns#", "Emoji": "toot:Emoji"})
        if any(isinstance(item, dict) and item.get("type") == "Hashtag" for item in result.get("tag", [])):
            dynamic_context.add({"Hashtag": "https://www.w3.org/ns/activitystreams#Hashtag"})

        # Update the @context in the result dictionary
        result["@context"] = dynamic_context.full_context

        return result


@dataclass
class Application(Actor):
    type: Union[str, Undefined] = field(default="Application")


@dataclass
class Group(Actor):
    type: Union[str, Undefined] = field(default="Group")


@dataclass
class Organization(Actor):
    type: Union[str, Undefined] = field(default="Organization")


@dataclass
class Person(Actor):
    type: Union[str, Undefined] = field(default="Person")


@dataclass
class Service(Actor):
    type: Union[str, Undefined] = field(default="Service")
