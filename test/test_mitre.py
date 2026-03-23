import json
import types

import pytest


def _make_request(*, authenticated=True, method="POST", post_data=None, body=b""):
    user = types.SimpleNamespace(is_authenticated=authenticated)
    return types.SimpleNamespace(method=method, POST=post_data or {}, body=body, user=user)


def test_mitre_lab_17_api_uses_subprocess_without_shell_and_passes_args_list(mocker):
    # Assumption: tests run with project root on PYTHONPATH so `introduction` is importable.
    import introduction.mitre as mitre

    req = _make_request(post_data={"ip": "127.0.0.1"})

    popen_mock = mocker.Mock()
    popen_mock.communicate.return_value = (
        b"STATE SERVICE\n\n22/tcp open ssh\n",
        b"",
    )

    def _popen_side_effect(cmd, shell, stdout, stderr):
        # Secure behavior: shell must be False and command must be a list (no string concatenation).
        assert shell is False
        assert cmd == ["nmap", "127.0.0.1"]
        return popen_mock

    mocker.patch.object(mitre.subprocess, "Popen", side_effect=_popen_side_effect)
    mocker.patch.object(mitre, "JsonResponse", side_effect=lambda payload: payload)

    result = mitre.mitre_lab_17_api(req)

    assert "ports" in result
    assert result["ports"] == ["22/tcp open ssh"]
