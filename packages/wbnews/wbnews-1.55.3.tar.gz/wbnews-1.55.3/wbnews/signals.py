from django.db.models.signals import ModelSignal

# this signal is gather the news relationship to efficiently handle the insertion.
create_news_relationships = ModelSignal(use_caching=False)
