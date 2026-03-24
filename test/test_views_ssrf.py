import os

import pytest
from django.test import RequestFactory

from introduction import views


@pytest.mark.django_db
class TestSsrfLabFileAccess:
    def setup_method(self):
        self.factory = RequestFactory()

    def test_ssrf_lab_allows_only_whitelisted_files(self, mocker, settings):
        request = self.factory.post("/ssrf/lab", data={"blog": "safe_blog.txt"})
        request.user = mocker.Mock(is_authenticated=True)

        dirname = os.path.dirname(views.__file__)
        safe_path = os.path.join(dirname, "safe_blog.txt")
        mock_open = mocker.mock_open(read_data="SAFE CONTENT")
        mocker.patch("builtins.open", mock_open)

        response = views.ssrf_lab(request)

        assert response.status_code == 200
        assert b"SAFE CONTENT" in response.content

    def test_ssrf_lab_rejects_non_whitelisted_files(self, mocker):
        request = self.factory.post("/ssrf/lab", data={"blog": "../../../etc/passwd"})
        request.user = mocker.Mock(is_authenticated=True)

        mock_open = mocker.patch("builtins.open")

        response = views.ssrf_lab(request)

        assert response.status_code == 200
        assert b"No blog found" in response.content
        mock_open.assert_not_called()
