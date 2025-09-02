import re

from django.contrib.postgres.fields import ArrayField
from django.db import models
from wbcore.models import WBModel

from wbnews.models.utils import endpoint_to_author


class NewsSource(WBModel):
    class Type(models.TextChoices):
        RSS = "RSS", "RSS"
        EMAIL = "EMAIL", "EMAIL"

    type = models.CharField(default=Type.RSS, choices=Type.choices, max_length=6)
    title = models.CharField(max_length=255)
    identifier = models.CharField(max_length=255, unique=True, blank=True, null=True)
    tags = ArrayField(models.CharField(max_length=16), default=list, blank=True)
    image = models.URLField(blank=True, null=True)
    description = models.TextField(default="", blank=True)
    author = models.CharField(max_length=255, default="")
    clean_content = models.BooleanField(default=False)
    endpoint = models.CharField(max_length=1024, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"

    def save(self, *args, **kwargs):
        if not self.author and self.endpoint:
            self.author = endpoint_to_author(self.endpoint)
        super().save(*args, **kwargs)

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbnews:sourcerepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{title}}"

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbnews:source"

    @classmethod
    def source_dict_to_model(cls, data: dict):
        sources = NewsSource.objects.all()
        endpoint = data.pop("endpoint", None)
        if "id" in data:
            return sources.get(id=data["id"])
        if type := data.get("type"):
            sources = sources.filter(type=type)
        if identifier := data.get("identifier"):
            sources = sources.filter(identifier=identifier)
        elif endpoint:
            for source in sources:
                match = re.search(source.endpoint, endpoint)
                if source.endpoint == endpoint or match:
                    return source
        if sources.count() == 1:
            return sources.first()
        else:
            if endpoint:
                # Pattern to capture and replace the local part of an email
                pattern = r"^[^@]+"
                # Replace the local part of an email with a wildcard regex
                endpoint = re.sub(pattern, ".*", re.escape(endpoint))
            return NewsSource.objects.create(**data, endpoint=endpoint)
