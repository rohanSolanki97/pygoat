import subprocess
from types import SimpleNamespace

import pytest


# Assumption: tests run with project root on PYTHONPATH so `introduction` is importable.
from introduction import mitre


def _fake_request(method: str, ip: str):
    return SimpleNamespace(method=method, POST={"ip": ip})


def test_mitre_lab_17_api_uses_safe_subprocess_invocation_no_shell(mocker):
    # Arrange
    req = _fake_request("POST", "127.0.0.1; echo pwned")

    popen_mock = mocker.patch("introduction.mitre.subprocess.Popen")

    class _Proc:
        def communicate(self):
            # Minimal output that satisfies regex parsing in mitre_lab_17_api
            stdout = b"STATE SERVICE\n\n22/tcp open ssh\n"
            stderr = b""
            return stdout, stderr

    popen_mock.return_value = _Proc()

    # Act
    resp = mitre.mitre_lab_17_api(req)

    # Assert
    assert resp.status_code == 200
    popen_mock.assert_called_once()
    args, kwargs = popen_mock.call_args

    # Previously vulnerable behavior: shell=True and string command concatenation.
    # Fixed behavior: shell=False and argv list.
    assert kwargs.get("shell") is False
    assert args[0] == ["nmap", "127.0.0.1; echo pwned"]
    assert kwargs.get("stdout") is subprocess.PIPE
    assert kwargs.get("stderr") is subprocess.PIPE
