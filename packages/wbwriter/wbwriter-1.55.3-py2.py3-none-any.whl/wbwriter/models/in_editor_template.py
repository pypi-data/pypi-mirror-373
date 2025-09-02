from django.db import models
from wbcore.models import WBModel


class InEditorTemplate(WBModel):
    """A template that the user can choose and configure in the context of
    the WYSIWYG editor.

    In-Editor templates define CSS styles that need to be applied in
    combination with the HTML template, and a number of other
    In-Editor templates that may be nested within the given In-Editor
    template.

    Note that templates can not allow themself to be nested inside them.

    Attributes
    ----------
    uuid : models.CharField
        A unique identifier. The `uuid` must pass as a valid CSS class and
        must less than 256 characters long.

        The regular expression for valid CSS classes: "-?[_a-zA-Z]+[_a-zA-Z0-9-]*"

        See section 4.1.3, second paragraph on
        https://www.w3.org/TR/CSS21/syndata.html#characters
    title : models.CharField
        A human readable title.
    description : models.TextField
        A descriptive text that outlines the use case and possible
        configurations of the template.
    style : models.TextField, optional
        The CSS that is required to properly display the HTML template.
    template : models.TextField
        The HTML that makes up the template.

        TODO: WRITE ABOUT SCHEMA AND CONFIGURATION OPTIONS.
    is_stand_alone_template : models.BooleanField, default=True
        Signifies whether this template can be used without a surrounding
        template (i.e. as root node of the article).
    """

    uuid = models.CharField(max_length=255, unique=True)
    title = models.CharField(
        verbose_name="Title",
        max_length=255,
        help_text="The title should be unique but doesn't need to be.",
    )
    description = models.TextField(
        verbose_name="Description",
        default="",
        help_text="A brief text that describes the use case for this template.",
    )
    style = models.TextField(
        verbose_name="Template CSS",
        default="",
        blank=True,
        null=True,
        help_text="The CSS that styles the templates HTML.",
    )
    template = models.TextField(
        verbose_name="Template HTML",
        default="",
        help_text="The HTML code of the template.",
    )
    # configuration_field_definitions = models.JSONField(
    #     verbose_name="Configuration Field Definitions",
    #     help_text="Maps configuration IDs to field definitions for rendering a form.",
    #     blank=True,
    #     null=True,
    # )
    # configuration_form_layout = models.JSONField(
    #     verbose_name="Configuration Form Layout",
    #     help_text="The field layout of the configuration form.",
    #     blank=True,
    #     null=True,
    # )
    modified = models.DateTimeField(
        verbose_name="Last modification date and time",
        auto_now=True,
        help_text="The last time this template has been edited.",
    )

    is_stand_alone_template = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    @classmethod
    def get_endpoint_basename(self):
        return "wbwriter:in-editor-template"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbwriter:in-editor-template-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{ title }}"
