import pytest
from django.http import HttpResponseBadRequest

# NOTE:
# The project uses a Django app named 'introduction'. We import the module directly.
from introduction import mitre


def _make_request_with_post(ip_value):
    class _PostDict(dict):
        def get(self, key, default=None):
            return super().get(key, default)

    class _Req:
        method = "POST"
        POST = _PostDict({"ip": ip_value})

    return _Req()


def test_mitre_lab_17_api_rejects_non_ip_input_as_bad_request(mocker):
    # Arrange: prevent any subprocess execution if validation fails
    mocker.patch.object(mitre, "command_out", autospec=True)
    request = _make_request_with_post("127.0.0.1; rm -rf /")

    # Act
    resp = mitre.mitre_lab_17_api(request)

    # Assert: invalid input is rejected early
    assert isinstance(resp, HttpResponseBadRequest)
    assert resp.status_code == 400


def test_mitre_lab_17_api_calls_command_out_with_list_args_not_shell_string(mocker):
    # Arrange
    request = _make_request_with_post("127.0.0.1")

    # Provide deterministic nmap output for the parsing logic
    fake_stdout = (
        "Starting Nmap\n"
        "STATE SERVICE\n\n"
        "22/tcp open ssh\n"
        "80/tcp open http\n\n"
    ).encode("utf-8")
    fake_stderr = b""

    command_out_spy = mocker.patch.object(
        mitre, "command_out", autospec=True, return_value=(fake_stdout, fake_stderr)
    )

    # Act
    resp = mitre.mitre_lab_17_api(request)

    # Assert: command is passed as argv list (no shell=True string concatenation)
    command_out_spy.assert_called_once()
    called_command = command_out_spy.call_args.args[0]
    assert called_command == ["nmap", "127.0.0.1"]

    # And response includes parsed ports (smoke check)
    assert resp.status_code == 200
    payload = resp.json()
    assert "ports" in payload
    assert "22/tcp open ssh" in payload["ports"]
