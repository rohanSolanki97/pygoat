import types

import pytest


# Assumption: Django app module path is "introduction.views" as per file_path.
from introduction import views


def _make_authenticated_post(blog_value: str):
    user = types.SimpleNamespace(is_authenticated=True)
    req = types.SimpleNamespace()
    req.user = user
    req.method = "POST"
    req.POST = {"blog": blog_value}
    return req


def test_ssrf_lab_blocks_non_allowlisted_file_and_does_not_open(mocker):
    # Arrange
    request = _make_authenticated_post("../../etc/passwd")

    open_mock = mocker.patch(
        "builtins.open",
        side_effect=AssertionError("open() should not be called for disallowed file"),
    )
    render_mock = mocker.patch("introduction.views.render", side_effect=lambda _req, _tpl, ctx=None: ctx)

    # Act
    ctx = views.ssrf_lab(request)

    # Assert
    assert ctx == {"blog": "No blog found"}
    assert open_mock.call_count == 0
    render_mock.assert_called_once()
