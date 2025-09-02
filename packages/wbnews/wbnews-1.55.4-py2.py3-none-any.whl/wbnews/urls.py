from django.urls import include, path
from wbcore.routers import WBCoreRouter

from wbnews.viewsets import views

router = WBCoreRouter()
router.register(r"newsrepresentation", views.NewsRepresentationViewSet, basename="newsrepresentation")
router.register(r"newssourcerepresentation", views.SourceRepresentationViewSet, basename="sourcerepresentation")
router.register(r"news", views.NewsModelViewSet, basename="news")
router.register(r"newssource", views.SourceModelViewSet, basename="source")
router.register(r"newsrelationship", views.NewsRelationshipModelViewSet, basename="newsrelationship")


source_router = WBCoreRouter()
source_router.register(r"news", views.NewsSourceModelViewSet, basename="source-news")

urlpatterns = [
    path("", include(router.urls)),
    path("source/<int:source_id>/", include(source_router.urls)),
    path(
        "contentnews/<int:content_type>/<int:content_id>/",
        views.NewsModelViewSet.as_view({"get": "list"}),
        name="news_content_object",
    ),
]
