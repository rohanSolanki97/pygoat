from types import SimpleNamespace

import pytest


# Assumption: tests run with project root on PYTHONPATH so `introduction` is importable.


def _make_authenticated_post_request(blog_value: str):
    user = SimpleNamespace(is_authenticated=True)
    return SimpleNamespace(user=user, method="POST", POST={"blog": blog_value})


def test_ssrf_lab_rejects_non_allowlisted_blog_filename(mocker):
    from introduction import views

    request = _make_authenticated_post_request("../../etc/passwd")

    render_mock = mocker.patch.object(views, "render", return_value=SimpleNamespace(status_code=200))
    open_mock = mocker.patch("builtins.open", side_effect=AssertionError("open() must not be called for disallowed files"))

    views.ssrf_lab(request)

    assert open_mock.call_count == 0
    render_mock.assert_called_once()
    assert render_mock.call_args.args[1] == "Lab/ssrf/ssrf_lab.html"
    assert render_mock.call_args.args[2] == {"blog": "No blog found"}


def test_ssrf_lab_allows_only_allowlisted_files_and_uses_safe_join(mocker):
    from introduction import views

    request = _make_authenticated_post_request("safe_blog.txt")

    dirname_mock = mocker.patch.object(views.os.path, "dirname", return_value="/app/introduction")
    join_mock = mocker.patch.object(views.os.path, "join", return_value="/app/introduction/safe_blog.txt")

    m = mocker.mock_open(read_data="SAFE CONTENT")
    mocker.patch("builtins.open", m)

    render_mock = mocker.patch.object(views, "render", return_value=SimpleNamespace(status_code=200))

    views.ssrf_lab(request)

    dirname_mock.assert_called_once()
    join_mock.assert_called_once_with("/app/introduction", "safe_blog.txt")
    m.assert_called_once_with("/app/introduction/safe_blog.txt", "r")
    render_mock.assert_called_once()
    assert render_mock.call_args.args[2] == {"blog": "SAFE CONTENT"}
