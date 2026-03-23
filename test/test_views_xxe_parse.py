import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory

from introduction import views


@pytest.mark.django_db
def test_xxe_parse_disables_external_entities(mocker):
    """Ensure feature_external_ges is explicitly disabled to mitigate XXE."""
    factory = RequestFactory()
    user = User.objects.create_user(username="tester")

    xml_payload = """<?xml version='1.0'?>
<!DOCTYPE foo [
<!ELEMENT text ANY >
<!ENTITY xxe SYSTEM "file:///etc/passwd" >]>
<root><text>&xxe;</text></root>"""

    request = factory.post(
        "/xxe/parse", data=xml_payload, content_type="application/xml"
    )
    request.user = user

    # Wrap the real make_parser so we can assert on setFeature
    real_make_parser = views.make_parser
    parser = real_make_parser()
    set_feature_spy = mocker.spy(parser, "setFeature")

    # Force xxe_parse to use our instrumented parser instance
    mocker.patch("introduction.views.make_parser", return_value=parser)

    views.xxe_parse(request)

    # Verify that external entity processing is disabled
    set_feature_spy.assert_any_call(views.feature_external_ges, False)


@pytest.mark.django_db
def test_xxe_parse_stores_parsed_text_in_comment(mocker, django_db_blocker):
    """Ensure the business behavior (storing parsed <text>) still works."""
    from introduction.models import comments

    with django_db_blocker.unblock():
        comments.objects.all().delete()
        comment = comments.objects.create(name="System", comment="old")

    factory = RequestFactory()
    user = User.objects.create_user(username="tester")

    xml_payload = """<?xml version='1.0'?>
<root><text>Hello World</text></root>"""

    request = factory.post(
        "/xxe/parse", data=xml_payload, content_type="application/xml"
    )
    request.user = user

    # Use real parser but keep the new secure configuration
    mocker.patch("introduction.views.make_parser", wraps=views.make_parser)

    response = views.xxe_parse(request)

    assert response.status_code == 200

    updated = comments.objects.get(id=comment.id)
    assert updated.comment == "Hello World"
