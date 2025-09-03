import json
from pathlib import Path
from apmodel.nodeinfo.nodeinfo import Nodeinfo, NodeinfoProtocol, NodeinfoOutbound
from apmodel.types import Undefined

def test_nodeinfo_2_0():
    path = Path(__file__).parent / "data" / "nodeinfo_sample_2.0.json"
    with open(path) as f:
        data = json.load(f)
    
    nodeinfo = Nodeinfo.from_json(data)

    assert nodeinfo.version == "2.0"
    assert nodeinfo.software.name == "foofedi"
    assert nodeinfo.software.version == "2025.8.27"
    assert isinstance(nodeinfo.software.homepage, Undefined)
    assert nodeinfo.protocols[0] == NodeinfoProtocol.ACTIVITYPUB
    assert NodeinfoOutbound.ATOM1_0 in nodeinfo.services.outbound
    assert nodeinfo.openRegistrations is False
    assert nodeinfo.usage.users.total == 4
    assert nodeinfo.metadata["nodeName"] == "FooFedi TEST"

def test_nodeinfo_2_1():
    path = Path(__file__).parent / "data" / "nodeinfo_sample_2.1.json"
    with open(path) as f:
        data = json.load(f)
    
    nodeinfo = Nodeinfo.from_json(data)

    assert nodeinfo.version == "2.1"
    assert nodeinfo.software.name == "foofedi"
    assert nodeinfo.software.version == "2025.8.27"
    assert nodeinfo.software.homepage == "https://foofedi.example.com/"
    assert nodeinfo.software.repository == "https://git.example.com/foofedi/foofedi"
    assert nodeinfo.protocols[0] == NodeinfoProtocol.ACTIVITYPUB
    assert NodeinfoOutbound.ATOM1_0 in nodeinfo.services.outbound
    assert nodeinfo.openRegistrations is False
    assert nodeinfo.usage.users.total == 4
    assert nodeinfo.metadata["nodeName"] == "FooFedi TEST"