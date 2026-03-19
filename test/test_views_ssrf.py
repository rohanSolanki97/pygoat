# Assumptions:
# - The Django app module is named "introduction" and is importable in tests.
# - We avoid Django runtime by monkeypatching render and os.path.

import types

import pytest

import introduction.views as views


def test_ssrf_lab_rejects_non_whitelisted_blog_key(monkeypatch):
    # Arrange
    monkeypatch.setattr(views, "render", lambda _req, _tpl, ctx: ctx)

    request = types.SimpleNamespace(
        user=types.SimpleNamespace(is_authenticated=True),
        method="POST",
        POST={"blog": "../../etc/passwd"},
    )

    # Act
    ctx = views.ssrf_lab(request)

    # Assert
    assert ctx == {"blog": "No blog found"}


def test_ssrf_lab_uses_whitelist_mapping_and_opens_mapped_file(monkeypatch):
    # Arrange
    monkeypatch.setattr(views, "render", lambda _req, _tpl, ctx: ctx)
    monkeypatch.setattr(views.os.path, "dirname", lambda _p: "/base")

    joined = {}

    def fake_join(dirname, filename):
        joined["dirname"] = dirname
        joined["filename"] = filename
        return f"{dirname}/{filename}"

    monkeypatch.setattr(views.os.path, "join", fake_join)

    opened = {}

    class DummyFile:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return "BLOG CONTENT"

    def fake_open(path, mode):
        opened["path"] = path
        opened["mode"] = mode
        return DummyFile()

    monkeypatch.setattr(views, "open", fake_open, raising=False)

    request = types.SimpleNamespace(
        user=types.SimpleNamespace(is_authenticated=True),
        method="POST",
        POST={"blog": "blog1"},
    )

    # Act
    ctx = views.ssrf_lab(request)

    # Assert
    assert joined["dirname"] == "/base"
    assert joined["filename"] == "blog1.txt"
    assert opened["path"] == "/base/blog1.txt"
    assert opened["mode"] == "r"
    assert ctx == {"blog": "BLOG CONTENT"}
