import os

import pytest
from django.test import RequestFactory

from introduction import views


@pytest.mark.django_db
class TestSsrfLabFileAccessRestriction:
    def setup_method(self):
        self.factory = RequestFactory()

    def test_ssrf_lab_rejects_unauthorized_file(self, monkeypatch):
        request = self.factory.post("/ssrf/lab", data={"blog": "../../etc/passwd"})
        request.user = type("User", (), {"is_authenticated": True})()

        response = views.ssrf_lab(request)

        assert response.status_code == 200
        assert "No blog found" in response.content.decode()

    def test_ssrf_lab_allows_only_whitelisted_files(self, monkeypatch, tmp_path):
        dirname = tmp_path
        safe_file = dirname / "safe_blog.txt"
        safe_file.write_text("safe content")

        def fake_dirname(_):
            return str(dirname)

        monkeypatch.setattr(os.path, "dirname", fake_dirname)

        request = self.factory.post("/ssrf/lab", data={"blog": "safe_blog.txt"})
        request.user = type("User", (), {"is_authenticated": True})()

        response = views.ssrf_lab(request)

        assert response.status_code == 200
        assert "safe content" in response.content.decode()
