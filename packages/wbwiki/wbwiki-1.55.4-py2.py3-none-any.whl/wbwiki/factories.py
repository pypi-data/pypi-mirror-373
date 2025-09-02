import factory
from django.contrib.contenttypes.models import ContentType

from wbwiki.models import WikiArticle, WikiArticleRelationship


class WikiArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WikiArticle

    title = factory.Faker("pystr")
    summary = factory.Faker("pystr")
    content = factory.Faker("pystr")


class AbstractPublicationFactory(factory.django.DjangoModelFactory):
    object_id = factory.SelfAttribute("content_object.id")
    content_type = factory.LazyAttribute(lambda o: ContentType.objects.get_for_model(o.content_object))

    class Meta:
        exclude = ["content_object"]
        abstract = True


class WikiArticleRelationshipFactory(AbstractPublicationFactory):
    class Meta:
        model = WikiArticleRelationship

    wiki = factory.SubFactory(WikiArticleFactory)
    content_object = factory.SubFactory("wbcore.contrib.authentication.factories.AuthenticatedPersonFactory")
    # content_object = factory.SubFactory(WikiArticleFactory)
