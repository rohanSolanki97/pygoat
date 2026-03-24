import types

import pytest

import introduction.views as views


class _FakeQuerySet(list):
    def filter(self, **kwargs):
        return self


def _make_request(count_value: str):
    req = types.SimpleNamespace()
    req.user = types.SimpleNamespace(is_authenticated=True)
    req.method = "POST"
    req.POST = {"count": count_value}
    return req


def test_insec_desgine_lab_rejects_non_integer_count_and_does_not_create_tickets(mocker):
    # Arrange
    mocker.patch.object(views, "authentication_decorator", lambda f: f)

    # tickits.objects.filter(user=...) is used to get existing tickets
    fake_existing = _FakeQuerySet()
    tickits_model = types.SimpleNamespace(objects=types.SimpleNamespace(filter=mocker.Mock(return_value=fake_existing)))
    mocker.patch.object(views, "tickits", tickits_model)

    save_spy = mocker.Mock()
    # If the old behavior existed, it would int("abc") and fall into broad except; we ensure no save occurs.
    mocker.patch.object(views, "render", autospec=True, return_value=types.SimpleNamespace(status_code=200))
    mocker.patch.object(views, "gentckt", autospec=True, return_value="TICKETCODE")

    # Patch constructor used as tickits(user=..., tickit=...)
    def _tickits_ctor(**kwargs):
        return types.SimpleNamespace(save=save_spy)

    mocker.patch.object(views, "tickits", types.SimpleNamespace(objects=tickits_model.objects, **{"__call__": _tickits_ctor}), create=True)

    request = _make_request("not-a-number")

    # Act
    resp = views.insec_desgine_lab(request)

    # Assert
    assert resp.status_code == 200
    save_spy.assert_not_called()


def test_insec_desgine_lab_rejects_zero_or_negative_count(mocker):
    # Arrange
    mocker.patch.object(views, "authentication_decorator", lambda f: f)
    tickits_model = types.SimpleNamespace(objects=types.SimpleNamespace(filter=mocker.Mock(return_value=_FakeQuerySet())))
    mocker.patch.object(views, "tickits", tickits_model)
    render_spy = mocker.patch.object(views, "render", autospec=True, return_value=types.SimpleNamespace(status_code=200))

    request = _make_request("0")

    # Act
    resp = views.insec_desgine_lab(request)

    # Assert
    assert resp.status_code == 200
    # Ensure it returned the error branch introduced by the fix
    assert any("You can have at most 5 tickits" in str(call.args[2].get("error", "")) for call in render_spy.call_args_list)
