# Assumptions: project uses pytest + pytest-django. Tests cover removal of `safe` filter for username.

import pytest
from django.template import Context, Template


def test_lab2_username_is_autoescaped_when_rendered():
    payload = "<img src=x onerror=alert(1)>"
    tpl = Template("Hey {{ username }},")

    rendered = tpl.render(Context({"username": payload}))

    assert "<img" not in rendered
    assert "&lt;img" in rendered


def test_lab2_username_safe_filter_would_render_raw_html_regression_guard():
    payload = "<img src=x onerror=alert(1)>"
    tpl = Template("Hey {{ username|safe }},")

    rendered = tpl.render(Context({"username": payload}))

    assert "<img" in rendered
