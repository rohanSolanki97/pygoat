import pytest

# Assumption: tests run with repo root on PYTHONPATH so "introduction" is importable.
from introduction import views


def test_xxe_parse_disables_external_general_entities(mocker):
    # Arrange
    parser = mocker.Mock()
    make_parser_mock = mocker.patch("introduction.views.make_parser", return_value=parser)

    # Avoid XML parsing and DB writes; we only care about the parser feature flag.
    doc_iter = [(mocker.Mock(), mocker.Mock(tagName="text"))]
    parse_string_mock = mocker.patch("introduction.views.parseString", return_value=doc_iter)

    # Ensure loop doesn't crash
    node = doc_iter[0][1]
    node.toxml.return_value = "<text>hello</text>"
    doc_iter[0][0].__eq__ = lambda self, other: True  # not used; START_ELEMENT compare is done directly

    mocker.patch("introduction.views.comments.objects.filter", return_value=mocker.Mock(update=mocker.Mock(return_value=1)))
    mocker.patch("introduction.views.render", side_effect=lambda request, tpl, ctx=None: {"tpl": tpl, "ctx": ctx})

    request = mocker.Mock()
    request.body = b"<root/>"

    # Act
    views.xxe_parse(request)

    # Assert
    make_parser_mock.assert_called_once()
    parser.setFeature.assert_called_once_with(views.feature_external_ges, False)
    parse_string_mock.assert_called_once()
