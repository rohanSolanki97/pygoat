import types

import pytest


# Assumption: Django app module path is "introduction.views" as per file_path.
from introduction import views


def _make_request(xml_body: str):
    user = types.SimpleNamespace(is_authenticated=True)
    req = types.SimpleNamespace()
    req.user = user
    req.body = xml_body.encode("utf-8")
    return req


def test_xxe_parse_disables_external_entities(mocker):
    # Arrange
    request = _make_request("<root><text>Hello</text></root>")

    parser = mocker.Mock()
    make_parser_mock = mocker.patch("introduction.views.make_parser", return_value=parser)

    # Avoid real XML parsing; we only care about the parser feature flag being set to False.
    mocker.patch("introduction.views.parseString", return_value=[])
    mocker.patch("introduction.views.render", return_value="rendered")
    mocker.patch("introduction.views.comments")

    # Act
    views.xxe_parse(request)

    # Assert
    make_parser_mock.assert_called_once()
    parser.setFeature.assert_called_once_with(views.feature_external_ges, False)
