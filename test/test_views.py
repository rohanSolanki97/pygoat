import importlib
import types

import pytest


def _make_request(user_authenticated: bool, body: bytes):
    user = types.SimpleNamespace(is_authenticated=user_authenticated)
    return types.SimpleNamespace(user=user, body=body)


def test_xxe_parse_disables_external_general_entities(mocker):
    # Arrange
    views = importlib.import_module("introduction.views")

    request = _make_request(
        user_authenticated=True,
        body=b"<root><text>hello</text></root>",
    )

    # Stub out parser + downstream XML parsing so we only assert the security-relevant flag.
    parser = mocker.Mock()
    mocker.patch.object(views, "make_parser", autospec=True, return_value=parser)

    # parseString is imported into the module namespace; stub it to avoid real XML parsing.
    mocker.patch.object(views, "parseString", autospec=True, return_value=[])

    # Avoid DB update and template rendering side effects.
    mocker.patch.object(views.comments.objects, "filter", autospec=True)
    mocker.patch.object(views, "render", autospec=True)

    # Act
    views.xxe_parse(request)

    # Assert
    parser.setFeature.assert_any_call(views.feature_external_ges, False)
