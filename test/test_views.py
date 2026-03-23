import types

import pytest

# Assumption: tests run with project root on PYTHONPATH so `introduction` is importable.
from introduction import views


def _make_request(blog_key: str, authenticated: bool = True):
    user = types.SimpleNamespace(is_authenticated=authenticated)
    req = types.SimpleNamespace()
    req.user = user
    req.method = "POST"
    req.POST = {"blog": blog_key}
    return req


def test_ssrf_lab_rejects_path_traversal_and_does_not_open_file(monkeypatch):
    # Previously vulnerable behavior: user-controlled filename joined and opened.
    # Fixed behavior: only whitelisted keys are allowed; invalid key returns "No blog found".
    opened = {"called": False}

    def fake_open(*args, **kwargs):
        opened["called"] = True
        raise AssertionError("open() should not be called for non-whitelisted blog key")

    monkeypatch.setattr(views, "open", fake_open, raising=True)
    monkeypatch.setattr(views.os.path, "dirname", lambda _: "/base")
    monkeypatch.setattr(views.os.path, "join", lambda a, b: f"{a}/{b}")
    monkeypatch.setattr(views, "render", lambda request, template, context=None: {"template": template, "context": context or {}})

    req = _make_request("../../etc/passwd")
    resp = views.ssrf_lab(req)

    assert opened["called"] is False
    assert resp["template"] == "Lab/ssrf/ssrf_lab.html"
    assert resp["context"]["blog"] == "No blog found"


def test_ssrf_lab_allows_only_whitelisted_blog_keys_and_opens_mapped_filename(monkeypatch):
    captured = {}

    class _File:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return "BLOG_CONTENT"

    def fake_open(path, mode):
        captured["path"] = path
        captured["mode"] = mode
        return _File()

    monkeypatch.setattr(views, "open", fake_open, raising=True)
    monkeypatch.setattr(views.os.path, "dirname", lambda _: "/base")
    monkeypatch.setattr(views.os.path, "join", lambda a, b: f"{a}/{b}")
    monkeypatch.setattr(views, "render", lambda request, template, context=None: {"template": template, "context": context or {}})

    req = _make_request("blog1")
    resp = views.ssrf_lab(req)

    assert captured["path"] == "/base/blog1.txt"
    assert captured["mode"] == "r"
    assert resp["context"]["blog"] == "BLOG_CONTENT"
