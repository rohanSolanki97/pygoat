import json
import types

import pytest

# Assumption: project root is on PYTHONPATH and module can be imported as "introduction.mitre"
import introduction.mitre as mitre


class _DummyPost(dict):
    def get(self, key, default=None):
        return super().get(key, default)


class _DummyRequest:
    def __init__(self, method="POST", post=None):
        self.method = method
        self.POST = _DummyPost(post or {})


def test_mitre_lab_17_api_rejects_missing_ip_returns_400(mocker):
    # Arrange
    req = _DummyRequest(method="POST", post={})

    # Act
    resp = mitre.mitre_lab_17_api(req)

    # Assert
    assert resp.status_code == 400
    assert b"IP address is required." in resp.content


def test_mitre_lab_17_api_rejects_invalid_ip_returns_400(mocker):
    # Arrange: injection-like payload should be rejected by regex validation
    req = _DummyRequest(method="POST", post={"ip": "127.0.0.1; rm -rf /"})

    # Act
    resp = mitre.mitre_lab_17_api(req)

    # Assert
    assert resp.status_code == 400
    assert b"Invalid IP address provided." in resp.content


def test_mitre_lab_17_api_uses_subprocess_without_shell_and_argument_list(mocker):
    # Arrange
    popen_spy = mocker.patch.object(mitre.subprocess, "Popen")

    # Make communicate() return bytes that satisfy the parsing logic in mitre_lab_17_api
    # pattern = "STATE SERVICE.*\n\n" and then [0][14:-2].split('\n')
    stdout = b"STATE SERVICE\n\n22/tcp open ssh\n\n"
    stderr = b""
    proc = mocker.Mock()
    proc.communicate.return_value = (stdout, stderr)
    popen_spy.return_value = proc

    req = _DummyRequest(method="POST", post={"ip": "127.0.0.1"})

    # Act
    resp = mitre.mitre_lab_17_api(req)

    # Assert: subprocess called with list args and shell=False (no shell injection)
    popen_spy.assert_called_once()
    called_args, called_kwargs = popen_spy.call_args
    assert called_args[0] == ["nmap", "127.0.0.1"]
    assert called_kwargs.get("shell") is False

    # And endpoint still returns JSON
    assert resp.status_code == 200
    payload = json.loads(resp.content.decode("utf-8"))
    assert "raw_res" in payload
    assert "raw_err" in payload
    assert "ports" in payload
