from unittest import mock
from unittest.mock import patch, PropertyMock

import pytest

from wbnews.import_export.parsers.emails.utils import EmlContentParser


class TestEmlContentParser:

    @pytest.fixture
    def content_parser(self):
        parser = EmlContentParser(b'')
        parser.message = {"From": "main@acme.com"}
        return parser

    @patch.object(EmlContentParser, "text", new_callable=PropertyMock)
    def test_source_from_in_text(self, mock_text, content_parser):
        mock_text.return_value = "some random email content with a From field From: source name <email@test.com> and the rest of the email"
        assert content_parser.source == {"title": "Source Name", "endpoint": "email@test.com", "type": "EMAIL"}

    @patch.object(EmlContentParser, "text", new_callable=PropertyMock)
    def test_source_from_in_text(self, mock_text, content_parser):
        mock_text.return_value = "some random email content without a From field"
        assert content_parser.source == {"title": "Acme.Com", "endpoint": "main@acme.com", "type": "EMAIL"}
