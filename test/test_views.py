import types

import pytest

# Assumption: tests run with repo root on PYTHONPATH so `introduction` is importable.
import introduction.views as views


def test_ssrf_lab_rejects_non_allowlisted_blog_filename_and_does_not_open_file(mocker):
    # Arrange
    request = types.SimpleNamespace(
        user=types.SimpleNamespace(is_authenticated=True),
        method="POST",
        POST={"blog": "../../etc/passwd"},
    )

    open_mock = mocker.patch("builtins.open", side_effect=AssertionError("open() should not be called for non-allowlisted input"))
    render_mock = mocker.patch("introduction.views.render", side_effect=lambda req, tpl, ctx=None: {"tpl": tpl, "ctx": ctx or {}})

    # Act
    result = views.ssrf_lab(request)

    # Assert
    assert open_mock.call_count == 0
    assert result["tpl"] == "Lab/ssrf/ssrf_lab.html"
    assert result["ctx"]["blog"] == "No blog found"
    render_mock.assert_called_once()


def test_ssrf_lab_allows_allowlisted_blog_filename_and_reads_file(mocker):
    # Arrange
    request = types.SimpleNamespace(
        user=types.SimpleNamespace(is_authenticated=True),
        method="POST",
        POST={"blog": "safe_blog.txt"},
    )

    m = mocker.mock_open(read_data="SAFE CONTENT")
    open_mock = mocker.patch("builtins.open", m)
    render_mock = mocker.patch("introduction.views.render", side_effect=lambda req, tpl, ctx=None: {"tpl": tpl, "ctx": ctx or {}})

    # Act
    result = views.ssrf_lab(request)

    # Assert
    open_mock.assert_called_once()
    assert result["tpl"] == "Lab/ssrf/ssrf_lab.html"
    assert result["ctx"]["blog"] == "SAFE CONTENT"
    render_mock.assert_called_once()
