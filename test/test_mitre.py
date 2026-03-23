import types
from unittest.mock import MagicMock

import pytest

# Assumption: tests run with repo root on PYTHONPATH so "introduction" is importable.
import introduction.mitre as mitre


def _make_request(ip: str):
    req = types.SimpleNamespace()
    req.method = "POST"
    req.POST = {"ip": ip}
    req.COOKIES = {}
    req.user = types.SimpleNamespace(is_authenticated=True)
    return req


def test_mitre_lab_17_api_uses_subprocess_without_shell_and_list_args(mocker):
    # Arrange: prevent real subprocess execution and avoid parsing errors
    popen_mock = mocker.patch("introduction.mitre.subprocess.Popen")
    process = MagicMock()
    process.communicate.return_value = (b"STATE SERVICE\n\n80/tcp open http\n", b"")
    popen_mock.return_value = process

    mocker.patch(
        "introduction.mitre.re.findall",
        return_value=["STATE SERVICE\n\n80/tcp open http\n"],
    )

    request = _make_request("127.0.0.1; touch /tmp/pwned")

    # Act
    mitre.mitre_lab_17_api(request)

    # Assert: command injection mitigation - no shell, args passed as list
    popen_mock.assert_called_once()
    args, kwargs = popen_mock.call_args
    assert args[0] == ["nmap", "127.0.0.1; touch /tmp/pwned"]
    assert kwargs["shell"] is False
