from xml.sax.handler import feature_external_ges

# Assumption: tests run from repo root where `introduction` is importable.
from introduction import views


def test_xxe_parse_disables_external_general_entities(mocker):
    # Arrange
    parser = mocker.Mock()
    make_parser = mocker.patch("introduction.views.make_parser", return_value=parser)

    # Avoid real XML parsing; ensure we can observe parser config.
    mocker.patch("introduction.views.parseString", return_value=[])
    request = mocker.Mock()
    request.body = b"<root/>"

    # Avoid DB write and template rendering side effects.
    mocker.patch("introduction.views.comments.objects.filter", return_value=mocker.Mock(update=mocker.Mock()))
    mocker.patch("introduction.views.render", return_value="ok")

    # Act
    result = views.xxe_parse(request)

    # Assert
    assert result == "ok"
    make_parser.assert_called_once()
    parser.setFeature.assert_any_call(feature_external_ges, False)
