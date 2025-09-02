from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from reversion.views import RevisionMixin
from wbcore import viewsets
from wbcore.contrib.authentication.authentication import JWTCookieAuthentication

from wbwiki.models import WikiArticle, WikiArticleRelationship
from wbwiki.serializers import (
    WikiArticleModelSerializer,
    WikiArticleRelationshipModelSerializer,
)

from .buttons import (
    ContentObjectWikiArticleButtonConfig,
    WikiArticleRelationshipButtonConfig,
)
from .display import WikiArticleDisplayConfig, WikiArticleRelationshipDisplayConfig
from .endpoints import (
    ContentObjectWikiArticleEndpointConfig,
    WikiArticleRelationshipEndpointConfig,
)


class WikiArticleModelViewSet(RevisionMixin, viewsets.ModelViewSet):
    queryset = WikiArticle.objects.all()
    serializer_class = WikiArticleModelSerializer
    # search_fields = ("title", "summary", "content", "tags__title")
    filterset_fields = {
        "title": ["icontains"],
        "summary": ["icontains"],
        "tags": ["exact"],
    }

    display_config_class = WikiArticleDisplayConfig

    @action(detail=False, methods=["PATCH"], authentication_classes=[JWTCookieAuthentication])
    def linkwiki(self, request, pk=None):
        content_type_id = request.GET.get("content_type")
        object_id = request.GET.get("content_id")
        wiki_id = request.POST.get("wiki")

        if content_type_id and object_id:
            if wiki_id:
                wiki_relationship, created = WikiArticleRelationship.objects.get_or_create(
                    wiki_id=wiki_id,
                    content_type_id=content_type_id,
                    object_id=object_id,
                )
                if created:
                    message = _("Relationship Item has been added to wiki")
                    _status = status.HTTP_200_OK
                else:
                    message = _("Wiki has already been linked to this Item")
                    _status = status.HTTP_400_BAD_REQUEST
            else:
                message = _("Wiki is mandatory")
                _status = status.HTTP_400_BAD_REQUEST
        else:
            message = _("Relationship Item could not be linked to wiki")
            _status = status.HTTP_400_BAD_REQUEST

        return Response(
            {"__notification": {"title": message}},
            status=_status,
        )


class ContentObjectWikiArticleModelViewSet(WikiArticleModelViewSet):
    endpoint_config_class = ContentObjectWikiArticleEndpointConfig
    button_config_class = ContentObjectWikiArticleButtonConfig

    def get_queryset(self):
        if (content_type_id := self.kwargs.get("content_type")) and (object_id := self.kwargs.get("content_id")):
            return (
                super()
                .get_queryset()
                .filter(relationships__content_type=content_type_id, relationships__object_id=object_id)
            )
        return WikiArticle.objects.none()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        if (content_type_id := self.kwargs.get("content_type")) and (object_id := self.kwargs.get("content_id")):
            WikiArticleRelationship.objects.get_or_create(
                wiki_id=response.data["instance"]["id"],
                content_type_id=content_type_id,
                object_id=object_id,
            )

        return response


class WikiArticleRelationshipModelViewSet(viewsets.ModelViewSet):
    serializer_class = WikiArticleRelationshipModelSerializer
    display_config_class = WikiArticleRelationshipDisplayConfig
    endpoint_config_class = WikiArticleRelationshipEndpointConfig
    button_config_class = WikiArticleRelationshipButtonConfig
    queryset = WikiArticleRelationship.objects.all()
    search_fields = ("computed_str", "content_type__model")
    filterset_fields = {
        "computed_str": ["icontains", "exact"],
    }

    def get_queryset(self):
        return super().get_queryset().filter(wiki__id=self.kwargs["wiki_id"])
