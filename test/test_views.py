import pytest

# Assumption: tests run with repo root on PYTHONPATH so "introduction" is importable.
from introduction import views


def test_ssrf_lab_rejects_non_allowlisted_filename(mocker):
    # Arrange
    mocker.patch("introduction.views.render", side_effect=lambda request, tpl, ctx=None: {"tpl": tpl, "ctx": ctx})

    request = mocker.Mock()
    request.user.is_authenticated = True
    request.method = "POST"
    request.POST.get.side_effect = lambda k, default=None: {"blog": "../../etc/passwd"}.get(k, default)
    request.POST.__getitem__.side_effect = lambda k: {"blog": "../../etc/passwd"}[k]

    open_mock = mocker.patch("builtins.open", side_effect=AssertionError("open() must not be called for non-allowlisted input"))

    # Act
    resp = views.ssrf_lab(request)

    # Assert
    assert resp["ctx"]["blog"] == "No blog found"
    open_mock.assert_not_called()


def test_ssrf_lab_reads_allowlisted_file_only(mocker):
    # Arrange
    mocker.patch("introduction.views.render", side_effect=lambda request, tpl, ctx=None: {"tpl": tpl, "ctx": ctx})
    mocker.patch("introduction.views.os.path.dirname", return_value="/app/introduction")
    mocker.patch("introduction.views.os.path.join", side_effect=lambda a, b: f"{a}/{b}")

    m = mocker.mock_open(read_data="SAFE CONTENT")
    open_mock = mocker.patch("builtins.open", m)

    request = mocker.Mock()
    request.user.is_authenticated = True
    request.method = "POST"
    request.POST.get.side_effect = lambda k, default=None: {"blog": "safe_blog.txt"}.get(k, default)
    request.POST.__getitem__.side_effect = lambda k: {"blog": "safe_blog.txt"}[k]

    # Act
    resp = views.ssrf_lab(request)

    # Assert
    open_mock.assert_called_once_with("/app/introduction/safe_blog.txt", "r")
    assert resp["ctx"]["blog"] == "SAFE CONTENT"
