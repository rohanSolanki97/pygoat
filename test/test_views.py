import types

import pytest

# Assumption: tests run with repo root on PYTHONPATH so `introduction` is importable.
import introduction.views as views


def _make_request(method="POST", authenticated=True, post=None):
    user = types.SimpleNamespace(is_authenticated=authenticated)
    req = types.SimpleNamespace()
    req.user = user
    req.method = method
    req.POST = post or {}
    return req


def test_ssrf_lab_allows_only_whitelisted_files_and_uses_safe_open(mocker):
    # Arrange
    request = _make_request(method="POST", authenticated=True, post={"blog": "../secrets.txt"})

    open_mock = mocker.patch("builtins.open", side_effect=AssertionError("open() must not be called for disallowed files"))
    render_mock = mocker.patch("introduction.views.render", return_value=mocker.Mock())

    # Act
    views.ssrf_lab(request)

    # Assert: disallowed path is rejected and no file IO occurs
    assert open_mock.call_count == 0
    render_mock.assert_called()
    _, args, kwargs = render_mock.mock_calls[0]
    assert args[1] == "Lab/ssrf/ssrf_lab.html"
    assert args[2] == {"blog": "No blog found"}


def test_ssrf_lab_reads_allowed_file_with_context_manager(mocker):
    # Arrange
    request = _make_request(method="POST", authenticated=True, post={"blog": "safe_blog.txt"})

    m = mocker.mock_open(read_data="SAFE CONTENT")
    open_mock = mocker.patch("builtins.open", m)
    render_mock = mocker.patch("introduction.views.render", return_value=mocker.Mock())

    # Act
    views.ssrf_lab(request)

    # Assert: allowed file is opened and content returned
    open_mock.assert_called_once()
    render_mock.assert_called()
    _, args, kwargs = render_mock.mock_calls[-1]
    assert args[1] == "Lab/ssrf/ssrf_lab.html"
    assert args[2] == {"blog": "SAFE CONTENT"}
