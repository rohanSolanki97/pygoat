import types

import pytest


# Assumption: tests run with project root on PYTHONPATH so `introduction` is importable.
from introduction import mitre


def test_mitre_lab_17_api_uses_subprocess_without_shell_and_list_command(mocker):
    # Arrange
    request = types.SimpleNamespace(
        method="POST",
        POST={"ip": "127.0.0.1; touch /tmp/pwned"},
    )

    popen_mock = mocker.Mock()
    popen_mock.communicate.return_value = (
        b"STATE SERVICE\n\n22/tcp open ssh\n",
        b"",
    )
    popen_cls = mocker.patch.object(mitre.subprocess, "Popen", return_value=popen_mock)

    mocker.patch.object(mitre, "JsonResponse", side_effect=lambda payload: payload)

    # Act
    result = mitre.mitre_lab_17_api(request)

    # Assert
    popen_cls.assert_called_once()
    (called_command,), called_kwargs = popen_cls.call_args
    assert called_command == ["nmap", "127.0.0.1; touch /tmp/pwned"]
    assert called_kwargs.get("shell") is False

    assert result["ports"] == ["22/tcp open ssh"]
