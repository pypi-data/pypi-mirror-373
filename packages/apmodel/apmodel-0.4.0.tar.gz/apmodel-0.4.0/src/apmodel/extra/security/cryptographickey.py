from dataclasses import dataclass, field
from typing import Union

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from ...types import Undefined, ActivityPubModel

@dataclass
class CryptographicKey(ActivityPubModel):
    type: Union[str, Undefined] = field(default="CryptographicKey", kw_only=True)

    id: Union[str, Undefined] = field(default_factory=Undefined)
    owner: Union[str, Undefined] = field(default_factory=Undefined)
    publicKeyPem: Union[rsa.RSAPublicKey, str, bytes, Undefined] = field(default_factory=Undefined)

    _extra: dict = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.publicKeyPem, Undefined) and not isinstance(self.publicKeyPem, rsa.RSAPublicKey):
            pub_key = serialization.load_pem_public_key(self.publicKeyPem.encode("utf-8") if isinstance(self.publicKeyPem, str) else self.publicKeyPem)
            if isinstance(pub_key, rsa.RSAPublicKey):
                self.publicKeyPem = pub_key
            else:
                raise ValueError("Unsupported Key: {}".format(type(pub_key)))