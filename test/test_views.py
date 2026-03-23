import os
from types import SimpleNamespace

import pytest


# Assumption: tests run with project root on PYTHONPATH so `introduction` is importable.
from introduction import views


def _fake_request(blog_value: str, authenticated: bool = True):
    user = SimpleNamespace(is_authenticated=authenticated)
    return SimpleNamespace(user=user, method="POST", POST={"blog": blog_value})


def test_ssrf_lab_blocks_non_whitelisted_file_and_does_not_open(mocker):
    # Arrange
    req = _fake_request("../../etc/passwd")

    open_mock = mocker.patch("builtins.open", side_effect=AssertionError("open() must not be called for non-whitelisted files"))
    render_mock = mocker.patch("introduction.views.render", return_value=SimpleNamespace(status_code=200))

    # Act
    resp = views.ssrf_lab(req)

    # Assert
    assert resp.status_code == 200
    open_mock.assert_not_called()
    render_mock.assert_called_once()
    assert render_mock.call_args.args[1] == "Lab/ssrf/ssrf_lab.html"
    assert render_mock.call_args.args[2] == {"blog": "No blog found"}


def test_ssrf_lab_allows_only_whitelisted_file_and_opens_joined_path(mocker):
    # Arrange
    req = _fake_request("safe_blog.txt")

    dirname = os.path.dirname(views.__file__)
    expected_path = os.path.join(dirname, "safe_blog.txt")

    file_handle = mocker.mock_open(read_data="SAFE CONTENT")
    open_mock = mocker.patch("builtins.open", file_handle)
    render_mock = mocker.patch("introduction.views.render", return_value=SimpleNamespace(status_code=200))

    # Act
    resp = views.ssrf_lab(req)

    # Assert
    assert resp.status_code == 200
    open_mock.assert_called_once_with(expected_path, "r")
    render_mock.assert_called_once()
    assert render_mock.call_args.args[2] == {"blog": "SAFE CONTENT"}
