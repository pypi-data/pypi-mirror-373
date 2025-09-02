from reversion.views import RevisionMixin
from wbcore.viewsets import ModelViewSet, RepresentationViewSet

from wbwriter.models import Publication
from wbwriter.models.publication_models import PublicationParser
from wbwriter.serializers import (
    PublicationModelSerializer,
    PublicationParserRepresentationSerializer,
    PublicationParserSerializer,
    PublicationRepresentationSerializer,
)
from wbwriter.viewsets.buttons import PublicationButtonConfig
from wbwriter.viewsets.display import (
    PublicationDisplayConfig,
    PublicationParserDisplayConfig,
)
from wbwriter.viewsets.titles import PublicationTitleConfig


class PublicationModelViewSet(RevisionMixin, ModelViewSet):
    """Displays all fields of the Publication model."""

    serializer_class = PublicationModelSerializer
    queryset = Publication.objects.all()

    button_config_class = PublicationButtonConfig
    display_config_class = PublicationDisplayConfig
    title_config_class = PublicationTitleConfig

    search_fields = ("title", "author__computed_str", "slug", "content")
    filterset_fields = {
        "title": ["icontains", "exact"],
        "target": ["icontains", "exact"],
        "author": ["exact"],
        "created": ["exact", "lte", "gte"],
        "modified": ["exact", "lte", "gte"],
    }
    ordering_fields = ("title", "author", "created", "modified")

    def get_queryset(self):
        if self.request.user.has_perm("wbwriter.view_publication"):
            qs = Publication.objects.all()

            if content_type := self.request.GET.get("content_type"):
                qs = qs.filter(content_type_id=content_type)

            if object_id := self.request.GET.get("object_id"):
                qs = qs.filter(object_id=object_id)

            return qs.prefetch_related("tags").select_related("parser", "author")

        return Publication.objects.none()


class PublicationParserModelViewSet(ModelViewSet):
    display_config_class = PublicationParserDisplayConfig

    search_fields = ("title", "slug")
    filterset_fields = {
        "title": ["icontains", "exact"],
    }
    ordering_fields = ("title",)

    serializer_class = PublicationParserSerializer
    queryset = PublicationParser.objects.all()

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.profile.is_internal:
            return PublicationParser.objects.all()

        return PublicationParser.objects.none()


class PublicationRepresentationViewSet(RepresentationViewSet):
    """Displays the title and the created date of the Publication model."""

    serializer_class = PublicationRepresentationSerializer
    queryset = Publication.objects.all()

    display_config_class = PublicationDisplayConfig
    button_config_class = PublicationButtonConfig

    search_fields = ("title", "author", "slug", "content")
    filterset_fields = {
        "title": ["icontains", "exact"],
        "target": ["icontains", "exact"],
        "author": ["exact"],
        "created": ["exact", "lte", "gte"],
        "modified": ["exact", "lte", "gte"],
    }
    ordering_fields = ("title", "author", "created", "modified")

    def get_queryset(self):
        if self.request.user.is_superuser or ((person := self.request.user.profile) and person.is_internal):
            return Publication.objects.all()

        return Publication.objects.none()


class PublicationParserRepresentationViewSet(RepresentationViewSet):
    """Displays the title of the PublicationParser model."""

    serializer_class = PublicationParserRepresentationSerializer
    queryset = PublicationParser.objects.all()

    display_config_class = PublicationParserDisplayConfig

    search_fields = ("title", "slug")
    filterset_fields = {
        "title": ["icontains", "exact"],
    }
    ordering_fields = ("title",)

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.profile.is_internal:
            return PublicationParser.objects.all()

        return PublicationParser.objects.none()
