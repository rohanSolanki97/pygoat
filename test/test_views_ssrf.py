import os

import pytest
from django.test import RequestFactory

from introduction.views import ssrf_lab


@pytest.mark.django_db
class TestSSRFLab:
    def setup_method(self):
        self.factory = RequestFactory()

    def test_ssrf_lab_rejects_unauthorized_file(self):
        request = self.factory.post("/ssrf/lab", data={"blog": "../../etc/passwd"})
        request.user = type("User", (), {"is_authenticated": True})()

        response = ssrf_lab(request)

        assert response.status_code == 200
        assert b"No blog found" in response.content

    def test_ssrf_lab_allows_only_whitelisted_files(self, mocker, tmp_path, settings):
        dirname = os.path.dirname(__file__)
        safe_file = tmp_path / "safe_blog.txt"
        safe_file.write_text("Safe content")

        mocker.patch("introduction.views.os.path.dirname", return_value=str(tmp_path))

        request = self.factory.post("/ssrf/lab", data={"blog": "safe_blog.txt"})
        request.user = type("User", (), {"is_authenticated": True})()

        response = ssrf_lab(request)

        assert response.status_code == 200
        assert b"Safe content" in response.content
