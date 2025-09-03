from dataclasses import field, dataclass
from typing import Union

from cryptography.hazmat.primitives.asymmetric import ed25519, rsa
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidKey
from multiformats import multicodec, multibase

from ...exceptions import InvalidField
from ...types import ActivityPubModel, Undefined
from ...dumper import _serialize_model_to_json # Import the helper

@dataclass
class Multikey(ActivityPubModel):
    type: Union[str, Undefined] = field(default="Multikey", kw_only=True)

    id: str
    controller: str
    publicKeyMultibase: Union[ed25519.Ed25519PublicKey | rsa.RSAPublicKey, str, Undefined] = field(default_factory=Undefined)
    secretKeyMultibase: Union[ed25519.Ed25519PrivateKey | rsa.RSAPrivateKey, str, Undefined] = field(default_factory=Undefined)
    
    _extra: dict = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.publicKeyMultibase, str):
            decoded = multibase.decode(self.publicKeyMultibase)
            codec, data = multicodec.unwrap(decoded)
            if codec.name == "ed25519-pub":
                try:
                    pub_key = ed25519.Ed25519PublicKey.from_public_bytes(data)
                    if isinstance(pub_key, ed25519.Ed25519PublicKey):
                        self.publicKeyMultibase = pub_key
                    else:
                        raise ValueError("Unsupported Key: {}".format(type(pub_key)))
                except InvalidKey:
                    raise InvalidField("Invalid ed25519 public key passed.")
            elif codec.name == "rsa-pub":
                try:
                    pub_key = serialization.load_der_public_key(data)
                    if isinstance(pub_key, rsa.RSAPublicKey):
                        self.publicKeyMultibase = pub_key
                    else:
                        raise ValueError("Unsupported Key: {}".format(type(pub_key)))
                except ValueError:
                    raise InvalidField("Invalid rsa public key passed.")
            else:
                raise ValueError("Unsupported Codec: {}".format(codec.name))
        if isinstance(self.secretKeyMultibase, str):
            decoded = multibase.decode(self.secretKeyMultibase)
            codec, data = multicodec.unwrap(decoded)
            if codec.name == "ed25519-priv":
                try:
                    priv_key = ed25519.Ed25519PrivateKey.from_private_bytes(data)
                    if isinstance(priv_key, ed25519.Ed25519PrivateKey):
                        self.secretKeyMultibase = priv_key
                    else:
                        raise ValueError("Unsupported Key: {}".format(type(priv_key)))
                except InvalidKey:
                    raise InvalidField("Invalid ed25519 public key passed.")
            elif codec.name == "rsa-priv":
                try:
                    priv_key = serialization.load_der_private_key(data, password=None)
                    if isinstance(priv_key, rsa.RSAPrivateKey):
                        self.secretKeyMultibase = priv_key
                    else:
                        raise ValueError("Unsupported Key: {}".format(type(priv_key)))
                except ValueError:
                    raise InvalidField("Invalid rsa public key passed.")
            else:
                raise ValueError("Unsupported Codec: {}".format(codec.name))

    def to_json(self):
        data = _serialize_model_to_json(self)

        # Apply Multikey-specific serialization for key objects
        for key in ["publicKeyMultibase", "secretKeyMultibase"]:
            value = data.get(key)
            if isinstance(value, rsa.RSAPrivateKey):
                wrapped = multicodec.wrap("rsa-priv", value.private_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
                data[key] = multibase.encode(wrapped, "base58btc")
            elif isinstance(value, ed25519.Ed25519PrivateKey):
                wrapped = multicodec.wrap("ed25519-priv", value.private_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PrivateFormat.Raw,
                    encryption_algorithm=serialization.NoEncryption()
                ))
                data[key] = multibase.encode(wrapped, "base58btc")
            elif isinstance(value, rsa.RSAPublicKey):
                wrapped = multicodec.wrap("rsa-pub", value.public_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PublicFormat.PKCS1
                ))
                data[key] = multibase.encode(wrapped, "base58btc")
            elif isinstance(value, ed25519.Ed25519PublicKey):
                wrapped = multicodec.wrap("ed25519-pub", value.public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw
                ))
                data[key] = multibase.encode(wrapped, "base58btc")
        return data