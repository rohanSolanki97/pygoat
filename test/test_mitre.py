import pytest
from django.test import RequestFactory

from introduction import mitre


@pytest.mark.django_db
class TestMitreLab17CommandExecution:
    def setup_method(self):
        self.factory = RequestFactory()

    def test_command_out_uses_list_and_shell_false(self, mocker):
        mocked_popen = mocker.patch("introduction.mitre.subprocess.Popen")
        process_mock = mocker.Mock()
        process_mock.communicate.return_value = (b"STATE SERVICE\n\n80/tcp open http\n", b"")
        mocked_popen.return_value = process_mock

        command = ["nmap", "127.0.0.1"]
        mitre.command_out(command)

        mocked_popen.assert_called_once_with(
            command,
            shell=False,
            stdout=mitre.subprocess.PIPE,
            stderr=mitre.subprocess.PIPE,
        )

    def test_mitre_lab_17_api_builds_safe_command_list(self, mocker):
        mocked_command_out = mocker.patch("introduction.mitre.command_out")
        mocked_command_out.return_value = (b"STATE SERVICE\n\n80/tcp open http\n", b"")

        request = self.factory.post("/mitre/17/api", data={"ip": "127.0.0.1"})

        response = mitre.mitre_lab_17_api(request)

        assert response.status_code == 200
        mocked_command_out.assert_called_once_with(["nmap", "127.0.0.1"])
