import types
from unittest.mock import Mock

import pytest

# Assumption: tests run with repo root on PYTHONPATH so `introduction` is importable.
import introduction.mitre as mitre


def _make_request(method="POST", post=None, cookies=None):
    req = types.SimpleNamespace()
    req.method = method
    req.POST = post or {}
    req.COOKIES = cookies or {}
    return req


def test_mitre_lab_17_api_uses_subprocess_without_shell_and_list_args(mocker):
    # Arrange
    request = _make_request(method="POST", post={"ip": "127.0.0.1; touch /tmp/pwned"})
    popen_mock = mocker.patch("introduction.mitre.subprocess.Popen")
    process = Mock()
    process.communicate.return_value = (b"STATE SERVICE\n\n22/tcp open ssh\n", b"")
    popen_mock.return_value = process

    # Act
    response = mitre.mitre_lab_17_api(request)

    # Assert: command injection hardening - list args + shell=False
    popen_mock.assert_called_once()
    args, kwargs = popen_mock.call_args
    assert args[0] == ["nmap", "127.0.0.1; touch /tmp/pwned"]
    assert kwargs["shell"] is False
    assert kwargs["stdout"] is mitre.subprocess.PIPE
    assert kwargs["stderr"] is mitre.subprocess.PIPE

    # Response should still be produced
    assert hasattr(response, "status_code")
    assert response.status_code == 200
