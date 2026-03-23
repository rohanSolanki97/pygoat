import types


def _make_request(*, method="POST", user_authenticated=True, blog_value=""):
    user = types.SimpleNamespace(is_authenticated=user_authenticated)
    return types.SimpleNamespace(method=method, user=user, POST={"blog": blog_value})


def test_ssrf_lab_blocks_non_allowlisted_file(monkeypatch):
    # Assumption: tests run with project root on PYTHONPATH so `introduction` is importable.
    import introduction.views as views

    def fake_render(request, template, context=None):
        return {"template": template, "context": context or {}}

    def fail_open(*args, **kwargs):
        raise AssertionError("open() should not be called for non-allowlisted file")

    monkeypatch.setattr(views, "render", fake_render)
    monkeypatch.setattr(views, "open", fail_open, raising=True)

    req = _make_request(blog_value="../../etc/passwd")
    resp = views.ssrf_lab(req)

    assert resp["template"] == "Lab/ssrf/ssrf_lab.html"
    assert resp["context"]["blog"] == "No blog found"


def test_ssrf_lab_allows_allowlisted_file_and_reads_contents(monkeypatch):
    import introduction.views as views

    def fake_render(request, template, context=None):
        return {"template": template, "context": context or {}}

    class FakeFile:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return "SAFE CONTENT"

    def fake_open(path, mode):
        assert mode == "r"
        # Ensure no path traversal is introduced by the function.
        assert ".." not in path
        return FakeFile()

    monkeypatch.setattr(views, "render", fake_render)
    monkeypatch.setattr(views, "open", fake_open, raising=True)

    req = _make_request(blog_value="safe_blog.txt")
    resp = views.ssrf_lab(req)

    assert resp["template"] == "Lab/ssrf/ssrf_lab.html"
    assert resp["context"]["blog"] == "SAFE CONTENT"
