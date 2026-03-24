import json
import types

import pytest

import introduction.mitre as mitre


def _make_request(ip: str):
    req = types.SimpleNamespace()
    req.method = "POST"
    req.POST = {"ip": ip}
    return req


def test_mitre_lab_17_api_rejects_non_ipv4_input_and_does_not_invoke_subprocess(mocker):
    # Arrange
    # If the old vulnerable behavior existed, it would attempt to run "nmap <ip>" via shell=True.
    popen_spy = mocker.patch.object(mitre.subprocess, "Popen", autospec=True)
    # Avoid decorator side-effects in unit test
    mocker.patch.object(mitre, "csrf_exempt", lambda f: f)

    request = _make_request("127.0.0.1; cat /etc/passwd")

    # Act
    resp = mitre.mitre_lab_17_api(request)

    # Assert
    assert getattr(resp, "status_code", None) == 400
    # JsonResponse content is bytes; validate error payload
    payload = json.loads(resp.content.decode("utf-8"))
    assert payload["error"] == "Invalid IP address"
    popen_spy.assert_not_called()


def test_command_out_uses_shell_false_and_list_command(mocker):
    # Arrange
    popen_mock = mocker.patch.object(mitre.subprocess, "Popen", autospec=True)
    proc = popen_mock.return_value
    proc.communicate.return_value = (b"ok", b"")

    # Act
    out, err = mitre.command_out(["nmap", "127.0.0.1"])

    # Assert
    assert out == b"ok"
    assert err == b""
    popen_mock.assert_called_once()
    _, kwargs = popen_mock.call_args
    assert kwargs["shell"] is False
