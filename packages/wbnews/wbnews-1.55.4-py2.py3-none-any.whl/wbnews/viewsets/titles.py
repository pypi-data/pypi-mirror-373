from django.utils.translation import gettext as _
from wbcore.metadata.configs.titles import TitleViewConfig

from wbnews.models import NewsSource


class SourceModelTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Sources")

    def get_instance_title(self):
        if "pk" in self.view.kwargs:
            return _("Source: {source}").format(source=str(self.view.get_object()))
        return _("News Source")


class NewsTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("News Flow")

    def get_instance_title(self):
        if "pk" in self.view.kwargs:
            return str(self.view.get_object())
        return _("News")


class NewsSourceModelTitleConfig(TitleViewConfig):
    def get_list_title(self):
        source = NewsSource.objects.get(id=self.view.kwargs["source_id"])
        return _("News from {source}").format(source=source.title)


class NewsRelationshipTitleConfig(TitleViewConfig):
    def get_list_title(self):
        if self.view and (content_object := self.view.content_object):
            return _("News Article for {}").format(str(content_object))
        return _("News Article")

    def get_instance_title(self):
        try:
            instance = self.view.get_object()
            return str(instance)
        except AssertionError:
            return _("News Article")
