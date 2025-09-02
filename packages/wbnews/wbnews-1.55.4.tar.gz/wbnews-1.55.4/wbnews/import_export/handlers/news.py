from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

import pytz
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from slugify import slugify
from wbcore.contrib.io.imports import ImportExportHandler

if TYPE_CHECKING:
    from wbnews.models import News


class NewsImportHandler(ImportExportHandler):
    MODEL_APP_LABEL = "wbnews.News"
    model: "News"

    def _deserialize(self, data: Dict[str, Any]):
        from wbnews.models.sources import NewsSource

        data["source"] = NewsSource.source_dict_to_model(data["source"])
        if parsed_datetime := data.get("datetime", None):
            data["datetime"] = pytz.utc.localize(datetime.strptime(parsed_datetime, "%Y-%m-%dT%H:%M:%S"))
        else:
            data["datetime"] = timezone.now()

        data["default_guid"] = self.model.get_default_guid(data["title"], data.get("link", None))
        if guid := data.get("guid", None):
            data["guid"] = slugify(guid)
        else:
            data["guid"] = data["default_guid"]

        # constrained fields to the max allowed size
        if "title" in data:
            data["title"] = data["title"][:500]

        if "link" in data:
            data["link"] = data["link"][:1024]

    def _get_instance(self, data: Dict[str, Any], history: Optional[models.QuerySet] = None, **kwargs) -> models.Model:
        default_guid = data.pop("default_guid")
        instance = None
        try:
            instance = self.model.all_objects.get(models.Q(guid=data["guid"]) | models.Q(guid=default_guid))
        except MultipleObjectsReturned:
            instance = self.model.all_objects.get(models.Q(guid=data["guid"]))
        except ObjectDoesNotExist:
            pass

        if instance:
            self.import_source.log += f"\nFound existing news {instance.id} (guid: {instance.guid})"
        return instance

    def _create_instance(self, data: Dict[str, Any], **kwargs) -> models.Model:
        self.import_source.log += "\nCreate News."
        return self.model.objects.create(**data, import_source=self.import_source)
