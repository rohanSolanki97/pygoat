import subprocess

import pytest

# Assumption: tests run from repo root where `introduction` is importable.
from introduction import mitre


def test_command_out_does_not_invoke_shell(mocker):
    # Arrange
    popen_mock = mocker.Mock()
    popen_mock.communicate.return_value = (b"ok", b"")
    popen_ctor = mocker.patch("introduction.mitre.subprocess.Popen", return_value=popen_mock)

    # Act
    out, err = mitre.command_out(["nmap", "127.0.0.1"])

    # Assert
    popen_ctor.assert_called_once()
    _, kwargs = popen_ctor.call_args
    assert kwargs["shell"] is False
    assert out == b"ok"
    assert err == b""


def test_mitre_lab_17_api_builds_argument_list_not_shell_string(mocker):
    # Arrange
    request = mocker.Mock()
    request.method = "POST"
    request.POST.get.return_value = "127.0.0.1"

    # Avoid depending on regex output format; just ensure it doesn't crash.
    mocker.patch("introduction.mitre.re.findall", return_value=["STATE SERVICE\n\n22/tcp open ssh\n"])
    mocker.patch("introduction.mitre.JsonResponse", side_effect=lambda payload: payload)

    command_out_mock = mocker.patch(
        "introduction.mitre.command_out",
        return_value=(b"STATE SERVICE\n\n22/tcp open ssh\n", b""),
    )

    # Act
    payload = mitre.mitre_lab_17_api(request)

    # Assert
    command_out_mock.assert_called_once()
    (cmd,), _ = command_out_mock.call_args
    assert cmd == ["nmap", "127.0.0.1"]
    assert "ports" in payload
