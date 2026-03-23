from types import SimpleNamespace

import pytest


# Assumption: tests run with project root on PYTHONPATH so `introduction` is importable.


def _make_authenticated_request(xml_bytes: bytes):
    user = SimpleNamespace(is_authenticated=True)
    return SimpleNamespace(user=user, body=xml_bytes)


def test_xxe_parse_disables_external_general_entities(mocker):
    from introduction import views

    request = _make_authenticated_request(b"<root><text>hello</text></root>")

    parser = mocker.Mock()
    make_parser_mock = mocker.patch.object(views, "make_parser", return_value=parser)

    # Avoid real XML parsing; just ensure parser is passed through.
    mocker.patch.object(views, "parseString", return_value=[])

    # Avoid DB update and template rendering.
    mocker.patch.object(views, "comments")
    render_mock = mocker.patch.object(views, "render", return_value=SimpleNamespace(status_code=200))

    views.xxe_parse(request)

    make_parser_mock.assert_called_once_with()
    parser.setFeature.assert_called_once_with(views.feature_external_ges, False)
    render_mock.assert_called_once()
