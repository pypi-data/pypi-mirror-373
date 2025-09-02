from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class WikiArticleRelationshipEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wiki:wiki-relationship-list",
            args=[self.view.kwargs["wiki_id"]],
            request=self.request,
        )


class ContentObjectWikiArticleEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wiki:contentobjectwiki-list",
            args=[self.view.kwargs["content_type"], self.view.kwargs["content_id"]],
            request=self.request,
        )
