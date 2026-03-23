import pytest
from django.http import HttpRequest
from django.test import RequestFactory
from introduction.mitre import mitre_lab_17_api, command_out


@pytest.mark.django_db
class TestMitreLab17Api:
    def setup_method(self):
        self.factory = RequestFactory()

    def test_command_out_uses_list_and_shell_false(self, mocker):
        mocked_popen = mocker.patch("introduction.mitre.subprocess.Popen")
        process_mock = mocker.Mock()
        process_mock.communicate.return_value = (b"STATE SERVICE\nopen ssh\n", b"")
        mocked_popen.return_value = process_mock

        command = ["nmap", "127.0.0.1"]
        command_out(command)

        mocked_popen.assert_called_once_with(
            command,
            shell=False,
            stdout=mocker.ANY,
            stderr=mocker.ANY,
        )

    def test_mitre_lab_17_api_builds_safe_command_list(self, mocker):
        mocked_command_out = mocker.patch("introduction.mitre.command_out")
        mocked_command_out.return_value = (b"STATE SERVICE\nopen ssh\n", b"")

        request = self.factory.post("/mitre/17/api", data={"ip": "127.0.0.1"})

        response = mitre_lab_17_api(request)

        assert response.status_code == 200
        mocked_command_out.assert_called_once()
        called_args, _ = mocked_command_out.call_args
        assert isinstance(called_args[0], list)
        assert called_args[0][0] == "nmap"
        assert called_args[0][1] == "127.0.0.1"
