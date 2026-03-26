import types

import pytest

# Assumption: tests run with repo root on PYTHONPATH so "introduction" is importable.
import introduction.views as views


def test_ssrf_lab_rejects_non_allowlisted_blog_filename(mocker):
    # Arrange
    request = types.SimpleNamespace(
        user=types.SimpleNamespace(is_authenticated=True),
        method="POST",
        POST={"blog": "../../etc/passwd"},
    )
    render_mock = mocker.patch("introduction.views.render", return_value=types.SimpleNamespace(status_code=200))
    open_mock = mocker.patch("builtins.open", side_effect=AssertionError("open() must not be called for disallowed files"))

    # Act
    resp = views.ssrf_lab(request)

    # Assert
    assert resp.status_code == 200
    open_mock.assert_not_called()
    render_mock.assert_called_once()
    args, kwargs = render_mock.call_args
    assert args[1] == "Lab/ssrf/ssrf_lab.html"
    assert args[2] == {"blog": "No blog found"}


def test_ssrf_lab_allows_allowlisted_blog_filename_and_reads_file(mocker):
    # Arrange
    request = types.SimpleNamespace(
        user=types.SimpleNamespace(is_authenticated=True),
        method="POST",
        POST={"blog": "safe_blog.txt"},
    )
    render_mock = mocker.patch("introduction.views.render", return_value=types.SimpleNamespace(status_code=200))

    m = mocker.mock_open(read_data="SAFE CONTENT")
    open_mock = mocker.patch("builtins.open", m)

    # Act
    resp = views.ssrf_lab(request)

    # Assert
    assert resp.status_code == 200
    open_mock.assert_called_once()
    render_mock.assert_called_once()
    args, kwargs = render_mock.call_args
    assert args[1] == "Lab/ssrf/ssrf_lab.html"
    assert args[2] == {"blog": "SAFE CONTENT"}
