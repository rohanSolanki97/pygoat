import types

import pytest

# Assumption: tests run with repo root on PYTHONPATH so `introduction` is importable.
import introduction.views as views


def test_xxe_parse_disables_external_entities_feature(mocker):
    # Arrange
    parser_instance = mocker.Mock()
    make_parser_mock = mocker.patch("introduction.views.make_parser", return_value=parser_instance)

    # Ensure parseString is called but doesn't need to actually parse XML for this delta behavior.
    mocker.patch("introduction.views.parseString", return_value=[])

    request = types.SimpleNamespace(body=b"<root/>")

    # Act
    views.xxe_parse(request)

    # Assert
    make_parser_mock.assert_called_once()
    parser_instance.setFeature.assert_called_once_with(views.feature_external_ges, False)
