import types

import pytest

import introduction.views as views


def _make_request(blog_value: str):
    req = types.SimpleNamespace()
    req.user = types.SimpleNamespace(is_authenticated=True)
    req.method = "POST"
    req.POST = {"blog": blog_value}
    return req


def test_ssrf_lab_rejects_non_whitelisted_blog_selection(mocker):
    # Arrange
    # Avoid decorator side-effects in unit test
    mocker.patch.object(views, "authentication_decorator", lambda f: f)

    request = _make_request("../../etc/passwd")

    # Act
    resp = views.ssrf_lab(request)

    # Assert
    assert isinstance(resp, views.HttpResponseBadRequest)
    assert resp.status_code == 400
    assert b"Invalid blog selection" in resp.content


def test_ssrf_lab_uses_whitelisted_filename_not_user_input(mocker):
    # Arrange
    mocker.patch.object(views, "authentication_decorator", lambda f: f)
    # If vulnerable behavior existed, os.path.join would receive the raw user input.
    join_spy = mocker.patch.object(views.os.path, "join", wraps=views.os.path.join)
    # Prevent actual file IO and template rendering
    mocker.patch.object(views, "open", mocker.mock_open(read_data="BLOG"), create=True)
    mocker.patch.object(views, "render", autospec=True, return_value=types.SimpleNamespace(status_code=200))

    request = _make_request("default")

    # Act
    resp = views.ssrf_lab(request)

    # Assert
    assert resp.status_code == 200
    # Ensure join was called with the safe whitelisted filename, not the key
    assert any(call.args[1] == "safe_blog.txt" for call in join_spy.call_args_list)
    assert all(call.args[1] != "default" for call in join_spy.call_args_list)
