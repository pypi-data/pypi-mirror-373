from typing import Optional

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class MetaInformationDisplayConfig(DisplayViewConfig):
    """Provides getter methods for the list and instance displays."""

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [repeat_field(2, "article_type")],
                ["name", "key"],
                ["meta_information_type", "boolean_default"],
            ]
        )

    def get_list_display(self) -> Optional[dp.ListDisplay]:
        """Sets up and returns the list display for MetaInformation."""
        return dp.ListDisplay(
            fields=[
                dp.Field(key="id", label="ID"),
                dp.Field(key="article_type", label="Article Type"),
                dp.Field(key="name", label="Name"),
                dp.Field(key="key", label="Key"),
                dp.Field(key="meta_information_type", label="Meta Information Type"),
                dp.Field(key="boolean_default", label="Boolean Default"),
            ],
            formatting=[],
            legends=[],
        )
