import types

import pytest

# Assumption: tests run with project root on PYTHONPATH, so "introduction" is importable.
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
    popen_mock = mocker.Mock()
    popen_mock.communicate.return_value = (
        b"STATE SERVICE\n\n22/tcp open ssh\n",
        b"",
    )
    popen_ctor = mocker.patch.object(mitre.subprocess, "Popen", return_value=popen_mock)

    # Act
    resp = mitre.mitre_lab_17_api(request)

    # Assert: command injection mitigation - no shell, args passed as list
    popen_ctor.assert_called_once()
    called_args, called_kwargs = popen_ctor.call_args
    assert called_args[0] == ["nmap", "127.0.0.1; touch /tmp/pwned"]
    assert called_kwargs["shell"] is False
    assert called_kwargs["stdout"] is mitre.subprocess.PIPE
    assert called_kwargs["stderr"] is mitre.subprocess.PIPE

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["ports"] == ["22/tcp open ssh"]
