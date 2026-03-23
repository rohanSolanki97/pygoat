import json
import types

import pytest


def _make_request(*, method="POST", user_authenticated=True, post=None, body=b""):
    user = types.SimpleNamespace(is_authenticated=user_authenticated)
    return types.SimpleNamespace(method=method, user=user, POST=post or {}, body=body)


def test_mitre_lab_17_api_uses_shell_false_and_list_command(monkeypatch):
    # Assumption: tests run with project root on PYTHONPATH so `introduction` is importable.
    import introduction.mitre as mitre

    called = {}

    def fake_popen(command, shell, stdout, stderr):
        called["command"] = command
        called["shell"] = shell

        class Proc:
            def communicate(self):
                # Must match regex in mitre_lab_17_api: "STATE SERVICE.*\n\n"
                out = b"STATE SERVICE\n\n80/tcp open http\n"
                err = b""
                return out, err

        return Proc()

    monkeypatch.setattr(mitre.subprocess, "Popen", fake_popen)

    req = _make_request(post={"ip": "127.0.0.1; echo pwned"})
    resp = mitre.mitre_lab_17_api(req)

    assert called["shell"] is False
    assert called["command"] == ["nmap", "127.0.0.1; echo pwned"]
    payload = json.loads(resp.content.decode("utf-8"))
    assert payload["ports"] == ["80/tcp open http"]
