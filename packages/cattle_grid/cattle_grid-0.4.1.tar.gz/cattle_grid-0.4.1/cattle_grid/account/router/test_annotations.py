from .annotations import name_from_routing_key


def test_accountname_from_routing_key():
    assert "alice" == name_from_routing_key("send.alice")
