from datetime import timedelta, datetime, timezone
from django.utils import timezone as django_timezone
from unittest.mock import patch

import pytest

from wbnews.models import News, NewsSource
from faker import Faker

fake = Faker()

@pytest.mark.django_db
class TestSource:
    @pytest.mark.parametrize("news_source__title", ["source1"])
    def test_str(self, news_source):
        assert str(news_source) == f"{news_source.title}"

    def test_source_dict_to_model(self, news_source_factory):
        ns1 = news_source_factory.create()
        ns2 = news_source_factory.create()

        assert NewsSource.source_dict_to_model({"id": ns1.id, "identifier": ns2.identifier}) == ns1 # priority to "id"
        assert NewsSource.source_dict_to_model({"endpoint": ns1.endpoint, "identifier": ns2.identifier}) == ns2 # priority to "identifier"
        assert NewsSource.source_dict_to_model({"endpoint": ns2.endpoint}) == ns2 # exact match on endpoint

        ns1.endpoint = ".*@test.com"
        ns1.save()
        assert NewsSource.source_dict_to_model({"endpoint": "abc@test.com"}) == ns1 # regex match on endpoint

        new_source = NewsSource.source_dict_to_model({"endpoint": "abc@main_source.com", "title": "New Source"})
        assert new_source not in [ns1, ns2]
        assert new_source.endpoint == ".*@main_source\.com"
        assert new_source.title == "New Source"
        assert new_source.author == "Main Source"


@pytest.mark.django_db
class TestNews:
    @pytest.mark.parametrize("news__title", ["new1"])
    def test_str(self, news):
        assert str(news) == f"{news.title} ({news.source.title})"

    def test_mark_as_deplicates_not_in_default_queryset(self, news):
        assert set(News.objects.all()) == {news}

    def test_get_default_guid(self):
        assert News.get_default_guid("This is a title", None) == "this-is-a-title"
        assert News.get_default_guid("This is a title", "http://mylink.com") == "http://mylink.com" # link takes precendence
        assert News.get_default_guid("a" * 24, None, max_length=20) == "a" * 20

    def test_future_news(self, news_factory):
        # ensure a future datetime always default to now
        now = django_timezone.now()
        future_news = news_factory.create(datetime=now + timedelta(days=1))
        assert (future_news.datetime - now).seconds < 1 # we do that to account for clock difference

    @patch("wbnews.models.news.detect_near_duplicates")
    def test_handle_duplicates(self, mock_fct, news_factory):
        val_date = fake.date_time(tzinfo=timezone.utc)
        n0 = news_factory.create(datetime=val_date - timedelta(days=1)) # we exclude this news from the duplicate search
        n1 = news_factory.create(datetime=val_date)
        n2 = news_factory.create(datetime=val_date)
        n3 = news_factory.create(datetime=val_date)

        mock_fct.return_value = [n0.id, n3.id] # n0 is considered as duplicate but does not fall within the specified daterange so it will not be marked
        News.handle_duplicates(val_date, val_date)

        n3.refresh_from_db()
        assert n3.mark_as_duplicate is True
        assert set(News.objects.all()) == {n0, n1, n2}
