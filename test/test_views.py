import types

import pytest


def _make_request(*, user_authenticated=True, body=b""):
    user = types.SimpleNamespace(is_authenticated=user_authenticated)
    return types.SimpleNamespace(method="POST", user=user, body=body)


def test_xxe_parse_disables_external_entities(monkeypatch):
    # Assumption: tests run with project root on PYTHONPATH so `introduction` is importable.
    import introduction.views as views

    parser_mock = types.SimpleNamespace(setFeature=pytest.Mock())

    def fake_make_parser():
        return parser_mock

    def fake_parse_string(xml, parser=None):
        # Ensure the parser passed is the one we configured.
        assert parser is parser_mock
        return []

    monkeypatch.setattr(views, "make_parser", fake_make_parser)
    monkeypatch.setattr(views, "parseString", fake_parse_string)

    req = _make_request(body=b"<root><text>hello</text></root>")

    # We only care that external entities are disabled; the rest of the function may error
    # due to mocked parseString returning no nodes.
    with pytest.raises(Exception):
        views.xxe_parse(req)

    parser_mock.setFeature.assert_called_once_with(views.feature_external_ges, False)
