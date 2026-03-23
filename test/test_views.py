import os
import types

import pytest


def _make_request(*, authenticated=True, blog_value):
    user = types.SimpleNamespace(is_authenticated=authenticated)
    return types.SimpleNamespace(method="POST", POST={"blog": blog_value}, user=user)


def test_ssrf_lab_rejects_non_allowlisted_blog_filename(mocker):
    import introduction.views as views

    # Ensure we don't touch filesystem and we can observe behavior.
    open_mock = mocker.patch("builtins.open", side_effect=AssertionError("open() should not be called"))
    render_mock = mocker.patch.object(views, "render", side_effect=lambda request, template, context: context)

    req = _make_request(blog_value="../../etc/passwd")

    result = views.ssrf_lab(req)

    assert result == {"blog": "No blog found"}
    open_mock.assert_not_called()
    render_mock.assert_called_once()


def test_ssrf_lab_allows_only_allowlisted_files_and_opens_joined_path(mocker, tmp_path):
    import introduction.views as views

    # Arrange a fake directory for __file__ resolution.
    fake_dir = tmp_path
    safe_file = fake_dir / "safe_blog.txt"
    safe_file.write_text("hello")

    mocker.patch.object(views.os.path, "dirname", return_value=str(fake_dir))

    # Use real open but assert the path is within fake_dir and matches allowlist.
    real_open = open

    def _open_side_effect(path, mode="r", *args, **kwargs):
        assert os.path.abspath(path) == os.path.abspath(str(safe_file))
        return real_open(path, mode, *args, **kwargs)

    mocker.patch("builtins.open", side_effect=_open_side_effect)
    mocker.patch.object(views, "render", side_effect=lambda request, template, context: context)

    req = _make_request(blog_value="safe_blog.txt")

    result = views.ssrf_lab(req)

    assert result == {"blog": "hello"}
