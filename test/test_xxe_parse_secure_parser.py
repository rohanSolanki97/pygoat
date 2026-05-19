import pytest


# Assumptions: introduction.views is importable; pytest is available.
# This tests the security fix: external general entities are disabled.

def test_xxe_parse_disables_external_general_entities(monkeypatch):
    import introduction.views as views

    # Spy parser capturing setFeature calls
    class DummyParser:
        def __init__(self):
            self.features = []

        def setFeature(self, feature, value):
            self.features.append((feature, value))

    dummy_parser = DummyParser()

    # Patch make_parser to return our dummy
    monkeypatch.setattr(views, "make_parser", lambda: dummy_parser)

    # Make parseString return an iterable doc to avoid real XML parsing
    def fake_parse_string(xml_text, parser=None):
        assert parser is dummy_parser
        return []  # no events

    monkeypatch.setattr(views, "parseString", fake_parse_string)

    # Minimal request object with authenticated user and body
    class DummyUser:
        is_authenticated = True

    class DummyRequest:
        user = DummyUser()
        body = b"<root/>"

    # Act
    views.xxe_parse(DummyRequest())

    # Assert: external general entities are explicitly disabled
    assert (views.feature_external_ges, False) in dummy_parser.features
