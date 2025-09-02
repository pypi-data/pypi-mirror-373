from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext as _


class NewsRelationship(models.Model):
    class SentimentChoices(models.IntegerChoices):
        POSITIVE = 4, _("Positive")
        SLIGHTLY_POSITIVE = 3, _("Slightly Positive")
        SLIGHTLY_NEGATIVE = 2, _("Slightly Negative")
        NEGATIVE = 1, _("Negative")

        def get_color(self):
            colors = {
                "POSITIVE": "#96DD99",
                "SLIGHTLY_POSITIVE": "#FFEE8C",
                "SLIGHTLY_NEGATIVE": "#FF964F",
                "NEGATIVE": "#FF6961",
            }
            return colors[self.name]

    news = models.ForeignKey(to="wbnews.News", related_name="relationships", on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    content_object_repr = models.CharField(max_length=512, default="")

    important = models.BooleanField(null=True, blank=True)
    sentiment = models.PositiveIntegerField(null=True, blank=True, choices=SentimentChoices.choices)
    analysis = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.content_object_repr = str(self.content_object)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.news.title} -> {self.content_object}"

    class Meta:
        verbose_name = "News Relationship"
        indexes = [models.Index(fields=["content_type", "object_id"])]
        constraints = [
            models.UniqueConstraint(name="unique_news_relationship", fields=["content_type", "object_id", "news"])
        ]
