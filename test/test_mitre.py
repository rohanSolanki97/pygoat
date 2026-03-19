import subprocess

import pytest

# Assumption: tests run from repo root and "introduction" is importable as a package.
from introduction import mitre


def test_command_out_invokes_subprocess_without_shell(mocker):
    # Arrange
    popen_spy = mocker.patch("introduction.mitre.subprocess.Popen")
    process = mocker.Mock()
    process.communicate.return_value = (b"ok", b"")
    popen_spy.return_value = process

    # Act
    out, err = mitre.command_out(["nmap", "127.0.0.1"])

    # Assert
    assert (out, err) == (b"ok", b"")
    popen_spy.assert_called_once()
    _, kwargs = popen_spy.call_args
    assert kwargs["shell"] is False
    assert kwargs["stdout"] == subprocess.PIPE
    assert kwargs["stderr"] == subprocess.PIPE


def test_mitre_lab_17_api_builds_argument_list_not_shell_string(mocker):
    # Arrange
    command_out_spy = mocker.patch(
        "introduction.mitre.command_out", return_value=(b"STATE SERVICE\n\n80/tcp open http\n", b"")
    )

    class _Req:
        method = "POST"

        class POST:
            @staticmethod
            def get(key):
                assert key == "ip"
                # Previously could be exploited via shell metacharacters; now must be passed as a single arg.
                return "127.0.0.1; echo pwned"

    # Act
    resp = mitre.mitre_lab_17_api(_Req())

    # Assert
    (cmd,), _ = command_out_spy.call_args
    assert isinstance(cmd, list)
    assert cmd[0] == "nmap"
    assert cmd[1] == "127.0.0.1; echo pwned"
    assert hasattr(resp, "content")
