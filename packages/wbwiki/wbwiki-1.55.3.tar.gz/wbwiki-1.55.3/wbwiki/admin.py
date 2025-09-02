from django.contrib import admin

from wbwiki.models import WikiArticle, WikiArticleRelationship


class WikiArticleRelationshipInline(admin.TabularInline):
    model = WikiArticleRelationship
    extra = 0
    raw_id_fields = ["content_type", "wiki"]


@admin.register(WikiArticleRelationship)
class WikiArticleRelationshipAdmin(admin.ModelAdmin):
    pass


@admin.register(WikiArticle)
class WikiArticleModelAdmin(admin.ModelAdmin):
    inlines = [WikiArticleRelationshipInline]
