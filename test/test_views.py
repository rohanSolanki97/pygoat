import types

import pytest

# Assumption: Django app module path is "introduction.views" based on source file location.
import introduction.views as views


def test_ssrf_lab_allows_only_whitelisted_blog_files(mocker):
    # Arrange
    request = types.SimpleNamespace(
        user=types.SimpleNamespace(is_authenticated=True),
        method="POST",
        POST={"blog": "../../etc/passwd"},
    )

    render_mock = mocker.patch("introduction.views.render", side_effect=lambda req, tpl, ctx=None: {"tpl": tpl, "ctx": ctx})
    open_mock = mocker.patch("builtins.open", side_effect=AssertionError("open() should not be called for non-whitelisted input"))

    # Act
    result = views.ssrf_lab(request)

    # Assert
    assert result["tpl"] == "Lab/ssrf/ssrf_lab.html"
    assert result["ctx"] == {"blog": "No blog found"}
    open_mock.assert_not_called()
    render_mock.assert_called_once()
