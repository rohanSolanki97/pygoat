import types

import pytest


# Assumption: tests run with project root on PYTHONPATH so `introduction` is importable.


def _make_request(body: bytes, user_authenticated: bool = True):
    class _User:
        is_authenticated = user_authenticated

    req = types.SimpleNamespace()
    req.method = "POST"
    req.body = body
    req.user = _User()
    req.POST = {}
    req.COOKIES = {}
    req.META = {}
    req.headers = {}
    return req


def test_xxe_parse_disables_external_general_entities(mocker):
    from introduction import views

    # Arrange
    parser_mock = mocker.Mock()
    make_parser_mock = mocker.patch.object(views, "make_parser", return_value=parser_mock)

    # parseString is called with parser=parser; we don't need real XML parsing here
    doc_iterable = []
    mocker.patch.object(views, "parseString", return_value=doc_iterable)

    # Avoid DB interaction
    mocker.patch.object(views, "comments")

    # Act
    views.xxe_parse(_make_request(b"<root/>"))

    # Assert
    make_parser_mock.assert_called_once()
    parser_mock.setFeature.assert_called_once_with(views.feature_external_ges, False)
