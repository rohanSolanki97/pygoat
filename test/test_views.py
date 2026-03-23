import os
import types

import pytest


# Assumption: tests run with project root on PYTHONPATH so `introduction` is importable.


def _make_request(blog_value: str, user_authenticated: bool = True):
    class _User:
        is_authenticated = user_authenticated

    req = types.SimpleNamespace()
    req.method = "POST"
    req.POST = {"blog": blog_value}
    req.user = _User()
    req.COOKIES = {}
    req.body = b""
    req.META = {}
    req.headers = {}
    return req


def test_ssrf_lab_rejects_non_allowlisted_blog_and_does_not_open_file(mocker):
    from introduction import views

    # Arrange: attempt path traversal
    req = _make_request("../../etc/passwd")

    open_mock = mocker.patch("builtins.open", side_effect=AssertionError("open() should not be called"))
    render_mock = mocker.patch.object(views, "render", return_value="RENDERED")

    # Act
    resp = views.ssrf_lab(req)

    # Assert
    assert resp == "RENDERED"
    open_mock.assert_not_called()
    render_mock.assert_called_once()
    _, _, ctx = render_mock.call_args[0]
    assert ctx == {"blog": "No blog found"}


def test_ssrf_lab_allows_allowlisted_blog_and_reads_from_joined_path(mocker):
    from introduction import views

    # Arrange
    req = _make_request("safe_blog.txt")

    dirname_mock = mocker.patch.object(views.os.path, "dirname", return_value="/app/introduction")
    join_mock = mocker.patch.object(views.os.path, "join", wraps=os.path.join)

    file_handle = mocker.mock_open(read_data="SAFE CONTENT")
    open_mock = mocker.patch("builtins.open", file_handle)
    render_mock = mocker.patch.object(views, "render", return_value="RENDERED")

    # Act
    resp = views.ssrf_lab(req)

    # Assert
    assert resp == "RENDERED"
    dirname_mock.assert_called_once()
    join_mock.assert_called_once_with("/app/introduction", "safe_blog.txt")
    open_mock.assert_called_once()
    render_mock.assert_called_once()
    _, _, ctx = render_mock.call_args[0]
    assert ctx == {"blog": "SAFE CONTENT"}
