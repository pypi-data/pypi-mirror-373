from django.utils.translation import gettext as _
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display import (
    Display,
    Inline,
    Layout,
    Page,
    Style,
    create_simple_display,
)
from wbcore.metadata.configs.display.instance_display.operators import default
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class WikiArticleRelationshipDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> dp.ListDisplay:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="content_type", label="Item Type"),
                dp.Field(key="computed_str", label="Related Item"),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display([["content_type", "object_id"]])


class WikiArticleDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> dp.ListDisplay:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="title", label="Title"),
                dp.Field(key="summary", label="Summary"),
                dp.Field(key="tags", label="Tags"),
            ]
        )

    def _get_custom_instance_display(self) -> Display:
        return Display(
            pages=[
                Page(
                    title=_("Main Information"),
                    layouts={
                        default(): Layout(
                            grid_template_areas=[["title"], ["summary"], ["tags"], ["content"]],
                            grid_template_columns=[
                                "minmax(min-content, 1fr)",
                            ],
                        ),
                    },
                ),
                Page(
                    title=_("Relationship"),
                    layouts={
                        default(): Layout(
                            grid_template_areas=[["relationship_key"]],
                            inlines=[Inline(key="relationship_key", endpoint="relationship")],
                            grid_template_columns=[
                                "minmax(min-content, 1fr)",
                            ],
                            grid_auto_rows=Style.MIN_CONTENT,
                        ),
                    },
                ),
            ]
        )

    def get_instance_display(self) -> Display:
        display = (
            self._get_custom_instance_display()
            if "pk" in self.view.kwargs
            else create_simple_display([["title", "summary", "tags", "content"]])
        )

        return display
