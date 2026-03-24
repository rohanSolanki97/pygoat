import subprocess
from types import SimpleNamespace

import pytest


# Assumption: tests run with repository root on PYTHONPATH so `introduction` is importable.


def test_mitre_lab_17_api_uses_list_command_and_shell_false(monkeypatch):
    """Regression test for command injection fix: ensure subprocess is invoked with shell=False and argv list."""
    from introduction import mitre

    captured = {}

    class DummyProcess:
        def communicate(self):
            # Minimal nmap-like output to satisfy regex parsing in mitre_lab_17_api
            stdout = b"STATE SERVICE\n\n80/tcp open http\n"
            stderr = b""
            return stdout, stderr

    def fake_popen(cmd, shell, stdout, stderr):
        captured["cmd"] = cmd
        captured["shell"] = shell
        return DummyProcess()

    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    request = SimpleNamespace(method="POST", POST={"ip": "127.0.0.1; echo pwned"})

    response = mitre.mitre_lab_17_api(request)

    assert captured["shell"] is False
    assert captured["cmd"] == ["nmap", "127.0.0.1; echo pwned"]
    # Ensure response is a JsonResponse-like object
    assert hasattr(response, "content")
