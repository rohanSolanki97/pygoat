import pytest


# Assumption: tests run with project root on PYTHONPATH so `introduction` is importable.
from introduction import views


class _DummyUser:
    def __init__(self, authenticated=True):
        self.is_authenticated = authenticated


class _DummyRequest:
    def __init__(self, body: bytes, authenticated=True):
        self.user = _DummyUser(authenticated)
        self.body = body


def test_xxe_parse_disables_external_general_entities(monkeypatch):
    parser_instance = object()
    calls = {"setFeature": []}

    class _FakeParser:
        def setFeature(self, feature, value):
            calls["setFeature"].append((feature, value))

    def fake_make_parser():
        return _FakeParser()

    def fake_parse_string(xml_text, parser=None):
        # Ensure the parser object created by make_parser is passed through.
        assert isinstance(parser, _FakeParser)
        # Return an empty iterable so the function fails later; we only assert the security-relevant call.
        return []

    monkeypatch.setattr(views, "make_parser", fake_make_parser)
    monkeypatch.setattr(views, "parseString", fake_parse_string)

    req = _DummyRequest(body=b"<root><text>hello</text></root>")

    with pytest.raises(UnboundLocalError):
        views.xxe_parse(req)

    assert calls["setFeature"] == [(views.feature_external_ges, False)]
