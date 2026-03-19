# Assumption: tests run from repo root where `introduction` is importable.
from introduction import views


def test_ssrf_lab2_rejects_non_allowlisted_identifier_without_fetching(mocker):
    # Arrange
    request = mocker.Mock()
    request.method = "POST"
    request.POST.get.return_value = "http://169.254.169.254/latest/meta-data"  # classic SSRF target

    requests_get = mocker.patch("introduction.views.requests.get")
    render = mocker.patch("introduction.views.render", side_effect=lambda _req, _tpl, ctx=None: ctx or {})

    # Act
    ctx = views.ssrf_lab2(request)

    # Assert
    requests_get.assert_not_called()
    render.assert_called()
    assert "error" in ctx
    assert "Invalid URL identifier" in ctx["error"]


def test_ssrf_lab2_fetches_only_allowlisted_url(mocker):
    # Arrange
    request = mocker.Mock()
    request.method = "POST"
    request.POST.get.return_value = "service1"

    response = mocker.Mock()
    response.content = b"hello"
    requests_get = mocker.patch("introduction.views.requests.get", return_value=response)
    mocker.patch("introduction.views.render", side_effect=lambda _req, _tpl, ctx=None: ctx or {})

    # Act
    ctx = views.ssrf_lab2(request)

    # Assert
    requests_get.assert_called_once()
    (safe_url,), _ = requests_get.call_args
    assert safe_url == "https://api.example.com/service1"
    assert ctx["response"] == "hello"
