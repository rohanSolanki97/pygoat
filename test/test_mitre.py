import types

import pytest


# Assumption: Django app module path is "introduction.mitre" as per file_path.
from introduction import mitre


def _make_request(ip: str):
    req = types.SimpleNamespace()
    req.method = "POST"
    req.POST = {"ip": ip}
    return req


def test_mitre_lab_17_api_uses_shell_false_and_argument_list(mocker):
    # Arrange
    request = _make_request("127.0.0.1; echo pwned")

    popen_mock = mocker.Mock()
    popen_mock.communicate.return_value = (
        b"STATE SERVICE\n\n22/tcp open ssh\n",
        b"",
    )

    popen_ctor = mocker.patch("introduction.mitre.subprocess.Popen", return_value=popen_mock)
    mocker.patch("introduction.mitre.JsonResponse", side_effect=lambda payload: payload)

    # Act
    payload = mitre.mitre_lab_17_api(request)

    # Assert
    popen_ctor.assert_called_once()
    args, kwargs = popen_ctor.call_args
    assert args[0] == ["nmap", "127.0.0.1; echo pwned"]
    assert kwargs["shell"] is False
    assert payload["ports"] == ["22/tcp open ssh"]
