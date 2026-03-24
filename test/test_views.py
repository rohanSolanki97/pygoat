from types import SimpleNamespace

import pytest


# Assumption: tests run with repository root on PYTHONPATH so `introduction` is importable.


def test_xxe_parse_disables_external_general_entities(monkeypatch):
    """Regression test for XXE fix: ensure external general entities are disabled."""
    from introduction import views

    class FakeParser:
        def __init__(self):
            self.features = []

        def setFeature(self, feature, value):
            self.features.append((feature, value))

    fake_parser = FakeParser()

    # make_parser() should return our fake parser
    monkeypatch.setattr(views, "make_parser", lambda: fake_parser)

    # parseString should be called with parser=fake_parser and return an iterable of events
    class FakeNode:
        tagName = "text"

        def toxml(self):
            return "<text>hello</text>"

    def fake_parse_string(_xml, parser=None):
        assert parser is fake_parser
        return [(views.START_ELEMENT, FakeNode())]

    monkeypatch.setattr(views, "parseString", fake_parse_string)

    # comments.objects.filter(id=1).update(comment=text) should be invoked
    class FakeFilter:
        def __init__(self):
            self.updated = None

        def update(self, comment):
            self.updated = comment
            return 1

    fake_filter = FakeFilter()

    class FakeCommentsObjects:
        def filter(self, id):
            assert id == 1
            return fake_filter

    monkeypatch.setattr(views, "comments", SimpleNamespace(objects=FakeCommentsObjects()))

    # render() can return any sentinel
    sentinel = object()
    monkeypatch.setattr(views, "render", lambda request, template_name: sentinel)

    request = SimpleNamespace(user=SimpleNamespace(is_authenticated=True), body=b"<text>hello</text>")

    result = views.xxe_parse(request)

    assert (views.feature_external_ges, False) in fake_parser.features
    assert fake_filter.updated == "hello"
    assert result is sentinel
