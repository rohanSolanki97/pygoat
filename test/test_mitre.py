import builtins
import types

import pytest

from introduction import mitre


class DummyProcess:
    def __init__(self, stdout=b"", stderr=b""):
        self._stdout = stdout
        self._stderr = stderr

    def communicate(self):
        return self._stdout, self._stderr


class DummySubprocessModule(types.SimpleNamespace):
    pass


@pytest.fixture(autouse=True)
def restore_subprocess(monkeypatch):
    # Ensure we restore the original subprocess after each test
    import subprocess as real_subprocess
    monkeypatch.setattr(mitre, "subprocess", real_subprocess)
    yield
    monkeypatch.setattr(mitre, "subprocess", real_subprocess)


def test_command_out_uses_shell_false_and_passes_list(monkeypatch):
    calls = {}

    def fake_popen(command, shell, stdout, stderr):
        calls["command"] = command
        calls["shell"] = shell
        calls["stdout"] = stdout
        calls["stderr"] = stderr
        return DummyProcess(stdout=b"scan", stderr=b"")

    import subprocess as real_subprocess
    dummy_subprocess = DummySubprocessModule(Popen=fake_popen, PIPE=real_subprocess.PIPE)
    monkeypatch.setattr(mitre, "subprocess", dummy_subprocess)

    # Act: mimic mitre_lab_17_api behaviour
    ip = "127.0.0.1"
    command = ["nmap", ip]
    stdout, stderr = mitre.command_out(command)

    assert calls["shell"] is False
    assert calls["command"] == ["nmap", "127.0.0.1"]
    assert stdout == b"scan"
    assert stderr == b""
