from contextlib import suppress

from wbcore.contrib.directory.serializers import PersonRepresentationSerializer
from wbcore.contrib.tags.serializers import TagSerializerMixin
from wbcore.serializers import (
    CharField,
    HyperlinkField,
    ModelSerializer,
    RepresentationSerializer,
    TextAreaField,
    register_resource,
)

from wbwriter.models import Publication, PublicationParser


class PublicationParserRepresentationSerializer(RepresentationSerializer):
    """Serializes the ID and the title of the Publication Parser model."""

    _detail = HyperlinkField(reverse_name="wbwriter:publicationparser-detail")

    class Meta:
        model = PublicationParser
        fields = ("id", "title", "_detail")


class PublicationModelSerializer(TagSerializerMixin, ModelSerializer):
    """Serializes the all fields of the Publication model except for the slug field."""

    description = TextAreaField()
    title = CharField(read_only=True)
    _author = PersonRepresentationSerializer(source="author")
    author = CharField(read_only=True)
    _parser = PublicationParserRepresentationSerializer(source="parser")

    @register_resource()
    def pdf_file(self, instance, request, user):
        with suppress(ValueError):
            if instance.content_file:
                return {"pdf_file": instance.content_file.url}
        return {}

    class Meta:
        model = Publication
        fields = (
            "id",
            "title",
            "target",
            "author",
            "_author",
            "created",
            "modified",
            "content",
            "description",
            "teaser_image",
            "thumbnail_image",
            "tags",
            "_tags",
            "additional_information",
            "_additional_resources",
            "parser",
            "_parser",
            "content_type",
            "object_id",
        )
        ordering = ("-modified", "title", "target")


class PublicationRepresentationSerializer(RepresentationSerializer):
    """Serializes the ID and the title of the Publication model."""

    _detail = HyperlinkField(reverse_name="wbwriter:publication-detail")

    class Meta:
        model = Publication
        fields = ("id", "title", "target", "modified", "_detail")
        ordering = ("-modified", "title", "target")


class PublicationParserSerializer(ModelSerializer):
    class Meta:
        model = PublicationParser
        fields = ("id", "title", "slug", "parser_path")
