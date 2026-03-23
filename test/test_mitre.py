import json
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory

from introduction import mitre


@pytest.mark.django_db
def test_command_out_uses_subprocess_without_shell_and_list_args():
    command = ["nmap", "127.0.0.1"]

    with patch("subprocess.Popen") as mock_popen:
        process_mock = MagicMock()
        process_mock.communicate.return_value = (b"STATE SERVICE\nopen http\n", b"")
        mock_popen.return_value = process_mock

        stdout, stderr = mitre.command_out(command)

        mock_popen.assert_called_once()
        called_args, called_kwargs = mock_popen.call_args

        # Ensure the command passed is a list and shell is disabled
        assert called_args[0] == command
        assert called_kwargs.get("shell") is False
        # Ensure the function returns stdout and stderr unchanged
        assert stdout == b"STATE SERVICE\nopen http\n"
        assert stderr == b""


@pytest.mark.django_db
def test_mitre_lab_17_api_builds_safe_command_and_parses_ports():
    factory = RequestFactory()
    request = factory.post("/mitre/17/api", data={"ip": "127.0.0.1"})
    request.user = User(username="tester")
    request.user.is_authenticated = True

    def fake_command_out(cmd):
        # Critical regression check: IP must be passed as a list argument to nmap
        assert cmd == ["nmap", "127.0.0.1"]
        fake_output = (
            "Some header text\nSTATE SERVICE\nopen http\nclosed ssh\n\nOther footer text".encode(
                "utf-8"
            )
        )
        return fake_output, b""

    with patch("introduction.mitre.command_out", side_effect=fake_command_out):
        response = mitre.mitre_lab_17_api(request)

    assert response.status_code == 200
    body = json.loads(response.content.decode("utf-8"))
    assert body["raw_res"].startswith("Some header text")
    assert body["raw_err"] == ""
    # Ensure the parsed ports list is as expected from the mocked output
    assert body["ports"] == ["open http", "closed ssh"]
