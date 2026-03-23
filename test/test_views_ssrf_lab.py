import os

import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory

from introduction import views


@pytest.mark.django_db
def test_ssrf_lab_allows_only_whitelisted_files(monkeypatch):
    factory = RequestFactory()
    user = User.objects.create_user(username="tester")

    def make_request(filename: str):
        req = factory.post("/ssrf/lab", data={"blog": filename})
        req.user = user
        return req

    # Attempt directory traversal / arbitrary path 
    request = make_request("../../secret.txt")
    response = views.ssrf_lab(request)

    assert response.status_code == 200
    assert b"No blog found" in response.content

    # Allowed file name should be read from a safe path using the exact basename
    request = make_request("safe_blog.txt")

    def fake_open(path, mode="r", *args, **kwargs):
        assert os.path.basename(path) == "safe_blog.txt"
        from io import StringIO

        return StringIO("Safe content")

    with monkeypatch.context() as m:
        m.setattr("builtins.open", fake_open)
        response = views.ssrf_lab(request)

    assert response.status_code == 200
    assert b"Safe content" in response.content


@pytest.mark.django_db
def test_ssrf_lab_rejects_non_whitelisted_even_if_file_exists(monkeypatch, tmp_path):
    factory = RequestFactory()
    user = User.objects.create_user(username="tester")

    # Create a real file with a non-whitelisted name to ensure whitelist is enforced
    malicious_name = "malicious.txt"
    malicious_file = tmp_path / malicious_name
    malicious_file.write_text("Should not be readable")

    request = factory.post("/ssrf/lab", data={"blog": malicious_name})
    request.user = user

    def pass_through_open(path, mode="r", *args, **kwargs):
        return open(malicious_file, mode, *args, **kwargs)

    with monkeypatch.context() as m:
        m.setattr("builtins.open", pass_through_open)
        response = views.ssrf_lab(request)

    assert response.status_code == 200
    # Even though file exists, name is not in allowed_files, so it must be denied
    assert b"No blog found" in response.content
