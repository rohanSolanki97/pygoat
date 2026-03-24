import os
from types import SimpleNamespace

import pytest


# Assumption: tests run with repository root on PYTHONPATH so `introduction` is importable.


def test_ssrf_lab_blocks_non_allowlisted_blog_file(monkeypatch):
    """Regression test for path traversal/SSRF-style local file read: only allow allowlisted files."""
    from introduction import views

    # Ensure render returns the context so we can assert on it
    def fake_render(_request, _template, context=None):
        return context or {}

    monkeypatch.setattr(views, "render", fake_render)

    # If open is called for a disallowed file, the fix is broken.
    def fail_open(*args, **kwargs):
        raise AssertionError("open() should not be called for disallowed blog files")

    monkeypatch.setattr(views, "open", fail_open, raising=False)

    request = SimpleNamespace(
        user=SimpleNamespace(is_authenticated=True),
        method="POST",
        POST={"blog": "../../etc/passwd"},
    )

    result = views.ssrf_lab(request)

    assert result["blog"] == "No blog found"


def test_ssrf_lab_allows_allowlisted_blog_file_and_reads_it(monkeypatch):
    """Ensure allowlisted files are still readable."""
    from introduction import views

    def fake_render(_request, _template, context=None):
        return context or {}

    monkeypatch.setattr(views, "render", fake_render)

    # Make os.path.dirname deterministic
    monkeypatch.setattr(views.os.path, "dirname", lambda _p: "/base")

    opened = {}

    class DummyFile:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return "SAFE CONTENT"

    def fake_open(path, mode):
        opened["path"] = path
        opened["mode"] = mode
        return DummyFile()

    monkeypatch.setattr(views, "open", fake_open, raising=False)

    request = SimpleNamespace(
        user=SimpleNamespace(is_authenticated=True),
        method="POST",
        POST={"blog": "safe_blog.txt"},
    )

    result = views.ssrf_lab(request)

    assert opened["path"] == os.path.join("/base", "safe_blog.txt")
    assert opened["mode"] == "r"
    assert result["blog"] == "SAFE CONTENT"
