from typing import Optional

from django.utils.translation import gettext as _
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
    create_simple_section,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

from wbnews.models import NewsRelationship


class SourceDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="title", label=_("Title")),
                dp.Field(key="identifier", label=_("RSS feed")),
                dp.Field(key="author", label=_("Author")),
                dp.Field(key="description", label=_("Description")),
                dp.Field(key="updated", label=_("Last Update")),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["title", "identifier"],
                ["author", "updated"],
                [repeat_field(2, "description")],
                [repeat_field(2, "news_section")],
            ],
            [create_simple_section("news_section", "News", [["news"]], "news", collapsed=False)],
        )


class NewsDisplayConfig(DisplayViewConfig):
    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["datetime", "source"],
                ["language", "link"],
                [repeat_field(2, "summary")],
                [repeat_field(2, "description")],
            ]
        )

    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="datetime", label=_("Datetime")),
                dp.Field(key="title", label=_("Title")),
                dp.Field(key="summary", label=_("Summary")),
                dp.Field(key="description", label=_("Description")),
                # dp.Field(key="tags", label=_("Edited")),
                dp.Field(key="source", label=_("Source")),
                dp.Field(key="language", label=_("Language")),
                dp.Field(key="image_url", label=_("Image")),
            ]
        )


class NewsRelationshipDisplayConfig(DisplayViewConfig):
    def get_instance_display(self) -> Display:
        if self.new_mode:
            return create_simple_display(
                [
                    ["news", "news"],
                    ["important", "sentiment"],
                    ["analysis", "analysis"],
                ]
            )

        return create_simple_display(
            [
                ["news", "news"],
                ["content_type", "object_id"],
                [
                    "important",
                    "sentiment",
                ],
                ["analysis", "analysis"],
                ["summary", "summary"],
                ["description", "description"],
            ]
        )

    def get_list_display(self) -> Optional[dp.ListDisplay]:
        fields = (
            [dp.Field(key="content_object_repr", label=_("Linked Object"))]
            if self.view.object_id is None and self.view.content_type is None
            else []
        )

        fields.extend(
            [
                dp.Field(key="datetime", label=_("Datetime")),
                dp.Field(key="analysis", label=_("Analysis")),
                dp.Field(key="title", label=_("Title")),
                dp.Field(key="summary", label=_("Summary")),
                dp.Field(key="description", label=_("Description")),
                dp.Field(key="important", label=_("Important")),
                dp.Field(key="source", label=_("Source")),
            ]
        )
        return dp.ListDisplay(
            fields=fields,
            formatting=[
                dp.Formatting(
                    column="sentiment",
                    formatting_rules=[
                        dp.FormattingRule(condition=("==", s.value), style={"backgroundColor": s.get_color()})
                        for s in NewsRelationship.SentimentChoices
                    ],
                )
            ],
            legends=[
                dp.Legend(
                    items=[dp.LegendItem(icon=s.get_color(), label=s.label) for s in NewsRelationship.SentimentChoices]
                )
            ],
        )


class NewsSourceDisplayConfig(DisplayViewConfig):
    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [repeat_field(2, "title")],
                ["datetime", "language", "link"],
                [repeat_field(2, "description")],
            ]
        )

    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="datetime", label=_("Datetime")),
                dp.Field(key="title", label=_("Title")),
                dp.Field(key="description", label=_("Description")),
                dp.Field(key="language", label=_("Language")),
                # dp.Field(key="tags", label="_(Edited")),
                # dp.Field(key="link", label="_(Link"))
            ]
        )
