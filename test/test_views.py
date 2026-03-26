import types

import pytest

# Assumption: tests run with repo root on PYTHONPATH so `introduction` is importable.
import introduction.views as views


def _make_request(body: bytes, authenticated=True):
    user = types.SimpleNamespace(is_authenticated=authenticated)
    req = types.SimpleNamespace()
    req.user = user
    req.body = body
    return req


def test_xxe_parse_disables_external_entities(mocker):
    # Arrange
    parser = mocker.Mock()
    make_parser_mock = mocker.patch("introduction.views.make_parser", return_value=parser)

    # Avoid real XML parsing; we only assert parser feature configuration.
    parse_string_mock = mocker.patch("introduction.views.parseString", return_value=[])

    # Avoid DB update side effects
    comments_mock = mocker.patch("introduction.views.comments")
    comments_mock.objects.filter.return_value.update.return_value = 1

    # Avoid template rendering requirements
    render_mock = mocker.patch("introduction.views.render", return_value=mocker.Mock())

    request = _make_request(b"<root><text>hello</text></root>", authenticated=True)

    # Act
    views.xxe_parse(request)

    # Assert
    make_parser_mock.assert_called_once()
    parser.setFeature.assert_called_once_with(views.feature_external_ges, False)
    parse_string_mock.assert_called_once()
    render_mock.assert_called_once()
