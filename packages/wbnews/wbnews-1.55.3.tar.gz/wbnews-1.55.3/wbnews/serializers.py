from django.utils.translation import gettext_lazy as _
from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers
from wbcore.content_type.serializers import (
    ContentTypeRepresentationSerializer,
    DynamicObjectIDRepresentationSerializer,
)

from .models import News, NewsRelationship, NewsSource


class SourceRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbnews:source-detail")

    class Meta:
        model = NewsSource
        fields = ("id", "title", "_detail")


class SourceModelSerializer(wb_serializers.ModelSerializer):
    title = wb_serializers.CharField(read_only=True, label=_("Title"))
    identifier = wb_serializers.CharField(read_only=True, label=_("Identifier"))
    image = wb_serializers.CharField(read_only=True)
    description = wb_serializers.CharField(read_only=True, label=_("Description"))
    author = wb_serializers.CharField(read_only=True, label=_("Author"))
    updated = wb_serializers.DateTimeField(read_only=True, label=_("Updated"))

    @wb_serializers.register_resource()
    def news(self, instance, request, user):
        return {"news": reverse("wbnews:source-news-list", args=[instance.id], request=request)}

    class Meta:
        model = NewsSource
        fields = ("id", "title", "identifier", "image", "description", "author", "updated", "_additional_resources")


class NewsRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbnews:news-detail")

    class Meta:
        model = News
        fields = ("id", "datetime", "title", "_detail")


class NewsModelSerializer(wb_serializers.ModelSerializer):
    _source = SourceRepresentationSerializer(source="source")
    image_url = wb_serializers.ImageURLField()

    @wb_serializers.register_resource()
    def open_link(self, instance, request, user):
        if instance.link:
            return {"open_link": instance.link}
        return {}

    # link = wb_serializers.URL()
    class Meta:
        model = News
        fields = (
            "id",
            "datetime",
            "title",
            "description",
            "summary",
            "link",
            "language",
            "image_url",
            "source",
            "_source",
            "_additional_resources",
        )


class NewsRelationshipModelSerializer(wb_serializers.ModelSerializer):
    source = wb_serializers.PrimaryKeyCharField(read_only=True)
    _source = SourceRepresentationSerializer(source="source")
    title = wb_serializers.TextField(read_only=True, label=_("Title"))
    description = wb_serializers.TextField(read_only=True, label=_("Description"))
    summary = wb_serializers.TextField(read_only=True, label=_("Summary"))
    datetime = wb_serializers.DateTimeField(read_only=True, label=_("Date"))
    _content_type = ContentTypeRepresentationSerializer(source="content_type")
    object_id = wb_serializers.CharField(label="Linked Object", required=False)
    _object_id = DynamicObjectIDRepresentationSerializer(
        content_type_field_name="content_type",
        source="object_id",
        optional_get_parameters={"content_type": "content_type"},
        depends_on=[{"field": "content_type", "options": {}}],
        filter_params={
            "is_security": True
        },  # TODO needs to find a way to not create a dependency to the wbfdm module here
    )
    news = wb_serializers.PrimaryKeyRelatedField(
        queryset=News.objects.all(), read_only=lambda view: not view.new_mode, label=_("News")
    )
    _news = NewsRepresentationSerializer(source="news")

    def validate(self, data):
        if view := self.context["view"]:
            if view.object_id:
                data["object_id"] = view.object_id
            if view.content_type:
                data["content_type"] = view.content_type
        return super().validate(data)

    class Meta:
        model = NewsRelationship
        read_only_fields = (
            "content_object_repr",
            "datetime",
            "title",
            "description",
            "summary",
            "content_type",
            "_content_type",
        )
        fields = (
            "id",
            "news",
            "_news",
            "content_object_repr",
            "datetime",
            "sentiment",
            "analysis",
            "important",
            "title",
            "description",
            "summary",
            "source",
            "_source",
            "content_type",
            "_content_type",
            "object_id",
            "_object_id",
            "_additional_resources",
        )
