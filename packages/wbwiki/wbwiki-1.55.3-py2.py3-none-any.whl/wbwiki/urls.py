from django.urls import include, path
from wbcore.routers import WBCoreRouter

from wbwiki import viewsets

router = WBCoreRouter()
router.register(r"wikiarticle", viewsets.WikiArticleModelViewSet, basename="wikiarticle")

wiki_router = WBCoreRouter()
wiki_router.register(
    r"relationship",
    viewsets.WikiArticleRelationshipModelViewSet,
    basename="wiki-relationship",
)

content_object_wiki_router = WBCoreRouter()
content_object_wiki_router.register(
    r"contentobjectwiki",
    viewsets.ContentObjectWikiArticleModelViewSet,
    basename="contentobjectwiki",
)

urlpatterns = [
    path("", include(router.urls)),
    path("wiki/<wiki_id>/", include(wiki_router.urls)),
    path("contentobjectwiki/<int:content_type>/<int:content_id>/", include(content_object_wiki_router.urls)),
]
