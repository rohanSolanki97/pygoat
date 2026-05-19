import os
import pytest


def test_ssrf_lab_rejects_path_traversal_and_absolute_path():
    import introduction.views as views

    class DummyUser:
        is_authenticated = True

    class DummyRequest:
        user = DummyUser()
        method = "POST"
        POST = {"blog": "../secrets.txt"}

    with pytest.raises(ValueError, match="Invalid file path"):
        views.ssrf_lab(DummyRequest())

    class DummyRequestAbs:
        user = DummyUser()
        method = "POST"
        POST = {"blog": os.path.abspath("/etc/passwd")}

    with pytest.raises(ValueError, match="Invalid file path"):
        views.ssrf_lab(DummyRequestAbs())


def test_ssrf_lab_uses_basename_before_joining(monkeypatch):
    import introduction.views as views

    class DummyUser:
        is_authenticated = True

    class DummyRequest:
        user = DummyUser()
        method = "POST"
        POST = {"blog": "subdir/../blog.txt"}

    # Arrange: if basename is used, open will be called with .../blog.txt
    opened_paths = {}

    def fake_open(path, mode="r", *args, **kwargs):
        opened_paths["path"] = path
        raise FileNotFoundError()

    monkeypatch.setattr(views, "open", fake_open, raising=False)

    # Act: traversal is blocked before basename; so make a safe input that still includes directories
    DummyRequest.POST = {"blog": "subdir/blog.txt"}
    views.ssrf_lab(DummyRequest())

    assert os.path.basename(opened_paths["path"]) == "blog.txt"
