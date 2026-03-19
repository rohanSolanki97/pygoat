# Assumption: tests run from repo root where `introduction` is importable.
from introduction import views


def _mk_tickits_qs(existing_count):
    # Minimal queryset-like object used by the view.
    qs = []
    for i in range(existing_count):
        qs.append(type("T", (), {"tickit": f"T{i}"})())
    return qs


def test_insec_desgine_lab_rejects_non_integer_count(mocker):
    # Arrange
    request = mocker.Mock()
    request.method = "POST"
    request.user = mocker.Mock()

    # Force ValueError in int(...)
    request.POST.get.return_value = "not-an-int"

    tickits_manager = mocker.Mock()
    tickits_manager.filter.return_value = _mk_tickits_qs(existing_count=0)
    mocker.patch.object(views, "tickits", mocker.Mock(objects=tickits_manager))

    render = mocker.patch("introduction.views.render", side_effect=lambda _req, _tpl, ctx=None: ctx or {})

    # Act
    ctx = views.insec_desgine_lab(request)

    # Assert
    assert "error" in ctx
    assert "Invalid ticket count" in ctx["error"]
    render.assert_called()


def test_insec_desgine_lab_rejects_count_exceeding_limit(mocker):
    # Arrange
    request = mocker.Mock()
    request.method = "POST"
    request.user = mocker.Mock()
    request.POST.get.return_value = "3"  # existing 3 + requested 3 => 6 (>5)

    tickits_manager = mocker.Mock()
    tickits_manager.filter.return_value = _mk_tickits_qs(existing_count=3)
    mocker.patch.object(views, "tickits", mocker.Mock(objects=tickits_manager))

    requests_render = mocker.patch("introduction.views.render", side_effect=lambda _req, _tpl, ctx=None: ctx or {})

    # Act
    ctx = views.insec_desgine_lab(request)

    # Assert
    assert "error" in ctx
    assert "at most 5" in ctx["error"]
    requests_render.assert_called()
