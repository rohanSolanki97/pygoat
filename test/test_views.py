import importlib
import types

import pytest


def _make_request(user_authenticated: bool, method: str = "POST", post=None):
    post = post or {}
    user = types.SimpleNamespace(is_authenticated=user_authenticated)
    return types.SimpleNamespace(method=method, POST=post, user=user)


def test_ssrf_lab2_blocks_non_allowlisted_domain_and_does_not_call_requests_get(mocker):
    # Arrange
    views = importlib.import_module("introduction.views")

    request = _make_request(
        user_authenticated=True,
        method="POST",
        post={"url": "http://evil.com/internal"},
    )

    render_spy = mocker.patch.object(views, "render", autospec=True)
    requests_get = mocker.patch.object(views.requests, "get", autospec=True)

    # Act
    views.ssrf_lab2(request)

    # Assert
    requests_get.assert_not_called()
    render_spy.assert_called_once()
    _, template, context = render_spy.call_args.args
    assert template == "Lab/ssrf/ssrf_lab2.html"
    assert context == {"error": "URL not allowed"}
