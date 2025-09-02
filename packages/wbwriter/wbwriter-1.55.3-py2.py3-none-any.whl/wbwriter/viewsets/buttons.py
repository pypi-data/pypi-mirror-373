from wbcore import serializers
from wbcore.contrib.directory.models import Person
from wbcore.contrib.directory.serializers import (
    InternalUserProfileRepresentationSerializer,
)
from wbcore.contrib.icons import WBIcon
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
)

from wbwriter.models.article import Article


class ArticleModelButtonConfig(ButtonViewConfig):
    def get_custom_list_instance_buttons(self) -> set:
        return {bt.HyperlinkButton(key="preview", label="Preview PDF", icon=WBIcon.VIEW.icon)}

    def get_custom_instance_buttons(self):
        class AssignAuthorSerializer(serializers.Serializer):
            author = serializers.PrimaryKeyRelatedField(queryset=Person.objects.filter_only_internal())
            _author = InternalUserProfileRepresentationSerializer(source="author")

        custom_instance_buttons = {
            bt.ActionButton(key="generate_pdf", label="Generate PDF", icon=WBIcon.DOCUMENT.icon),
            list(self.get_custom_list_instance_buttons())[0],
            bt.WidgetButton(key="publications", label="Publications", icon=WBIcon.NOTEBOOK.icon),
            bt.ActionButton(key="reroll_peer", label="Assign new peer reviewer", icon=WBIcon.REFRESH.icon),
            bt.ActionButton(key="reroll_qa", label="Assign new QA reviewer", icon=WBIcon.REFRESH.icon),
            bt.ActionButton(
                key="reroll_peer_and_qa", label="Assign new peer and QA reviewers", icon=WBIcon.REFRESH.icon
            ),
            bt.ActionButton(
                key="assign_new_author",
                label="Assign another author",
                icon=WBIcon.PEOPLE.icon,
                serializer=AssignAuthorSerializer,
                instance_display=create_simple_display([["author"]]),
            ),
        }
        # Make sure that the "Edit" button only shows up on Status "draft" and
        # only if the article has no author assigned, and is of Type "DDQ".
        if self.view.kwargs.get("pk", None):
            instance = self.view.get_object()
            if (
                instance.status == Article.Status.DRAFT
                and instance.type
                and instance.type.slug == "ddq"
                and not instance.author
            ):
                custom_instance_buttons.add(bt.ActionButton(key="edit", label="Edit", icon=WBIcon.EDIT.icon))

        return custom_instance_buttons


class PublicationButtonConfig(ButtonViewConfig):
    def get_custom_instance_buttons(self):
        return {bt.HyperlinkButton(key="pdf_file", label="PDF", icon=WBIcon.NOTEBOOK.icon)}

    def get_custom_list_instance_buttons(self):
        return self.get_custom_instance_buttons()
