import types
from unittest.mock import MagicMock

import pytest

# Assumption: tests run with repo root on PYTHONPATH so "introduction" is importable.
import introduction.mitre as mitre


def test_mitre_lab_17_api_uses_subprocess_without_shell_and_list_args(mocker):
    # Arrange
    request = types.SimpleNamespace(
        method="POST",
        POST={"ip": "127.0.0.1; touch /tmp/pwned"},
    )

    popen_mock = mocker.patch("introduction.mitre.subprocess.Popen")
    process_mock = MagicMock()
    process_mock.communicate.return_value = (
        b"STATE SERVICE\n\n22/tcp open ssh\n",
        b"",
    )
    popen_mock.return_value = process_mock

    # Act
    resp = mitre.mitre_lab_17_api(request)

    # Assert: secure behavior - shell=False and args passed as list (no shell parsing)
    popen_mock.assert_called_once()
    args, kwargs = popen_mock.call_args
    assert args[0] == ["nmap", "127.0.0.1; touch /tmp/pwned"]
    assert kwargs["shell"] is False
    assert kwargs["stdout"] is mitre.subprocess.PIPE
    assert kwargs["stderr"] is mitre.subprocess.PIPE

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["ports"] == ["22/tcp open ssh"]
