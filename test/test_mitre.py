import types

import pytest

# Assumption: Django app module path is "introduction.mitre" based on source file location.
import introduction.mitre as mitre


def test_mitre_lab_17_api_uses_safe_subprocess_args_and_shell_false(mocker):
    # Arrange
    request = types.SimpleNamespace(
        method="POST",
        POST={"ip": "127.0.0.1; touch /tmp/pwned"},
    )

    popen_mock = mocker.patch("introduction.mitre.subprocess.Popen")
    process = mocker.Mock()
    process.communicate.return_value = (b"STATE SERVICE\n\n80/tcp open http\n", b"")
    popen_mock.return_value = process

    json_response_mock = mocker.patch("introduction.mitre.JsonResponse", side_effect=lambda payload: payload)

    # Act
    result = mitre.mitre_lab_17_api(request)

    # Assert
    popen_mock.assert_called_once()
    args, kwargs = popen_mock.call_args
    assert args[0] == ["nmap", "127.0.0.1; touch /tmp/pwned"]
    assert kwargs["shell"] is False
    assert "ports" in result
    assert result["ports"] == ["80/tcp open http"]
    json_response_mock.assert_called_once()
