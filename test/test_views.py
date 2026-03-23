import types

import pytest

# Assumption: tests run with repo root on PYTHONPATH so "introduction" is importable.
import introduction.views as views


def _make_request(blog_value: str):
    req = types.SimpleNamespace()
    req.method = "POST"
    req.POST = {"blog": blog_value}
    req.user = types.SimpleNamespace(is_authenticated=True)
    return req


def test_ssrf_lab_rejects_non_allowlisted_blog_filename_and_does_not_open(mocker):
    # Arrange
    open_mock = mocker.patch("builtins.open", side_effect=AssertionError("open() must not be called"))
    render_mock = mocker.patch("introduction.views.render", return_value="rendered")

    request = _make_request("../../etc/passwd")

    # Act
    result = views.ssrf_lab(request)

    # Assert
    assert result == "rendered"
    open_mock.assert_not_called()
    render_mock.assert_called_once()
    assert render_mock.call_args[0][1] == "Lab/ssrf/ssrf_lab.html"
    assert render_mock.call_args[0][2] == {"blog": "No blog found"}
