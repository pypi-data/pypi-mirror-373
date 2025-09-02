from django.utils.translation import gettext as _
from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers
from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
)

from wbwiki.models import WikiArticle
from wbwiki.serializers import WikiArticleRepresentationSerializer


class WikiArticleRelationshipButtonConfig(ButtonViewConfig):
    def get_custom_instance_buttons(self):
        return self.get_custom_list_instance_buttons()

    def get_custom_list_instance_buttons(self):
        return {
            bt.WidgetButton(key="object_endpoint", label="{{computed_str}}", icon=WBIcon.CLIPBOARD.icon),
        }


class ContentObjectWikiArticleButtonConfig(ButtonViewConfig):
    def get_custom_buttons(self):
        if not self.view.kwargs.get("pk", None):

            class WikiArticleSerializer(wb_serializers.Serializer):
                wiki = wb_serializers.PrimaryKeyRelatedField(
                    queryset=WikiArticle.objects.all(),
                    required=True,
                    label=_("Wiki"),
                )
                _wiki = WikiArticleRepresentationSerializer(source="wiki")

            return {
                bt.ActionButton(
                    identifiers=("wbwiki:wikiarticle",),
                    method=RequestType.PATCH,
                    endpoint=f"{reverse('wbwiki:wikiarticle-linkwiki', args=[], request=self.request)}?content_type={self.view.kwargs['content_type']}&content_id={self.view.kwargs['content_id']}",
                    action_label=_("Add Existing Wiki"),
                    title=_("Add Existing Wiki"),
                    label=_("Add Existing Wiki"),
                    icon=WBIcon.LINK.icon,
                    serializer=WikiArticleSerializer,
                    description_fields="<p>Link item to Existing Wiki</p><p>Are you sure you want to proceed?</p>",
                    instance_display=create_simple_display([["wiki"]]),
                )
            }
        return {}
