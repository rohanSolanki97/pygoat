import types

import pytest


def _make_request(*, authenticated=True, body=b""):
    user = types.SimpleNamespace(is_authenticated=authenticated)
    return types.SimpleNamespace(method="POST", body=body, user=user)


def test_xxe_parse_disables_external_general_entities(mocker):
    # This test asserts the security fix: external entity processing is disabled.
    import introduction.views as views

    parser_mock = mocker.Mock()
    mocker.patch.object(views, "make_parser", return_value=parser_mock)

    # Avoid real XML parsing; we only care about parser feature flag.
    mocker.patch.object(views, "parseString", return_value=[])
    mocker.patch.object(views, "render", return_value="rendered")

    # Provide minimal body; parseString is mocked.
    req = _make_request(body=b"<root/>")

    views.xxe_parse(req)

    parser_mock.setFeature.assert_called_once_with(views.feature_external_ges, False)
