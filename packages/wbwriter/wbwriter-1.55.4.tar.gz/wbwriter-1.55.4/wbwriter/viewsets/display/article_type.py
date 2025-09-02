from typing import Optional

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
)
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class ArticleTypeDisplayConfig(DisplayViewConfig):
    """Provides getter methods for the list and instance displays."""

    def get_instance_display(self) -> Display:
        return create_simple_display([["label"]])

    def get_list_display(self) -> Optional[dp.ListDisplay]:
        """Sets up and returns the list display for ArticleType."""
        return dp.ListDisplay(
            fields=[
                dp.Field(key="id", label="ID"),
                dp.Field(key="label", label="Label"),
                dp.Field(key="slug", label="Slug"),
            ],
            formatting=[],
            legends=[],
        )
