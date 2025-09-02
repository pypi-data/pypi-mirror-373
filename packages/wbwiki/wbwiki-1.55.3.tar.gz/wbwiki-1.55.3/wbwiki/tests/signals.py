from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from wbcore.test.signals import custom_update_kwargs

from wbwiki.factories import WikiArticleRelationshipFactory
from wbwiki.viewsets import ContentObjectWikiArticleModelViewSet


@receiver(custom_update_kwargs, sender=ContentObjectWikiArticleModelViewSet)
def receive_kwargs_content_object(sender, *args, **kwargs):
    if wiki := kwargs.get("obj_factory"):
        WikiArticleRelationshipFactory(wiki=wiki, content_object=wiki)
        return {"content_type": ContentType.objects.get_for_model(wiki).id, "content_id": wiki.id}
    return {}
