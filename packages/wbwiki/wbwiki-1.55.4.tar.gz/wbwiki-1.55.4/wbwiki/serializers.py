from django.utils.translation import gettext as _
from rest_framework import serializers as rf_serializers
from rest_framework.reverse import reverse
from wbcore import serializers
from wbcore.content_type.serializers import (
    ContentTypeRepresentationSerializer,
    DynamicObjectIDRepresentationSerializer,
)
from wbcore.contrib.tags.serializers import TagSerializerMixin

from wbwiki.models import WikiArticle, WikiArticleRelationship

from .preferences import get_allowed_type_wiki_relationship


class WikiArticleRepresentationSerializer(serializers.RepresentationSerializer):
    class Meta:
        model = WikiArticle
        fields = ("id", "title")


class WikiArticleModelSerializer(TagSerializerMixin, serializers.ModelSerializer):
    @serializers.register_only_instance_resource()
    def relationship_resources(self, instance, request, user, **kwargs):
        resources = {"relationship": reverse("wiki:wiki-relationship-list", args=[instance.id], request=request)}
        return resources

    class Meta:
        model = WikiArticle
        fields = (
            "id",
            "title",
            "summary",
            "content",
            "tags",
            "_tags",
            "_additional_resources",
        )


class WikiArticleRelationshipModelSerializer(serializers.ModelSerializer):
    _wiki = WikiArticleRepresentationSerializer(source="wiki")
    _content_type = ContentTypeRepresentationSerializer(
        source="content_type",
        label_key="{{model_title}}",
        allowed_types=get_allowed_type_wiki_relationship(),
    )
    _object_id = DynamicObjectIDRepresentationSerializer(
        source="object_id",
        optional_get_parameters={"content_type": "content_type"},
        depends_on=[{"field": "content_type", "options": {}}],
    )

    @serializers.register_only_instance_resource()
    def additional_resources(self, instance, request, user, view, **kwargs):
        if instance and hasattr(instance.content_object, "get_endpoint_basename"):
            return {
                "object_endpoint": reverse(
                    f"{instance.content_object.get_endpoint_basename()}-detail",
                    args=[instance.object_id],
                    request=request,
                )
            }

    class Meta:
        model = WikiArticleRelationship
        dependency_map = {"object_id": ["content_type"]}
        fields = (
            "id",
            "content_type",
            "_content_type",
            "object_id",
            "_object_id",
            "wiki",
            "_wiki",
            "computed_str",
            "_additional_resources",
        )

    def validate(self, validated_data):
        content_type = validated_data.get("content_type", self.instance.content_type if self.instance else None)
        wiki = validated_data.get("wiki", self.instance.wiki if self.instance else None)
        object_id = validated_data.get("object_id", self.instance.object_id if self.instance else None)

        if content_type and wiki and object_id:
            qs = WikiArticleRelationship.objects.filter(wiki=wiki, content_type=content_type, object_id=object_id)
            qs = qs.exclude(id=self.instance.id) if self.instance else qs
            if qs.exists():
                raise rf_serializers.ValidationError(
                    {"object_id": _("Relationship with wiki: {} already exists").format(wiki)}
                )
        return super().validate(validated_data)
