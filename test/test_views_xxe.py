# Assumptions:
# - The Django app module is named "introduction" and is importable in tests.
# - We avoid Django runtime by monkeypatching parseString and make_parser.

import types

import pytest

import introduction.views as views


def test_xxe_parse_disables_external_general_entities(monkeypatch):
    # Arrange
    calls = []

    class DummyParser:
        def setFeature(self, feature, value):
            calls.append((feature, value))

    monkeypatch.setattr(views, "make_parser", lambda: DummyParser())

    # parseString is called with parser=parser; return an iterable to satisfy for-loop.
    monkeypatch.setattr(views, "parseString", lambda *_args, **_kwargs: [])

    # Avoid DB update and template rendering
    monkeypatch.setattr(views, "comments", types.SimpleNamespace(objects=types.SimpleNamespace(filter=lambda **_kw: types.SimpleNamespace(update=lambda **_kw2: 1))))
    monkeypatch.setattr(views, "render", lambda *_args, **_kwargs: "rendered")

    request = types.SimpleNamespace(user=types.SimpleNamespace(is_authenticated=True), body=b"<text>hi</text>")

    # Act
    result = views.xxe_parse(request)

    # Assert
    assert result == "rendered"
    assert (views.feature_external_ges, False) in calls
    assert (views.feature_external_ges, True) not in calls
