from typing import Optional

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class InEditorTemplateDisplayConfig(DisplayViewConfig):
    """Provides getter methods for the list and instance displays."""

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["uuid", "title"],
                ["style", "template"],
                ["modified", "is_stand_alone_template"],
                [repeat_field(2, "description")],
            ]
        )

    def get_list_display(self) -> Optional[dp.ListDisplay]:
        """Sets up and returns the list display for InEditorTemplate."""
        return dp.ListDisplay(
            fields=[
                dp.Field(key="uuid", label="UUID"),
                dp.Field(key="title", label="Title"),
                dp.Field(key="description", label="Description"),
                # dp.Field(key="style", label="Style"),
                # dp.Field(key="template", label="Template"),
                dp.Field(key="modified", label="Last modified"),
                dp.Field(key="is_stand_alone_template", label="Is a Stand-Alone Template"),
            ],
            formatting=[],
            legends=[],
        )
