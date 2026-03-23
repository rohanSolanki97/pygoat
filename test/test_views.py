from types import SimpleNamespace

import pytest


# Assumption: tests run with project root on PYTHONPATH so `introduction` is importable.
from introduction import views


def _fake_request(body: bytes, authenticated: bool = True):
    user = SimpleNamespace(is_authenticated=authenticated)
    return SimpleNamespace(user=user, body=body)


def test_xxe_parse_disables_external_entities(mocker):
    # Arrange
    parser = mocker.Mock()
    make_parser_mock = mocker.patch("introduction.views.make_parser", return_value=parser)

    # Avoid real XML parsing; we only assert parser feature is set securely.
    mocker.patch("introduction.views.parseString", return_value=[])
    mocker.patch("introduction.views.render", return_value=SimpleNamespace(status_code=200))
    comments_filter = mocker.Mock()
    comments_filter.update.return_value = 1
    mocker.patch("introduction.views.comments.objects.filter", return_value=comments_filter)

    req = _fake_request(b"<root><text>hello</text></root>")

    # Act
    resp = views.xxe_parse(req)

    # Assert
    assert resp.status_code == 200
    make_parser_mock.assert_called_once()
    parser.setFeature.assert_called_once_with(views.feature_external_ges, False)
