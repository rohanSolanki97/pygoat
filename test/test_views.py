import types

import pytest

# Assumption: Django app module path is "introduction.views" based on source file location.
import introduction.views as views


def test_xxe_parse_disables_external_general_entities(mocker):
    # Arrange
    request = types.SimpleNamespace(
        user=types.SimpleNamespace(is_authenticated=True),
        body=b"<text>Hello</text>",
    )

    parser = mocker.Mock()
    make_parser_mock = mocker.patch("introduction.views.make_parser", return_value=parser)

    # parseString is used as an iterator of (event, node)
    node = types.SimpleNamespace(tagName="text", toxml=lambda: "<text>Hello</text>")
    parse_string_mock = mocker.patch(
        "introduction.views.parseString",
        return_value=[(views.START_ELEMENT, node)],
    )

    # comments.objects.filter(id=1).update(comment=text)
    comments_mock = mocker.patch("introduction.views.comments")
    comments_mock.objects.filter.return_value.update.return_value = 1

    render_mock = mocker.patch("introduction.views.render", return_value="rendered")

    # Act
    result = views.xxe_parse(request)

    # Assert
    make_parser_mock.assert_called_once()
    parser.setFeature.assert_called_once_with(views.feature_external_ges, False)
    parse_string_mock.assert_called_once()
    render_mock.assert_called_once_with(request, "Lab/XXE/xxe_lab.html")
    assert result == "rendered"
