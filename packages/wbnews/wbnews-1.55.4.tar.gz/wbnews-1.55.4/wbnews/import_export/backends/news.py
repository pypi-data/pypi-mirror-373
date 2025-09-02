import json
from datetime import datetime
from io import BytesIO
from typing import Generator

import feedparser
from django.db.models import QuerySet
from slugify import slugify
from wbcore.contrib.io.backends.abstract import AbstractDataBackend
from wbcore.contrib.io.backends.utils import register

from wbnews.models import NewsSource


@register("News RSS Backend", save_data_in_import_source=True)
class DataBackend(AbstractDataBackend):
    def is_object_valid(self, obj: "NewsSource") -> bool:
        return obj.type == NewsSource.Type.RSS and obj.is_active and obj.endpoint

    def get_default_queryset(self) -> QuerySet["NewsSource"]:
        return NewsSource.objects.filter(type=NewsSource.Type.RSS, is_active=True, endpoint__isnull=False)

    def get_files(
        self, execution_time: datetime, queryset=None, **kwargs
    ) -> Generator[tuple[str, BytesIO], None, None] | None:
        if queryset is not None:
            for source in queryset:
                data = feedparser.parse(source.endpoint)
                if not data.get("bozo_exception"):
                    data["news_source"] = source.id
                    content_file = BytesIO()
                    content_file.write(json.dumps(data).encode())
                    file_name = (
                        f"{slugify(source.title, separator='_')}_rss_file_{datetime.timestamp(execution_time)}.json"
                    )
                    yield file_name, content_file
