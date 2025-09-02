from wbcore.serializers import ModelSerializer, RepresentationSerializer

from wbwriter.models import MetaInformation, MetaInformationInstance

from .article_type import ArticleTypeRepresentationSerializer


class MetaInformationModelSerializer(ModelSerializer):
    """Serializes all fields of the MetaInformation model."""

    _article_type = ArticleTypeRepresentationSerializer(source="article_type", many=True)

    class Meta:
        model = MetaInformation
        fields = (
            "id",
            "article_type",
            "_article_type",
            "name",
            "key",
            "meta_information_type",
            "boolean_default",
        )


class MetaInformationRepresentationSerializer(RepresentationSerializer):
    """Serializes the name and the key of the MetaInformation model."""

    class Meta:
        model = MetaInformation
        fields = ("id", "name", "key")


class MetaInformationInstanceModelSerializer(ModelSerializer):
    # from wbwriter.serializers import ArticleFullModelSerializer

    # _article = ArticleFullModelSerializer(source="article")
    _meta_information = MetaInformationRepresentationSerializer(source="meta_information")

    class Meta:
        model = MetaInformationInstance
        read_only_fields = ("meta_information",)
        fields = (
            "id",
            "meta_information",
            "_meta_information",
            # "article",
            # "_article",
            "boolean_value",
        )


class MetaInformationInstanceRepresentationSerializer(RepresentationSerializer):
    # from wbwriter.serializers import ArticleFullModelSerializer

    # _article = ArticleFullModelSerializer(source="article")
    _meta_information = MetaInformationRepresentationSerializer(source="meta_information")

    class Meta:
        model = MetaInformationInstance
        fields = (
            "id",
            "meta_information",
            "_meta_information",
            # "article",
            # "_article",
            "boolean_value",
        )
