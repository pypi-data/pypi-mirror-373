from wbcore import filters as wb_filters

from wbnews.models import News, NewsRelationship, NewsSource


class NewsFilterSet(wb_filters.FilterSet):
    datetime = wb_filters.DateTimeRangeFilter(method=wb_filters.DateRangeFilter.base_date_range_filter_method)

    class Meta:
        model = News
        fields = {"title": ["icontains"], "source": ["exact"], "language": ["exact"]}


class NewsRelationshipFilterSet(wb_filters.FilterSet):
    datetime = wb_filters.DateTimeRangeFilter(method="filter_datetime")
    title = wb_filters.CharFilter(lookup_expr="icontains")
    description = wb_filters.CharFilter(lookup_expr="icontains")
    summary = wb_filters.CharFilter(lookup_expr="icontains")
    source = wb_filters.ModelMultipleChoiceFilter(
        label="Source",
        queryset=NewsSource.objects.all(),
        endpoint=NewsSource.get_representation_endpoint(),
        value_key=NewsSource.get_representation_value_key(),
        label_key=NewsSource.get_representation_label_key(),
        method="filter_source",
    )
    content_type = wb_filters.CharFilter(method="fake_filter", hidden=True)
    object_id = wb_filters.CharFilter(method="fake_filter", hidden=True)

    def filter_datetime(self, queryset, name, value):
        if value:
            return queryset.filter(news__datetime__gte=value.lower, news__datetime__lte=value.upper)
        return queryset

    def filter_source(self, queryset, name, value):
        if value:
            return queryset.filter(news__source__in=value)
        return queryset

    class Meta:
        model = NewsRelationship
        fields = {
            "analysis": ["icontains"],
            "sentiment": ["exact"],
            "important": ["exact"],
        }
