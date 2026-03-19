# Assumptions:
# - The Django app module is named "introduction" and is importable in tests.
# - These tests focus only on the security fix: subprocess is invoked with shell=False and argv list.

import types

import pytest

import introduction.mitre as mitre


def test_mitre_command_out_uses_shell_false(monkeypatch):
    # Arrange
    captured = {}

    class DummyProc:
        def communicate(self):
            return (b"ok", b"")

    def fake_popen(cmd, shell, stdout, stderr):
        captured["cmd"] = cmd
        captured["shell"] = shell
        captured["stdout"] = stdout
        captured["stderr"] = stderr
        return DummyProc()

    monkeypatch.setattr(mitre.subprocess, "Popen", fake_popen)

    # Act
    out, err = mitre.command_out(["nmap", "127.0.0.1"])

    # Assert
    assert (out, err) == (b"ok", b"")
    assert captured["shell"] is False
    assert captured["cmd"] == ["nmap", "127.0.0.1"]


def test_mitre_lab_17_api_builds_argv_list_not_shell_string(monkeypatch):
    # Arrange
    # Avoid needing Django; we only validate the argv passed to subprocess.
    captured = {}

    class DummyProc:
        def communicate(self):
            # Provide output matching the regex used in the view.
            return (b"STATE SERVICE\n\n80/tcp open http\n", b"")

    def fake_popen(cmd, shell, stdout, stderr):
        captured["cmd"] = cmd
        captured["shell"] = shell
        return DummyProc()

    monkeypatch.setattr(mitre.subprocess, "Popen", fake_popen)

    # Make regex parsing deterministic
    monkeypatch.setattr(mitre.re, "findall", lambda pattern, text, flags=None: ["STATE SERVICE\n\n80/tcp open http\n"])

    # Replace JsonResponse with a simple passthrough to avoid Django dependency
    monkeypatch.setattr(mitre, "JsonResponse", lambda payload: payload)

    request = types.SimpleNamespace(method="POST", POST={"ip": "127.0.0.1; rm -rf /"})

    # Act
    resp = mitre.mitre_lab_17_api(request)

    # Assert
    # Previously vulnerable behavior would have built a single string "nmap <ip>" and used shell=True.
    assert captured["shell"] is False
    assert captured["cmd"][0] == "nmap"
    assert captured["cmd"][1] == "127.0.0.1; rm -rf /"
    assert isinstance(captured["cmd"], list)
    assert "ports" in resp
