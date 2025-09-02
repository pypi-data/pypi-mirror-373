from wbcore.viewsets import ModelViewSet, RepresentationViewSet

from wbwriter.models import MetaInformation
from wbwriter.serializers import MetaInformationModelSerializer
from wbwriter.serializers.meta_information import (
    MetaInformationRepresentationSerializer,
)

from .display import MetaInformationDisplayConfig


class MetaInformationRepresentationViewSet(RepresentationViewSet):
    serializer_class = MetaInformationRepresentationSerializer
    queryset = MetaInformation.objects.all()

    search_fields = ("name", "key")
    filter_fields = {
        "article_type": ["exact"],
        "name": ["icontains", "exact"],
        "key": ["icontains", "exact"],
        "meta_information_type": ["exact"],
    }
    ordering_fields = ("article_type", "name", "key", "meta_information_type")

    def get_queryset(self):
        request = self.request
        user = request.user
        profile = user.profile

        if user.is_superuser or profile.is_internal:
            return MetaInformation.objects.all()

        return MetaInformation.objects.none()


class MetaInformationModelViewSet(ModelViewSet):
    serializer_class = MetaInformationModelSerializer
    queryset = MetaInformation.objects.all()

    display_config_class = MetaInformationDisplayConfig

    search_fields = (
        "name",
        "key",
    )
    filterset_fields = {
        "article_type": ["exact"],
        "name": ["icontains"],
        "key": ["icontains"],
        "meta_information_type": ["exact"],
    }
    ordering_fields = ("article_type", "name", "key", "meta_information_type")
