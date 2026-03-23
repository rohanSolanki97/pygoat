import types

import pytest

# Assumption: tests run with project root on PYTHONPATH so `introduction` is importable.
from introduction import mitre


def _make_request(method="POST", post=None, cookies=None):
    req = types.SimpleNamespace()
    req.method = method
    req.POST = post or {}
    req.COOKIES = cookies or {}
    return req


def test_command_out_uses_shell_false(monkeypatch):
    captured = {}

    class _Proc:
        def communicate(self):
            return (b"ok", b"")

    def fake_popen(command, shell, stdout, stderr):
        captured["command"] = command
        captured["shell"] = shell
        return _Proc()

    monkeypatch.setattr(mitre.subprocess, "Popen", fake_popen)

    mitre.command_out(["nmap", "127.0.0.1"])

    assert captured["shell"] is False


def test_mitre_lab_17_api_passes_list_command_not_shell_string(monkeypatch):
    req = _make_request(post={"ip": "127.0.0.1; touch /tmp/pwned"})

    def fake_command_out(command):
        # Secure behavior: command must be a list (shell=False) so injection tokens remain an argument.
        assert isinstance(command, list)
        assert command[0] == "nmap"
        assert command[1] == "127.0.0.1; touch /tmp/pwned"
        return (b"STATE SERVICE\n\n80/tcp open http\n", b"")

    def fake_json_response(payload):
        return payload

    monkeypatch.setattr(mitre, "command_out", fake_command_out)
    monkeypatch.setattr(mitre, "JsonResponse", fake_json_response)

    resp = mitre.mitre_lab_17_api(req)

    assert resp["raw_err"] == ""
    assert resp["ports"] == ["80/tcp open http"]
