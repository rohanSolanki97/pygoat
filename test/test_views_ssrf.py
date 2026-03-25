import pytest

# Assumption: project root is on PYTHONPATH and module can be imported as "introduction.views"
import introduction.views as views


class _DummyUser:
    is_authenticated = True


class _DummyPost(dict):
    def __getitem__(self, key):
        return super().__getitem__(key)


class _DummyRequest:
    def __init__(self, url: str):
        self.user = _DummyUser()
        self.method = "POST"
        self.POST = _DummyPost({"url": url})


def test_ssrf_lab2_blocks_disallowed_domain_and_does_not_call_requests_get(mocker):
    # Arrange
    requests_get = mocker.patch.object(views.requests, "get")
    render_mock = mocker.patch.object(views, "render", return_value=mocker.Mock())

    req = _DummyRequest(url="http://169.254.169.254/latest/meta-data/")

    # Act
    views.ssrf_lab2(req)

    # Assert: blocked before outbound request
    requests_get.assert_not_called()
    render_mock.assert_called_once()
    _, _, context = render_mock.call_args[0][0], render_mock.call_args[0][1], render_mock.call_args[0][2]
    assert context == {"error": "Disallowed domain"}


def test_ssrf_lab2_allows_allowed_domain_and_calls_requests_get(mocker):
    # Arrange
    response = mocker.Mock()
    response.content = b"ok"
    requests_get = mocker.patch.object(views.requests, "get", return_value=response)
    render_mock = mocker.patch.object(views, "render", return_value=mocker.Mock())

    req = _DummyRequest(url="http://example.com/path")

    # Act
    views.ssrf_lab2(req)

    # Assert
    requests_get.assert_called_once_with("http://example.com/path")
    render_mock.assert_called_once()
