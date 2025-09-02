from wbcore.viewsets import ModelViewSet, RepresentationViewSet

from wbwriter.models import InEditorTemplate
from wbwriter.serializers import (
    InEditorTemplateModelSerializer,
    InEditorTemplateRepresentationSerializer,
)

from .display import InEditorTemplateDisplayConfig


class InEditorTemplateModelViewSet(ModelViewSet):
    ENDPOINT = "wbwriter:in-editor-template-list"
    IDENTIFIER = "wbwriter:in-editor-template"

    serializer_class = InEditorTemplateModelSerializer
    queryset = InEditorTemplate.objects.all()

    display_config_class = InEditorTemplateDisplayConfig

    search_fields = (
        "uuid",
        "title",
        "description",
    )
    filter_fields = {
        "uuid": ["icontains", "exact"],
        "title": ["icontains", "exact"],
        "description": [
            "icontains",
        ],
        "is_stand_alone_template": [
            "exact",
        ],
    }
    ordering_fields = (
        "uuid",
        "title",
        "is_stand_alone_template",
    )


class InEditorTemplateRepresentationViewSet(RepresentationViewSet):
    ENDPOINT = "wbwriter:in-editor-template-list"
    IDENTIFIER = "wbwriter:in-editor-template"

    serializer_class = InEditorTemplateRepresentationSerializer
    queryset = InEditorTemplate.objects.all()

    search_fields = (
        "uuid",
        "title",
        "description",
    )
    filter_fields = {
        "uuid": ["icontains", "exact"],
        "title": ["icontains", "exact"],
        "description": [
            "icontains",
        ],
        "is_stand_alone_template": [
            "exact",
        ],
    }
    ordering_fields = (
        "uuid",
        "title",
        "is_stand_alone_template",
    )
