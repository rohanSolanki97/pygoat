import types

import pytest

# Assumption: tests run with project root on PYTHONPATH so `introduction` is importable.
from introduction import views


def _make_request(body: bytes, authenticated: bool = True):
    user = types.SimpleNamespace(is_authenticated=authenticated)
    req = types.SimpleNamespace()
    req.user = user
    req.body = body
    return req


def test_xxe_parse_disables_external_general_entities(monkeypatch):
    captured = {}

    class _FakeParser:
        def setFeature(self, feature, value):
            captured["feature"] = feature
            captured["value"] = value

    def fake_make_parser():
        return _FakeParser()

    def fake_parse_string(xml, parser=None):
        # Return an iterable with a single START_ELEMENT 'text' node.
        node = types.SimpleNamespace(tagName="text", toxml=lambda: "<text>hello</text>")
        doc = types.SimpleNamespace(expandNode=lambda n: None)
        return [(views.START_ELEMENT, node)]

    class _Filter:
        def update(self, **kwargs):
            captured["updated"] = kwargs
            return 1

    monkeypatch.setattr(views, "make_parser", fake_make_parser)
    monkeypatch.setattr(views, "parseString", fake_parse_string)
    monkeypatch.setattr(views.comments.objects, "filter", lambda **kwargs: _Filter())
    monkeypatch.setattr(views, "render", lambda request, template: {"template": template})

    req = _make_request(b"<root><text>hello</text></root>")
    resp = views.xxe_parse(req)

    assert captured["feature"] == views.feature_external_ges
    assert captured["value"] is False
    assert captured["updated"] == {"comment": "hello"}
    assert resp["template"] == "Lab/XXE/xxe_lab.html"
