import types

import pytest

import introduction.views as views


def _make_request(url_value: str):
    req = types.SimpleNamespace()
    req.user = types.SimpleNamespace(is_authenticated=True)
    req.method = "POST"
    req.POST = {"url": url_value}
    return req


def test_ssrf_lab2_does_not_use_user_supplied_url_for_outbound_request(mocker):
    # Arrange
    mocker.patch.object(views, "authentication_decorator", lambda f: f)
    get_mock = mocker.patch.object(views.requests, "get", autospec=True)
    get_mock.return_value = types.SimpleNamespace(content=b"OK")
    mocker.patch.object(views, "render", autospec=True, return_value=types.SimpleNamespace(status_code=200))

    request = _make_request("http://169.254.169.254/latest/meta-data/")

    # Act
    resp = views.ssrf_lab2(request)

    # Assert
    assert resp.status_code == 200
    get_mock.assert_called_once()
    called_url = get_mock.call_args.args[0]
    assert called_url == "https://safe.example.com/endpoint"
    assert called_url != request.POST["url"]
