from typing import Optional

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
)
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class MetaInformationInstanceDisplayConfig(DisplayViewConfig):
    """Provides getter methods for the list and instance displays."""

    def get_instance_display(self) -> Display:
        return create_simple_display([["meta_information", "boolean_value"]])

    def get_list_display(self) -> Optional[dp.ListDisplay]:
        """Sets up and returns the list display for MetaInformationInstance."""
        return dp.ListDisplay(
            fields=[
                # dp.Field(key="id", label="ID"),
                # dp.Field(key="article", label="Article"),
                dp.Field(key="meta_information", label="Meta Information"),
                dp.Field(key="boolean_value", label="Boolean Value"),
            ],
            formatting=[],
            legends=[],
        )
