import importlib
import types

import pytest


def _make_request(user_authenticated: bool, method: str = "POST", post=None):
    post = post or {}
    user = types.SimpleNamespace(is_authenticated=user_authenticated)
    return types.SimpleNamespace(method=method, POST=post, user=user)


def test_ssrf_lab_rejects_path_traversal_filename(mocker):
    # Arrange
    views = importlib.import_module("introduction.views")

    request = _make_request(
        user_authenticated=True,
        method="POST",
        post={"blog": "../secrets.txt"},
    )

    render_spy = mocker.patch.object(views, "render", autospec=True)

    # Act
    views.ssrf_lab(request)

    # Assert
    render_spy.assert_called_once()
    _, template, context = render_spy.call_args.args
    assert template == "Lab/ssrf/ssrf_lab.html"
    assert context == {"blog": "Invalid file name."}
