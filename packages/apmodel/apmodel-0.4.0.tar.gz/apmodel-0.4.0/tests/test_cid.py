import pytest
import datetime

from apmodel.loader import load
from apmodel.extra.cid.data_integrity_proof import DataIntegrityProof
from apmodel.extra.cid.multikey import Multikey
from cryptography.hazmat.primitives import serialization

# Test DataIntegrityProof
def test_data_integrity_proof_from_json():
    data = {
        "type": "DataIntegrityProof",
        "cryptosuite": "ed25519-sha256",
        "proofValue": "z42h",
        "proofPurpose": "assertionMethod",
        "verificationMethod": "did:example:123#key-1",
        "created": "2023-10-27T10:00:00Z"
    }
    proof = load(data)
    assert isinstance(proof, DataIntegrityProof)
    assert proof.type == "DataIntegrityProof"
    assert proof.cryptosuite == "ed25519-sha256"
    assert proof.proofValue == "z42h"
    assert proof.proofPurpose == "assertionMethod"
    assert proof.verificationMethod == "did:example:123#key-1"
    assert isinstance(proof.created, datetime.datetime)
    assert proof.created == datetime.datetime(2023, 10, 27, 10, 0, tzinfo=datetime.timezone.utc)

def test_data_integrity_proof_to_json():
    proof = DataIntegrityProof(
        cryptosuite="ed25519-sha256",
        proofValue="z42h",
        proofPurpose="assertionMethod",
        verificationMethod="did:example:123#key-1",
        created=datetime.datetime(2023, 10, 27, 10, 0, 0)
    )
    json_data = proof.to_json()
    assert json_data["type"] == "DataIntegrityProof"
    assert json_data["cryptosuite"] == "ed25519-sha256"
    assert json_data["proofValue"] == "z42h"
    assert json_data["proofPurpose"] == "assertionMethod"
    assert json_data["verificationMethod"] == "did:example:123#key-1"
    assert json_data["created"] == "2023-10-27T10:00:00Z"
    assert "@context" in json_data
    assert "https://w3id.org/security/data-integrity/v1" in json_data["@context"]

def test_data_integrity_proof_context_aggregation():
    proof = DataIntegrityProof(
        cryptosuite="ed25519-sha256",
        proofValue="z42h",
        proofPurpose="assertionMethod",
        verificationMethod="did:example:123#key-1",
        created=datetime.datetime(2023, 10, 27, 10, 0, 0)
    )
    json_data = proof.to_json()
    assert isinstance(json_data["@context"], list)
    assert "https://www.w3.org/ns/activitystreams" in json_data["@context"]
    assert "https://w3id.org/security/data-integrity/v1" in json_data["@context"]

# Test Multikey
# Note: Testing Multikey with actual cryptography objects is complex due to key generation/serialization.
# We'll focus on the to_json behavior with string representations that from_json would produce.
def test_multikey_from_json():
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from multiformats import multicodec, multibase

    ed_priv = ed25519.Ed25519PrivateKey.generate()

    data = {
        "type": "Multikey",
        "id": "did:example:123#key-1",
        "controller": "did:example:123",
        "publicKeyMultibase": multibase.encode(multicodec.wrap("ed25519-pub", ed_priv.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )), "base58btc"),
        "secretKeyMultibase": multibase.encode(multicodec.wrap("ed25519-priv", ed_priv.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw, 
        encryption_algorithm=serialization.NoEncryption()
    )), "base58btc")
    }
    multikey = load(data)
    assert isinstance(multikey, Multikey)
    assert multikey.type == "Multikey"
    assert multikey.id == "did:example:123#key-1"
    assert multikey.controller == "did:example:123"
    # We expect these to be converted to actual key objects by __post_init__
    assert not isinstance(multikey.publicKeyMultibase, str)
    assert not isinstance(multikey.secretKeyMultibase, str)

def test_multikey_to_json():
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from multiformats import multicodec, multibase

    ed_priv = ed25519.Ed25519PrivateKey.generate()
    pub_mb = multibase.encode(multicodec.wrap("ed25519-pub", ed_priv.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )), "base58btc")

    priv_mb = multibase.encode(multicodec.wrap("ed25519-priv", ed_priv.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw, 
        encryption_algorithm=serialization.NoEncryption()
    )), "base58btc")
    # Create a Multikey instance with string representations that would come from from_json
    # This avoids needing to generate actual cryptography key objects for testing to_json
    multikey = Multikey(
        id="did:example:123#key-1",
        controller="did:example:123",
        publicKeyMultibase=pub_mb,
        secretKeyMultibase=priv_mb
    )

    json_data = multikey.to_json()
    assert json_data["type"] == "Multikey"
    assert json_data["id"] == "did:example:123#key-1"
    assert json_data["controller"] == "did:example:123"
    assert json_data["publicKeyMultibase"] == pub_mb
    assert json_data["secretKeyMultibase"] == priv_mb
    assert "@context" not in json_data # Multikey does not add custom context by default