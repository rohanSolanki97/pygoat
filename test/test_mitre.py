import subprocess

import pytest

# Assumption: tests run with repository root on PYTHONPATH so `introduction` is importable.
from introduction import mitre as mitre_module


def test_command_out_does_not_use_shell_and_passes_list_args(mocker):
    # Arrange
    popen_mock = mocker.patch.object(subprocess, "Popen")
    proc = mocker.Mock()
    proc.communicate.return_value = (b"out", b"err")
    popen_mock.return_value = proc

    # Act
    out, err = mitre_module.command_out(["nmap", "127.0.0.1"])

    # Assert
    assert (out, err) == (b"out", b"err")
    popen_mock.assert_called_once()
    _, kwargs = popen_mock.call_args
    assert kwargs["shell"] is False
    assert kwargs["stdout"] is subprocess.PIPE
    assert kwargs["stderr"] is subprocess.PIPE
