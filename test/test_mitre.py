import pytest


# Assumption: tests run with project root on PYTHONPATH so `introduction` is importable.
from introduction import mitre


class _DummyPost:
    def __init__(self, data):
        self._data = data

    def get(self, key, default=None):
        return self._data.get(key, default)


class _DummyRequest:
    def __init__(self, method="POST", post=None):
        self.method = method
        self.POST = _DummyPost(post or {})


def test_mitre_lab_17_api_uses_list_command_and_shell_false(monkeypatch):
    captured = {}

    def fake_command_out(command):
        captured["command"] = command
        # Minimal output that satisfies the regex parsing in mitre_lab_17_api
        res = "STATE SERVICE\n\n22/tcp open ssh\n"
        err = ""
        return res.encode(), err.encode()

    monkeypatch.setattr(mitre, "command_out", fake_command_out)

    req = _DummyRequest(post={"ip": "127.0.0.1; echo pwned"})
    resp = mitre.mitre_lab_17_api(req)

    assert captured["command"] == ["nmap", "127.0.0.1; echo pwned"]
    assert resp.status_code == 200


def test_command_out_invokes_subprocess_with_shell_false(monkeypatch):
    popen_calls = {}

    class _FakeProcess:
        def communicate(self):
            return b"", b""

    def fake_popen(command, shell, stdout, stderr):
        popen_calls["command"] = command
        popen_calls["shell"] = shell
        return _FakeProcess()

    monkeypatch.setattr(mitre.subprocess, "Popen", fake_popen)

    mitre.command_out(["nmap", "127.0.0.1"])

    assert popen_calls["command"] == ["nmap", "127.0.0.1"]
    assert popen_calls["shell"] is False
