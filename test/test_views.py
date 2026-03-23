import os
import pytest


# Assumption: tests run with project root on PYTHONPATH so `introduction` is importable.
from introduction import views


class _DummyUser:
    def __init__(self, authenticated=True):
        self.is_authenticated = authenticated


class _DummyPost:
    def __init__(self, data):
        self._data = data

    def get(self, key, default=None):
        return self._data.get(key, default)

    def __getitem__(self, key):
        return self._data[key]


class _DummyRequest:
    def __init__(self, method="POST", post=None, authenticated=True):
        self.method = method
        self.user = _DummyUser(authenticated)
        self.POST = _DummyPost(post or {})


def test_ssrf_lab_rejects_non_allowlisted_filename_and_does_not_open(monkeypatch):
    # Arrange
    open_called = {"called": False}

    def fake_open(*args, **kwargs):
        open_called["called"] = True
        raise AssertionError("open() should not be called for non-allowlisted input")

    monkeypatch.setattr(views, "open", fake_open, raising=True)

    render_calls = []

    def fake_render(request, template, context=None):
        render_calls.append((template, context or {}))
        return {"template": template, "context": context or {}}

    monkeypatch.setattr(views, "render", fake_render)

    req = _DummyRequest(post={"blog": "../../etc/passwd"})

    # Act
    resp = views.ssrf_lab(req)

    # Assert
    assert open_called["called"] is False
    assert resp["template"] == "Lab/ssrf/ssrf_lab.html"
    assert resp["context"]["blog"] == "No blog found"


def test_ssrf_lab_allows_only_allowlisted_files(monkeypatch, tmp_path):
    # Arrange: force __file__ dirname to our temp dir and create an allowlisted file.
    safe_file = tmp_path / "safe_blog.txt"
    safe_file.write_text("SAFE CONTENT", encoding="utf-8")

    monkeypatch.setattr(views, "__file__", str(tmp_path / "views.py"), raising=False)

    render_calls = []

    def fake_render(request, template, context=None):
        render_calls.append((template, context or {}))
        return {"template": template, "context": context or {}}

    monkeypatch.setattr(views, "render", fake_render)

    req = _DummyRequest(post={"blog": "safe_blog.txt"})

    # Act
    resp = views.ssrf_lab(req)

    # Assert
    assert resp["template"] == "Lab/ssrf/ssrf_lab.html"
    assert resp["context"]["blog"] == "SAFE CONTENT"
