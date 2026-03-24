import pytest
from django.test import RequestFactory

from introduction import views


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
        safe_file = tmp_path / "safe_blog.txt"
        safe_file.write_text("Safe content")

        monkeypatch.setattr(views.os.path, "dirname", lambda _path: str(tmp_path))

        request = self.factory.post("/ssrf/lab", data={"blog": "safe_blog.txt"})
        request.user = type("User", (), {"is_authenticated": True})()

        response = views.ssrf_lab(request)

        assert response.status_code == 200
        content = response.content.decode()
        assert "Safe content" in content
