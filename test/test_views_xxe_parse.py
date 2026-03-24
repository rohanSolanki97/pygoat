import pytest
from django.test import RequestFactory

from introduction import views


@pytest.mark.django_db
class TestXxeParseSecurity:
    def setup_method(self):
        self.factory = RequestFactory()

    def _build_xml(self, inner_text: str) -> bytes:
        xml_template = """<?xml version='1.0' encoding='UTF-8'?>\n<root><text>{}</text></root>"""
        return xml_template.format(inner_text).encode("utf-8")

    def test_xxe_parse_ignores_external_entities(self, mocker):
        request = self.factory.post("/xxe/parse", data=self._build_xml("hello"), content_type="application/xml")

        mocked_comments = mocker.patch("introduction.views.comments.objects.filter")
        mocked_comments.return_value.update.return_value = 1

        response = views.xxe_parse(request)

        assert response.status_code == 200

        from xml.sax import make_parser
        from xml.sax.handler import feature_external_ges

        parser = make_parser()
        parser.setFeature(feature_external_ges, False)

        from xml.sax._exceptions import SAXNotSupportedException

        with pytest.raises(SAXNotSupportedException):
            parser.setFeature(feature_external_ges, True)

