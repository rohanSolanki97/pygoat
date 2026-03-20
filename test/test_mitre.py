import subprocess

import pytest

# Assumption: tests run with repo root on PYTHONPATH so "introduction" is importable.
from introduction import mitre


def test_mitre_command_out_does_not_use_shell(mocker):
    # Arrange
    popen_mock = mocker.patch("introduction.mitre.subprocess.Popen")
    proc = mocker.Mock()
    proc.communicate.return_value = (b"ok", b"")
    popen_mock.return_value = proc

    # Act
    mitre.command_out(["nmap", "127.0.0.1"])

    # Assert
    popen_mock.assert_called_once()
    _, kwargs = popen_mock.call_args
    assert kwargs["shell"] is False
    assert kwargs["stdout"] is subprocess.PIPE
    assert kwargs["stderr"] is subprocess.PIPE


def test_mitre_lab_17_api_builds_subprocess_args_as_list_not_shell_string(mocker):
    # Arrange
    command_out_mock = mocker.patch("introduction.mitre.command_out", return_value=(b"STATE SERVICE\n\n80/tcp open http\n", b""))

    request = mocker.Mock()
    request.method = "POST"
    request.POST.get.side_effect = lambda k, default=None: {"ip": "127.0.0.1; rm -rf /"}.get(k, default)

    # Avoid depending on Django JsonResponse internals; just ensure we reach it.
    mocker.patch("introduction.mitre.JsonResponse", side_effect=lambda payload: payload)

    # Act
    mitre.mitre_lab_17_api(request)

    # Assert: command_out called with argv list; shell metacharacters are not interpreted by a shell
    command_out_mock.assert_called_once()
    (argv,), _ = command_out_mock.call_args
    assert isinstance(argv, list)
    assert argv[0] == "nmap"
    assert argv[1] == "127.0.0.1; rm -rf /"
