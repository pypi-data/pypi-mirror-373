from django.contrib import admin

from .models import News, NewsRelationship, NewsSource


@admin.register(NewsRelationship)
class NewsRelationshipAdmin(admin.ModelAdmin):
    list_display = ["news", "content_object"]
    autocomplete_fields = ["news"]


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    search_fields = ("title", "description")
    raw_id_fields = ["import_source"]
    autocomplete_fields = [
        "source",
    ]
    list_display = ["title", "language", "tags", "source", "datetime"]

    list_filter = ("source",)

    def get_queryset(self, request):
        return News.all_objects.select_related("source")


@admin.register(NewsSource)
class NewsSourceAdmin(admin.ModelAdmin):
    search_fields = ("type", "title", "identifier", "description", "author", "endpoint")
    list_filter = ("type",)
