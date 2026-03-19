# This test targets the XXE fix: feature_external_ges must be disabled.
from xml.sax.handler import feature_external_ges

import pytest

# Assumption: tests run with repository root on PYTHONPATH so `introduction` is importable.
from introduction import views as views_module


def test_xxe_parse_disables_external_general_entities(mocker):
    # Arrange
    parser = mocker.Mock()
    make_parser_mock = mocker.patch.object(views_module, "make_parser", return_value=parser)

    # parseString is called with request.body.decode('utf-8'); we don't need real XML parsing here.
    parse_string_mock = mocker.patch.object(views_module, "parseString", return_value=[])

    # Avoid DB update and template rendering side effects
    comments_mock = mocker.Mock()
    comments_mock.objects.filter.return_value.update.return_value = 1
    mocker.patch.object(views_module, "comments", comments_mock)
    mocker.patch.object(views_module, "render", return_value=mocker.Mock())

    request = mocker.Mock()
    request.body = b"<text>hello</text>"

    # Act
    views_module.xxe_parse(request)

    # Assert
    make_parser_mock.assert_called_once()
    parser.setFeature.assert_any_call(feature_external_ges, False)
    parse_string_mock.assert_called_once()
