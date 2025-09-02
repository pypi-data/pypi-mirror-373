from typing import Optional

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class PublicationDisplayConfig(DisplayViewConfig):
    """Provides getter methods for the list and instance displays."""

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["title", "author"],
                ["created", "modified"],
                [repeat_field(2, "teaser_image")],
                [repeat_field(2, "description")],
            ]
        )

    def get_list_display(self) -> Optional[dp.ListDisplay]:
        """Sets up and returns the list display for Publication."""
        return dp.ListDisplay(
            fields=[
                dp.Field(key="title", label="Title"),
                dp.Field(key="author", label="Author"),
                dp.Field(key="modified", label="Modified"),
                dp.Field(key="created", label="Created"),
                dp.Field(key="teaser_image", label="Teaser image"),
            ],
            formatting=[],
            legends=[],
        )


class PublicationParserDisplayConfig(DisplayViewConfig):
    """Provides getter methods for the list and instance displays."""

    def get_instance_display(self) -> Display:
        return create_simple_display([["title", "parser_path"]])

    def get_list_display(self) -> Optional[dp.ListDisplay]:
        """Sets up and returns the list display for Publication Parser."""
        return dp.ListDisplay(
            fields=[
                dp.Field(key="title", label="Title"),
                dp.Field(key="parser_path", label="Parser Path"),
            ],
            formatting=[],
            legends=[],
        )
