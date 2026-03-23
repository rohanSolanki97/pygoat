import types
from unittest.mock import MagicMock

import pytest

# Assumption: tests run with repo root on PYTHONPATH so `introduction` is importable.
import introduction.mitre as mitre


def test_mitre_lab_17_api_uses_shell_false_and_list_command_to_prevent_injection(mocker):
    # Arrange
    request = types.SimpleNamespace(
        method="POST",
        POST={"ip": "127.0.0.1; touch /tmp/pwned"},
    )

    popen_mock = mocker.patch("introduction.mitre.subprocess.Popen")
    process = MagicMock()
    process.communicate.return_value = (b"STATE SERVICE\n\n80/tcp open http\n", b"")
    popen_mock.return_value = process

    json_response_mock = mocker.patch("introduction.mitre.JsonResponse", side_effect=lambda payload: payload)

    # Act
    result = mitre.mitre_lab_17_api(request)

    # Assert: command is passed as list and shell=False
    popen_mock.assert_called_once()
    args, kwargs = popen_mock.call_args
    assert args[0] == ["nmap", "127.0.0.1; touch /tmp/pwned"]
    assert kwargs["shell"] is False

    # Assert: response still produced
    assert "ports" in result
    json_response_mock.assert_called_once()
