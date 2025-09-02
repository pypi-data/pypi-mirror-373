from datetime import date
from typing import Any

from celery import chord, shared_task
from celery.canvas import Signature
from django.conf.global_settings import LANGUAGES
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from slugify import slugify
from wbcore.contrib.ai.llm.decorators import llm
from wbcore.contrib.io.mixins import ImportMixin
from wbcore.models import WBModel

from wbnews.import_export.handlers.news import NewsImportHandler
from wbnews.models.llm.cleaned_news import clean_news_config, summarized_news_config
from wbnews.models.relationships import NewsRelationship
from wbnews.signals import create_news_relationships

from ..utils import detect_near_duplicates


@shared_task
def create_relationship(chain_results: list[list[dict[str, Any]]], news_id: int):
    objs = []
    for relationships in chain_results:
        for relationship in relationships:
            objs.append(NewsRelationship(news_id=news_id, **relationship))
    NewsRelationship.objects.bulk_create(
        objs,
        ignore_conflicts=True,
        unique_fields=["content_type", "object_id", "news"],
    )


class DefaultObjectManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mark_as_duplicate=False)


@llm([clean_news_config, summarized_news_config])
class News(ImportMixin, WBModel):
    errors = {
        "relationship_signal": "using the fetch_new_relationships signal must return a list of tuples, sender: {0} did not."
    }
    import_export_handler_class = NewsImportHandler

    datetime = models.DateTimeField(verbose_name=_("Datetime"), default=timezone.now)
    title = models.CharField(max_length=500, verbose_name=_("Title"))
    guid = models.CharField(max_length=1024, unique=True)
    description = models.TextField(blank=True, verbose_name=_("Description"))
    summary = models.TextField(blank=True, verbose_name=_("Summary"))
    language = models.CharField(max_length=16, choices=LANGUAGES, blank=True, null=True, verbose_name=_("Language"))
    link = models.URLField(max_length=1024, blank=True, null=True, verbose_name=_("Link"))
    tags = ArrayField(models.CharField(max_length=16), default=list)
    enclosures = ArrayField(models.URLField(), default=list)
    source = models.ForeignKey(
        "wbnews.NewsSource", on_delete=models.CASCADE, related_name="news", verbose_name=_("Source")
    )
    image_url = models.URLField(blank=True, null=True)
    mark_as_duplicate = models.BooleanField(default=False, verbose_name=_("Mark as duplicate"))

    objects = DefaultObjectManager()
    all_objects = models.Manager()

    def save(self, *args, **kwargs):
        self.datetime = min(self.datetime, timezone.now())  # we ensure a news is never in the future
        if self.guid is None:
            self.guid = self.get_default_guid(self.title, self.link)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.title} ({self.source.title})"

    def update_and_create_news_relationships(self, synchronous: bool = False):
        """
        This methods fires the signal to fetch the possible relationship to be linked to the news
        """
        tasks = []
        for sender, task_signature in create_news_relationships.send(sender=News, instance=self):
            assert isinstance(task_signature, Signature), self.errors["relationship_signal"].format(sender)
            tasks.append(task_signature)
        if tasks:
            res = chord(tasks, create_relationship.s(self.id))
            if synchronous:
                res.apply()
            else:
                res.apply_async()

    @classmethod
    def get_default_guid(cls, title: str, link: str | None, max_length: int = 1024) -> str:
        if link:
            return link
        return slugify(title)[0:max_length]

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbnews:news-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{title}} ({{datetime}})"

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbnews:news"

    @classmethod
    def handle_duplicates(cls, start: date, end: date, content_label: str = "description", threshold: float = 0.9):
        qs = News.objects.filter(datetime__gte=start, datetime__lte=end)
        data = dict(qs.values_list("id", content_label))
        duplicate_ids = detect_near_duplicates(data, threshold=threshold)
        qs.filter(id__in=duplicate_ids).update(mark_as_duplicate=True)


@receiver(post_save, sender="wbnews.News")
def post_save_create_news_relationships(sender: type, instance: "News", raw: bool, created: bool, **kwargs):
    """
    Post save to lazy create relationship between an instrument and a news upon creation
    """

    if not raw and created:
        instance.update_and_create_news_relationships()
