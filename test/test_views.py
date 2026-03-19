# This test targets the path traversal fix in ssrf_lab: absolute paths and ".." must be rejected
# and safe_join must be used instead of os.path.join.
import pytest

# Assumption: tests run with repository root on PYTHONPATH so `introduction` is importable.
from introduction import views as views_module


def _make_authenticated_request(mocker, file_value):
    request = mocker.Mock()
    request.user.is_authenticated = True
    request.method = "POST"
    request.POST = {"blog": file_value}
    return request


def test_ssrf_lab_rejects_absolute_path_and_does_not_call_safe_join(mocker):
    # Arrange
    request = _make_authenticated_request(mocker, "/etc/passwd")

    safe_join_mock = mocker.patch.object(views_module, "safe_join")
    mocker.patch.object(views_module.os.path, "isabs", return_value=True)
    render_mock = mocker.patch.object(views_module, "render", return_value="No blog found")

    # Act
    resp = views_module.ssrf_lab(request)

    # Assert
    assert resp == "No blog found"
    safe_join_mock.assert_not_called()
    render_mock.assert_called()  # falls into except and renders "No blog found"


def test_ssrf_lab_rejects_parent_traversal_and_does_not_call_safe_join(mocker):
    # Arrange
    request = _make_authenticated_request(mocker, "../secrets.txt")

    safe_join_mock = mocker.patch.object(views_module, "safe_join")
    mocker.patch.object(views_module.os.path, "isabs", return_value=False)
    render_mock = mocker.patch.object(views_module, "render", return_value="No blog found")

    # Act
    resp = views_module.ssrf_lab(request)

    # Assert
    assert resp == "No blog found"
    safe_join_mock.assert_not_called()
    render_mock.assert_called()


def test_ssrf_lab_uses_safe_join_for_relative_paths(mocker):
    # Arrange
    request = _make_authenticated_request(mocker, "Lab/ssrf/blog.txt")

    mocker.patch.object(views_module.os.path, "isabs", return_value=False)
    safe_join_mock = mocker.patch.object(views_module, "safe_join", return_value="/safe/base/Lab/ssrf/blog.txt")

    file_handle = mocker.Mock()
    file_handle.read.return_value = "BLOG_CONTENT"
    open_mock = mocker.patch.object(views_module, "open", return_value=file_handle)

    render_mock = mocker.patch.object(views_module, "render", return_value="OK")

    # Act
    resp = views_module.ssrf_lab(request)

    # Assert
    assert resp == "OK"
    safe_join_mock.assert_called_once()
    open_mock.assert_called_once_with("/safe/base/Lab/ssrf/blog.txt", "r")
    render_mock.assert_called_once()
