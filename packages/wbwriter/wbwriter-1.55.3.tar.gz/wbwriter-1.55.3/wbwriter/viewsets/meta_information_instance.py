from wbcore.viewsets import ModelViewSet, RepresentationViewSet

from wbwriter.models.meta_information import MetaInformationInstance
from wbwriter.serializers.meta_information import (
    MetaInformationInstanceModelSerializer,
    MetaInformationInstanceRepresentationSerializer,
)

from .display import MetaInformationInstanceDisplayConfig
from .endpoints import MetaInformationInstanceEndpointConfig


class MetaInformationInstanceModelViewSet(ModelViewSet):
    serializer_class = MetaInformationInstanceModelSerializer
    queryset = MetaInformationInstance.objects.all()

    display_config_class = MetaInformationInstanceDisplayConfig
    endpoint_config_class = MetaInformationInstanceEndpointConfig

    search_fields = None
    ordering_fields = ("boolean_value",)

    def get_queryset(self):
        qs = super().get_queryset()
        if article_id := self.kwargs.get("article_id", None):
            qs = qs.filter(article_id=article_id)
        return qs.select_related("meta_information")


class MetaInformationInstanceRepresentationViewSet(RepresentationViewSet):
    serializer_class = MetaInformationInstanceRepresentationSerializer
    queryset = MetaInformationInstance.objects.all()

    filter_fields = {
        # "article": ["exact"],
        "meta_information": ["exact"],
        "boolean_value": ["exact"],
    }
    ordering_fields = ("meta_information__name", "boolean_value")

    def get_queryset(self):
        request = self.request
        user = request.user
        profile = user.profile

        if user.is_superuser or profile.is_internal:
            return MetaInformationInstance.objects.all()

        return MetaInformationInstance.objects.none()
