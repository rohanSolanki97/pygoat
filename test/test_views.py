import types

import pytest

# Assumption: tests run with project root on PYTHONPATH, so "introduction" is importable.
import introduction.views as views


def _make_request(body: bytes, authenticated=True):
    user = types.SimpleNamespace(is_authenticated=authenticated)
    req = types.SimpleNamespace()
    req.user = user
    req.body = body
    return req


def test_xxe_parse_disables_external_general_entities(mocker):
    parser = mocker.Mock()
    make_parser = mocker.patch.object(views, "make_parser", return_value=parser)

    node = types.SimpleNamespace(tagName="text", toxml=lambda: "<text>hello</text>")
    doc = [(views.START_ELEMENT, node)]
    parse_string = mocker.patch.object(views, "parseString", return_value=doc)

    class Doc(list):
        def expandNode(self, _node):
            return None

    parse_string.return_value = Doc(doc)

    comments_filter = mocker.Mock()
    comments_filter.update.return_value = 1
    mocker.patch.object(
        views.comments, "objects", mocker.Mock(filter=mocker.Mock(return_value=comments_filter))
    )

    request = _make_request(b"<root><text>hello</text></root>")

    views.xxe_parse(request)

    make_parser.assert_called_once()
    parser.setFeature.assert_called_once_with(views.feature_external_ges, False)
