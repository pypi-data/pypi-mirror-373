from wbcore.viewsets import ModelViewSet, RepresentationViewSet

from wbwriter.models import ArticleType
from wbwriter.serializers import (
    ArticleTypeModelSerializer,
    ArticleTypeRepresentationSerializer,
)

from .display import ArticleTypeDisplayConfig


class ArticleTypeModelViewSet(ModelViewSet):
    ENDPOINT = "wbwriter:article-type-list"

    serializer_class = ArticleTypeModelSerializer
    # queryset = ArticleType.objects.all()

    display_config_class = ArticleTypeDisplayConfig

    search_fields = ("label", "slug")
    filter_fields = {"label": ["icontains", "exact"], "slug": ["icontains", "exact"]}
    ordering_fields = ("label",)

    def get_queryset(self):
        request = self.request
        user = request.user
        profile = user.profile

        if user.is_superuser or profile.is_internal:
            return ArticleType.objects.all()
        # TODO: What to do with customers?


class ArticleTypeRepresentationViewSet(RepresentationViewSet):
    serializer_class = ArticleTypeRepresentationSerializer
    queryset = ArticleType.objects.all()

    search_fields = ("label", "slug")
    filter_fields = {"label": ["icontains", "exact"], "slug": ["icontains", "exact"]}
    ordering_fields = ("label",)

    def get_queryset(self):
        request = self.request
        user = request.user
        profile = user.profile

        if user.is_superuser or profile.is_internal:
            return ArticleType.objects.all()

        return ArticleType.objects.none()
