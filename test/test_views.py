import types

import pytest

# Assumption: tests run with repo root on PYTHONPATH so "introduction" is importable.
import introduction.views as views


def _make_request(xml_body: str):
    req = types.SimpleNamespace()
    req.user = types.SimpleNamespace(is_authenticated=True)
    req.body = xml_body.encode("utf-8")
    return req


def test_xxe_parse_disables_external_entities(mocker):
    # Arrange
    parser = mocker.Mock()
    mocker.patch("introduction.views.make_parser", return_value=parser)

    # Avoid real XML parsing and DB writes; only verify parser feature is set securely
    mocker.patch("introduction.views.parseString", return_value=[])
    mocker.patch("introduction.views.comments")

    request = _make_request("<root><text>hello</text></root>")

    # Act
    views.xxe_parse(request)

    # Assert: external general entities must be disabled
    parser.setFeature.assert_any_call(views.feature_external_ges, False)
