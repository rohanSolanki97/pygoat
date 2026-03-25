import pytest

# Assumption: project root is on PYTHONPATH and module can be imported as "introduction.views"
import introduction.views as views


class _DummyUser:
    is_authenticated = True


class _DummyRequest:
    def __init__(self, body: bytes):
        self.user = _DummyUser()
        self.body = body


def test_xxe_parse_disables_external_general_entities(mocker):
    # Arrange
    parser = mocker.Mock()
    make_parser_mock = mocker.patch.object(views, "make_parser", return_value=parser)

    # parseString is imported into module namespace; patch it to avoid real XML parsing
    parse_string_mock = mocker.patch.object(views, "parseString", return_value=[])

    # comments.objects.filter(...).update(...) should not hit DB
    comments_mock = mocker.Mock()
    comments_mock.objects.filter.return_value.update.return_value = 1
    mocker.patch.object(views, "comments", comments_mock)

    # render should not require templates
    render_mock = mocker.patch.object(views, "render", return_value=mocker.Mock())

    req = _DummyRequest(body=b"<root><text>hello</text></root>")

    # Act
    views.xxe_parse(req)

    # Assert: security fix - external general entities disabled
    make_parser_mock.assert_called_once()
    parser.setFeature.assert_called_once_with(views.feature_external_ges, False)
    parse_string_mock.assert_called_once()
    render_mock.assert_called_once()
