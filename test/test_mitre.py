import json
from types import SimpleNamespace

import pytest


# Assumption: tests run with project root on PYTHONPATH so `introduction` is importable.


def _make_request(ip_value: str):
    return SimpleNamespace(method="POST", POST={"ip": ip_value})


def test_mitre_lab_17_api_uses_shell_false_and_argument_list(mocker):
    from introduction import mitre

    request = _make_request("127.0.0.1; touch /tmp/pwned")

    # Ensure the view builds a list command and does not use shell=True.
    def fake_command_out(command):
        assert command == ["nmap", request.POST["ip"]]
        # Return output matching the regex used by the view.
        res = b"STATE SERVICE\n\n22/tcp open ssh\n"
        err = b""
        return res, err

    mocker.patch.object(mitre, "command_out", side_effect=fake_command_out)

    # Also assert subprocess.Popen is called with shell=False inside command_out.
    popen_mock = mocker.patch.object(mitre.subprocess, "Popen")
    process = popen_mock.return_value
    process.communicate.return_value = (b"ok", b"")
    mitre.command_out(["nmap", "127.0.0.1"])
    popen_mock.assert_called_once()
    assert popen_mock.call_args.kwargs.get("shell") is False

    response = mitre.mitre_lab_17_api(request)

    assert response.status_code == 200
    payload = json.loads(response.content.decode("utf-8"))
    assert payload["ports"] == ["22/tcp open ssh"]
