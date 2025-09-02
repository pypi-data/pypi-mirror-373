from wbcore.serializers import HyperlinkField, ModelSerializer, RepresentationSerializer

from wbwriter.models import InEditorTemplate


class InEditorTemplateModelSerializer(ModelSerializer):
    """Serializes the complete InEditorTemplate model."""

    class Meta:
        model = InEditorTemplate
        fields = (
            "id",
            "uuid",
            "title",
            "description",
            "style",
            "template",
            "modified",
            "is_stand_alone_template",
        )


class InEditorTemplateRepresentationSerializer(RepresentationSerializer):
    """Serializes the minimum number of fields of the InEditorTemplate model
    that are needed to identify a template."""

    _detail = HyperlinkField(reverse_name="wbwriter:in-editor-template-detail")

    class Meta:
        model = InEditorTemplate
        fields = (
            "id",
            "uuid",
            "title",
            "description",
            "is_stand_alone_template",
            "_detail",
        )
