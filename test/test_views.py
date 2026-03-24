import pytest
from django.test import RequestFactory

from introduction import views


@pytest.mark.django_db
class TestXXEParse:
    def setup_method(self):
        self.factory = RequestFactory()

    def test_xxe_parse_does_not_expand_external_entities(self, monkeypatch):
        # Arrange: XML with an external entity; with feature_external_ges disabled,
        # the parsed text should contain the literal entity reference, not its contents.
        xml = """<?xml version='1.0'?>
<!DOCTYPE foo [ <!ELEMENT foo ANY >
<!ENTITY xxe SYSTEM "file:///etc/passwd" >]>
<foo><text>&xxe;</text></foo>"""

        request = self.factory.post("/xxe/parse", data=xml, content_type="application/xml")

        # Avoid touching the real database layer used by comments.objects.filter().update()
        class DummyQS:
            def update(self, **kwargs):
                self.updated = kwargs
                return 1

        captured = {}

        class DummyManager:
            def filter(self, **kwargs):
                captured["filter_kwargs"] = kwargs
                return DummyQS()

        class DummyComments:
            objects = DummyManager()

        monkeypatch.setattr(views, "comments", DummyComments)

        # Act
        response = views.xxe_parse(request)

        # Assert: request handled successfully
        assert response.status_code == 200
        # And update was called with some comment text
        assert "filter_kwargs" in captured
        assert captured["filter_kwargs"] == {"id": 1}


@pytest.mark.django_db
class TestSsrfLabFileAccess:
    def setup_method(self):
        self.factory = RequestFactory()

    def test_ssrf_lab_rejects_unauthorized_filename(self):
        request = self.factory.post("/ssrf/lab", data={"blog": "../../secret.txt"})
        request.user = type("User", (), {"is_authenticated": True})()

        response = views.ssrf_lab(request)

        assert response.status_code == 200
        content = response.content.decode()
        assert "No blog found" in content

    def test_ssrf_lab_allows_safe_filename_and_reads_file(self, tmp_path, monkeypatch):
        # Create a temporary directory and file structure that mimics the expected layout
        safe_file = tmp_path / "safe_blog.txt"
        safe_file.write_text("Safe content")

        # Monkeypatch os.path.dirname to return tmp_path for this test so that
        # ssrf_lab looks for files inside our temporary directory
        monkeypatch.setattr(views.os.path, "dirname", lambda _path: str(tmp_path))

        request = self.factory.post("/ssrf/lab", data={"blog": "safe_blog.txt"})
        request.user = type("User", (), {"is_authenticated": True})()

        response = views.ssrf_lab(request)

        assert response.status_code == 200
        content = response.content.decode()
        assert "Safe content" in content
