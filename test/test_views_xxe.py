import pytest
from django.test import RequestFactory
from xml.dom.pulldom import START_ELEMENT

from introduction import views
from introduction.views import xxe_parse


@pytest.mark.django_db
class TestXXEParse:
    def setup_method(self):
        self.factory = RequestFactory()

    def test_xxe_parse_does_not_resolve_external_entities(self, mocker):
        malicious_xml = """<?xml version='1.0'?>
<!DOCTYPE foo [
  <!ELEMENT foo ANY >
  <!ENTITY xxe SYSTEM "file:///etc/passwd" >]>
<text>&xxe;</text>"""
        request = self.factory.post("/xxe/parse", data=malicious_xml, content_type="application/xml")

        mocked_make_parser = mocker.patch("introduction.views.make_parser")
        mocked_parser = mocker.Mock()
        mocked_make_parser.return_value = mocked_parser

        mocked_parse_string = mocker.patch("introduction.views.parseString")
        mocked_events = [
            (START_ELEMENT, mocker.Mock(tagName="text", toxml=lambda: "<text>safe</text>")),
        ]
        mocked_parse_string.return_value = mocked_events

        mocked_comments = mocker.patch("introduction.views.comments.objects.filter")
        mocked_comments.return_value.update.return_value = 1

        response = xxe_parse(request)

        mocked_parser.setFeature.assert_any_call(views.feature_external_ges, False)
        assert response.status_code == 200

    def test_xxe_parse_updates_comment_with_parsed_text(self, mocker):
        xml = "<text>Hello</text>"
        request = self.factory.post("/xxe/parse", data=xml, content_type="application/xml")

        mocker.patch("introduction.views.make_parser", return_value=mocker.Mock())
        mocked_parse_string = mocker.patch("introduction.views.parseString")
        mocked_events = [
            (START_ELEMENT, mocker.Mock(tagName="text", toxml=lambda: "<text>Hello</text>")),
        ]
        mocked_parse_string.return_value = mocked_events

        mocked_comments = mocker.patch("introduction.views.comments.objects.filter")
        mocked_comments.return_value.update.return_value = 1

        response = xxe_parse(request)

        mocked_comments.assert_called_once_with(id=1)
        mocked_comments.return_value.update.assert_called_once_with(comment="Hello")
        assert response.status_code == 200
