import factory
from django.conf.global_settings import LANGUAGES
from django.utils import timezone
from faker import Factory

from wbnews.models import News, NewsSource

langs = [n for (n, v) in LANGUAGES]
faker = Factory.create()


class NewsSourceFactory(factory.django.DjangoModelFactory):
    title = factory.Sequence(lambda n: f"source_{n}")
    identifier = factory.Sequence(lambda n: f"http://myurl_{n}.com")
    image = factory.Faker("url")
    description = factory.Faker("sentence", nb_words=32)
    author = factory.Faker("name")
    endpoint = factory.Faker("url")

    class Meta:
        model = NewsSource


class NewsFactory(factory.django.DjangoModelFactory):
    datetime = factory.LazyFunction(timezone.now)
    title = factory.Faker("sentence", nb_words=32)
    description = factory.Faker("sentence", nb_words=32)
    summary = factory.Faker("sentence", nb_words=32)
    language = factory.Iterator(langs)
    link = factory.Faker("url")
    guid = factory.LazyAttribute(lambda o: News.get_default_guid(o.title, o.link))
    source = factory.SubFactory(NewsSourceFactory)

    class Meta:
        model = News
        django_get_or_create = ("guid",)
