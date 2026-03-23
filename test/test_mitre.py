import pytest
from django.test import RequestFactory
from introduction import mitre


@pytest.mark.django_db
class TestMitreLab17ApiCommandInjectionFix:
    def setup_method(self):
        self.factory = RequestFactory()

    def test_mitre_lab_17_api_uses_list_command_and_shell_false(self, monkeypatch):
        executed_commands = {}

        def fake_popen(cmd, shell, stdout, stderr):
            # Assert secure behavior: shell must be False and command must be a list
            assert shell is False
            assert isinstance(cmd, list)
            assert cmd[0] == "nmap"
            executed_commands["cmd"] = cmd

            class FakeProcess:
                def communicate(self_inner):
                    return b"STATE SERVICE\n\n80/tcp open http\n", b""

            return FakeProcess()

        monkeypatch.setattr(mitre.subprocess, "Popen", fake_popen)

        request = self.factory.post("/mitre/17/api", data={"ip": "127.0.0.1"})
        response = mitre.mitre_lab_17_api(request)

        assert response.status_code == 200
        assert executed_commands["cmd"] == ["nmap", "127.0.0.1"]

    def test_command_out_helper_uses_shell_false(self, monkeypatch):
        called = {}

        def fake_popen(cmd, shell, stdout, stderr):
            called["shell"] = shell
            called["cmd"] = cmd

            class FakeProcess:
                def communicate(self_inner):
                    return b"", b""

            return FakeProcess()

        monkeypatch.setattr(mitre.subprocess, "Popen", fake_popen)

        mitre.command_out(["nmap", "example.com"])

        assert called["shell"] is False
        assert called["cmd"] == ["nmap", "example.com"]
