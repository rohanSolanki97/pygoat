import os

import pytest
from django.test import RequestFactory

from introduction import views


@pytest.mark.django_db
class TestSsrfLabFileAccessRestrictions:
    def setup_method(self):
        self.factory = RequestFactory()

    def test_ssrf_lab_allows_only_whitelisted_files(self, mocker, settings):
        request = self.factory.post("/ssrf/lab", data={"blog": "safe_blog.txt"})
        mocker.patch("os.path.dirname", return_value="/tmp")
        mocker.patch("builtins.open", mocker.mock_open(read_data="SAFE CONTENT"))

        request.user = mocker.Mock(is_authenticated=True)

        response = views.ssrf_lab(request)

        assert response.status_code == 200
        assert b"SAFE CONTENT" in response.content

    def test_ssrf_lab_rejects_non_whitelisted_files(self, mocker):
        request = self.factory.post("/ssrf/lab", data={"blog": "../../etc/passwd"})
        request.user = mocker.Mock(is_authenticated=True)

        response = views.ssrf_lab(request)

        assert response.status_code == 200
        assert b"No blog found" in response.content
