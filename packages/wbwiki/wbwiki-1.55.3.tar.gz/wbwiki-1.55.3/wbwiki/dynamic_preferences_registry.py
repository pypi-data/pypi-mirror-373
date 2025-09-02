from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import ModelMultipleChoicePreference

mailing_section = Section("wbwiki")


@global_preferences_registry.register
class AllowedTypeWikiRelationshipPreference(ModelMultipleChoicePreference):
    section = mailing_section
    name = "allowed_type_wiki_relationship"
    queryset = ContentType.objects.all()
    default = []
    verbose_name = _("Allowed Type Wiki Relationship")
