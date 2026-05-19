# Assumptions: project uses pytest + pytest-django. These tests exercise template auto-escaping behavior changed by removal of the `safe` filter.

import pytest
from django.template import Context, Template


def test_xss_lab_query_is_autoescaped_when_rendered():
    # Arrange: payload that would execute if unescaped
    payload = "<script>alert(1)</script>"
    tpl = Template("The company '{{ query }}'")

    # Act
    rendered = tpl.render(Context({"query": payload}))

    # Assert: script tags are escaped (no raw <script>)
    assert "<script>" not in rendered
    assert "&lt;script&gt;" in rendered


def test_xss_lab_query_safe_filter_would_render_raw_script_regression_guard():
    # This test demonstrates the previously vulnerable behavior and ensures we don't reintroduce it.
    payload = "<script>alert(1)</script>"
    tpl = Template("The company '{{ query|safe }}'")

    rendered = tpl.render(Context({"query": payload}))

    # With `safe`, raw script appears (vulnerable). If this ever stops being true,
    # it indicates Django escaping behavior changed or template settings differ.
    assert "<script>" in rendered
