import pytest
from django.test import RequestFactory
from django.http import HttpRequest

from introduction import views


@pytest.mark.django_db
class TestXXEParse:
    def setup_method(self):
        self.factory = RequestFactory()

    def _build_xml_body(self, inner_text: str) -> bytes:
        xml = f"""<?xml version='1.0' encoding='UTF-8'?>
<!DOCTYPE foo [
  <!ELEMENT foo ANY>
  <!ELEMENT text ANY>
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<foo><text>{inner_text}</text></foo>"""
        return xml.encode("utf-8")

    def test_xxe_parse_does_not_expand_external_entities(self, mocker):
        request: HttpRequest = self.factory.post("/xxe/parse", data=self._build_xml_body("&xxe;"), content_type="application/xml")

        mocked_comments = mocker.patch("introduction.views.comments")
        mocked_query = mocked_comments.objects.filter.return_value

        response = views.xxe_parse(request)

        assert response.status_code == 200
        mocked_comments.objects.filter.assert_called_once_with(id=1)
        mocked_query.update.assert_called_once()
        args, kwargs = mocked_query.update.call_args
        updated_comment = kwargs.get("comment")
        assert "&xxe;" in updated_comment

    def test_xxe_parse_accepts_normal_text(self, mocker):
        body = self._build_xml_body("hello world")
        request: HttpRequest = self.factory.post("/xxe/parse", data=body, content_type="application/xml")

        mocked_comments = mocker.patch("introduction.views.comments")
        mocked_query = mocked_comments.objects.filter.return_value

        response = views.xxe_parse(request)

        assert response.status_code == 200
        mocked_query.update.assert_called_once_with(comment="hello world")
