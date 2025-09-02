import reversion
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework.reverse import reverse
from wbcore.contrib.tags.models import TagModelMixin
from wbcore.models import WBModel
from wbcore.utils.models import ComplexToStringMixin


@reversion.register()
class WikiArticle(TagModelMixin, WBModel):
    title = models.CharField(max_length=1024)
    summary = models.TextField(default="")
    content = models.TextField(default="")

    def __str__(self) -> str:
        return f"{self.title}"

    @classmethod
    def get_endpoint_basename(cls):
        return "wbwiki:wikiarticle"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbwiki:wikiarticle-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{ title }}"

    def get_tag_detail_endpoint(self):
        return reverse("wbwiki:wikiarticle-detail", [self.id])

    def get_tag_representation(self):
        return self.title

    class Meta:
        verbose_name = "Wiki Article"
        verbose_name_plural = "Wiki Articles"


class WikiArticleRelationship(ComplexToStringMixin, models.Model):
    wiki = models.ForeignKey(to="wbwiki.WikiArticle", related_name="relationships", on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, verbose_name=_("Item Type"), on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(verbose_name=_("Related Item"))
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self) -> str:
        return f"{self.wiki} -> {self.content_object}"

    def compute_str(self) -> str:
        return f"{self.content_object}"

    class Meta:
        verbose_name = _("Wiki Relationship")
        verbose_name_plural = _("Wiki Relationships")
        constraints = [
            models.UniqueConstraint(
                name="unique_wiki_article_relationship", fields=["wiki", "content_type", "object_id"]
            ),
        ]
        indexes = [models.Index(fields=["content_type", "object_id"])]

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{wiki}} -> {{computed_str}}"
