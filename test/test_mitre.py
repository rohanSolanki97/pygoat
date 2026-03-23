import json
import types

import pytest


# Assumption: tests run with project root on PYTHONPATH so `introduction` is importable.


def _make_request(method="POST", post=None, cookies=None, body=b"", user_authenticated=True):
    class _User:
        is_authenticated = user_authenticated

    req = types.SimpleNamespace()
    req.method = method
    req.POST = post or {}
    req.COOKIES = cookies or {}
    req.body = body
    req.user = _User()
    req.META = {}
    req.headers = {}
    return req


def test_mitre_lab_17_api_uses_shell_false_and_list_command(mocker):
    from introduction import mitre

    # Arrange
    req = _make_request(post={"ip": "127.0.0.1; touch /tmp/pwned"})

    popen_mock = mocker.Mock()
    proc_mock = mocker.Mock()
    proc_mock.communicate.return_value = (
        b"STATE SERVICE\n\n22/tcp open ssh\n",
        b"",
    )
    popen_mock.return_value = proc_mock
    mocker.patch.object(mitre.subprocess, "Popen", popen_mock)

    # Avoid brittle parsing failures by controlling re.findall output
    mocker.patch.object(mitre.re, "findall", return_value=["STATE SERVICE\n\n22/tcp open ssh\n"])

    # Act
    resp = mitre.mitre_lab_17_api(req)

    # Assert: command is passed as argv list and shell is disabled
    popen_mock.assert_called_once()
    args, kwargs = popen_mock.call_args
    assert args[0] == ["nmap", "127.0.0.1; touch /tmp/pwned"]
    assert kwargs.get("shell") is False

    assert hasattr(resp, "content")
    payload = json.loads(resp.content.decode("utf-8"))
    assert payload["ports"] == ["22/tcp open ssh"]
