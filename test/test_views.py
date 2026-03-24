import types

import pytest


# Assumption: tests run with project root on PYTHONPATH so `introduction` is importable.
from introduction import views


def test_xxe_parse_disables_external_general_entities(mocker):
    # Arrange
    request = types.SimpleNamespace(
        user=types.SimpleNamespace(is_authenticated=True),
        body=b"<root><text>Hello</text></root>",
    )

    parser_mock = mocker.Mock()
    make_parser_mock = mocker.patch.object(views, "make_parser", return_value=parser_mock)

    # Avoid real XML parsing; just ensure the secure parser is configured.
    mocker.patch.object(views, "parseString", return_value=[(views.START_ELEMENT, types.SimpleNamespace(tagName="text", toxml=lambda: "<text>Hello</text>"))])
    mocker.patch.object(views, "render", return_value="rendered")
    mocker.patch.object(views, "comments")

    # Act
    views.xxe_parse(request)

    # Assert
    make_parser_mock.assert_called_once_with()
    parser_mock.setFeature.assert_called_once_with(views.feature_external_ges, False)
