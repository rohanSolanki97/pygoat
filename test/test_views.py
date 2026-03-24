import types

import pytest


# Assumption: tests run with project root on PYTHONPATH so `introduction` is importable.
from introduction import views


def test_ssrf_lab_rejects_non_allowlisted_filename_and_does_not_open(mocker):
    # Arrange
    request = types.SimpleNamespace(
        user=types.SimpleNamespace(is_authenticated=True),
        method="POST",
        POST={"blog": "../../etc/passwd"},
    )

    open_mock = mocker.patch("builtins.open", side_effect=AssertionError("open() should not be called for non-allowlisted files"))
    render_mock = mocker.patch.object(views, "render", return_value="rendered")

    # Act
    result = views.ssrf_lab(request)

    # Assert
    assert result == "rendered"
    render_mock.assert_called_once()
    _, template_name, context = render_mock.call_args[0]
    assert template_name == "Lab/ssrf/ssrf_lab.html"
    assert context == {"blog": "No blog found"}
    assert open_mock.call_count == 0
