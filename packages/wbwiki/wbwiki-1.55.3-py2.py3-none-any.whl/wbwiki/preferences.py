from django.contrib.contenttypes.models import ContentType
from django.db.utils import ProgrammingError
from dynamic_preferences.registries import global_preferences_registry


def get_allowed_type_wiki_relationship():
    try:
        return global_preferences_registry.manager()["wbwiki__allowed_type_wiki_relationship"]
    except (RuntimeError, ProgrammingError):
        return ContentType.objects.none()
