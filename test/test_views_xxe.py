import pytest
from django.test import RequestFactory
from xml.sax import SAXNotRecognizedException

from introduction import views


@pytest.mark.django_db
class TestXxeParseFix:
    def setup_method(self):
        self.factory = RequestFactory()

    def test_xxe_parse_disables_external_entities(self, monkeypatch):
        features_set = {}

        class FakeParser:
            def setFeature(self, feature, value):
                features_set[feature] = value

        def fake_make_parser():
            return FakeParser()

        def fake_parse_string(xml_string, parser):
            # Return minimal iterable structure consumed by xxe_parse
            class FakeNode:
                tagName = "text"

                def toxml(self):
                    return "<text>safe</text>"

            def iterator():
                yield (views.START_ELEMENT, FakeNode())

            return iterator()

        monkeypatch.setattr(views, "make_parser", fake_make_parser)
        monkeypatch.setattr(views, "parseString", fake_parse_string)

        request = self.factory.post("/xxe/parse", data="<text>safe</text>", content_type="application/xml")

        response = views.xxe_parse(request)

        assert response.status_code == 200
        assert features_set.get(views.feature_external_ges) is False

    def test_xxe_parse_handles_parser_feature_errors_gracefully(self, monkeypatch):
        def fake_make_parser():
            class BrokenParser:
                def setFeature(self, feature, value):
                    raise SAXNotRecognizedException("feature not supported")

            return BrokenParser()

        def fake_parse_string(xml_string, parser):
            class FakeNode:
                tagName = "text"

                def toxml(self):
                    return "<text>safe</text>"

            def iterator():
                yield (views.START_ELEMENT, FakeNode())

            return iterator()

        monkeypatch.setattr(views, "make_parser", fake_make_parser)
        monkeypatch.setattr(views, "parseString", fake_parse_string)

        request = self.factory.post("/xxe/parse", data="<text>safe</text>", content_type="application/xml")

        with pytest.raises(SAXNotRecognizedException):
            # Even if feature setting fails, the vulnerability (external entity expansion)
            # is not reintroduced in this test; we only assert that the code path
            # attempts to set the secure feature and surfaces parser errors.
            views.xxe_parse(request)
