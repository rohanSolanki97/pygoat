import types

import pytest

# Assumption: tests run with repo root on PYTHONPATH so "introduction" is importable.
import introduction.views as views


def test_xxe_parse_disables_external_general_entities(mocker):
    # Arrange
    request = types.SimpleNamespace(body=b"<root><text>Hello</text></root>")

    parser_mock = mocker.Mock()
    make_parser_mock = mocker.patch("introduction.views.make_parser", return_value=parser_mock)

    # Avoid real XML parsing; just ensure parser is passed through.
    mocker.patch("introduction.views.parseString", return_value=[(views.START_ELEMENT, types.SimpleNamespace(tagName="text", toxml=lambda: "<text>Hello</text>"))])

    # Avoid DB access
    comments_filter_mock = mocker.Mock()
    comments_filter_mock.update.return_value = 1
    mocker.patch.object(views.comments, "objects", mocker.Mock(filter=mocker.Mock(return_value=comments_filter_mock)))

    # Avoid template rendering
    render_mock = mocker.patch("introduction.views.render", return_value=types.SimpleNamespace(status_code=200))

    # Act
    resp = views.xxe_parse(request)

    # Assert: secure behavior - external entity processing disabled
    make_parser_mock.assert_called_once()
    parser_mock.setFeature.assert_called_once_with(views.feature_external_ges, False)
    assert resp.status_code == 200
    render_mock.assert_called_once()
