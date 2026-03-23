import types

import pytest

# Assumption: tests run with project root on PYTHONPATH, so "introduction" is importable.
import introduction.views as views


def _make_request(method="POST", authenticated=True, post=None):
    user = types.SimpleNamespace(is_authenticated=authenticated)
    req = types.SimpleNamespace()
    req.user = user
    req.method = method
    req.POST = post or {}
    return req


def test_ssrf_lab_rejects_non_allowlisted_blog_and_does_not_open_file(mocker):
    # Arrange
    request = _make_request(method="POST", post={"blog": "../../etc/passwd"})
    open_mock = mocker.patch("builtins.open", autospec=True)
    render_mock = mocker.patch.object(views, "render", autospec=True)

    # Act
    views.ssrf_lab(request)

    # Assert: should not attempt to open arbitrary path
    open_mock.assert_not_called()
    render_mock.assert_called()
    assert render_mock.call_args[0][1] == "Lab/ssrf/ssrf_lab.html"
    assert render_mock.call_args[0][2] == {"blog": "No blog found"}


def test_ssrf_lab_allows_allowlisted_blog_and_reads_via_safe_join(mocker):
    # Arrange
    request = _make_request(method="POST", post={"blog": "safe_blog.txt"})
    mocker.patch.object(views.os.path, "dirname", return_value="/app/introduction")
    join_mock = mocker.patch.object(views.os.path, "join", return_value="/app/introduction/safe_blog.txt")

    m = mocker.mock_open(read_data="SAFE CONTENT")
    open_mock = mocker.patch("builtins.open", m, create=True)
    render_mock = mocker.patch.object(views, "render", autospec=True)

    # Act
    views.ssrf_lab(request)

    # Assert
    join_mock.assert_called_once_with("/app/introduction", "safe_blog.txt")
    open_mock.assert_called_once_with("/app/introduction/safe_blog.txt", "r")
    render_mock.assert_called()
    assert render_mock.call_args[0][2] == {"blog": "SAFE CONTENT"}
