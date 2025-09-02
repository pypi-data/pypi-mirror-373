from django.contrib.contenttypes.models import ContentType
from django.db.models import Case, Q, QuerySet, Value, When
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from reversion.views import RevisionMixin
from wbcore.contrib.authentication.authentication import JWTCookieAuthentication
from wbcore.contrib.directory.models import Person
from wbcore.contrib.i18n.viewsets import ModelTranslateMixin
from wbcore.contrib.icons import WBIcon
from wbcore.utils.views import CloneMixin
from wbcore.viewsets import ModelViewSet, RepresentationViewSet

from wbwriter.filters.article import ArticleFilter
from wbwriter.models import Article, can_access_article
from wbwriter.models.article import (
    DependantArticle,
    can_administrate_article,
    can_edit_article_author,
    can_edit_article_content,
    can_edit_article_meta_data,
    can_edit_article_type,
    generate_pdf_as_task,
)
from wbwriter.serializers import (
    ArticleFullModelSerializer,
    ArticleRepresentionSerializer,
    DependantArticleModelSerializer,
)

from .buttons import ArticleModelButtonConfig
from .display import ArticleDisplayConfig, DependantArticleDisplayConfig
from .endpoints import (
    DependantArticleEndpointViewConfig,
    ReviewerArticleModelEndpointConfig,
)
from .titles import ReviewerArticleTitleConfig


class ArticleRepresentionViewSet(RepresentationViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleRepresentionSerializer


class DependantArticleModelViewSet(ModelViewSet):
    queryset = DependantArticle.objects.all()
    serializer_class = DependantArticleModelSerializer
    display_config_class = DependantArticleDisplayConfig
    endpoint_config_class = DependantArticleEndpointViewConfig

    def get_queryset(self) -> QuerySet[DependantArticle]:
        queryset = super().get_queryset()
        if article_id := self.kwargs.get("article_id", None):
            queryset = queryset.filter(article_id=article_id)

        if used_article_id := self.kwargs.get("used_article_id", None):
            queryset = queryset.filter(dependant_article_id=used_article_id)

        return queryset.select_related("article", "dependant_article")


class ArticleInstancePermissionMixin:
    @cached_property
    def profile(self):
        user = self.request.user
        return user.profile

    @cached_property
    def instance(self) -> Article | None:
        if "pk" in self.kwargs:
            return self.get_object()

    @cached_property
    def can_edit_article_author(self) -> bool:
        if self.instance:
            return can_edit_article_author(self.instance, self.request.user)
        return False

    @cached_property
    def can_edit_article_meta_data(self) -> bool:
        if self.instance:
            return can_edit_article_meta_data(self.instance, self.request.user)
        return False

    @cached_property
    def can_edit_article_type(self) -> bool:
        return can_edit_article_type(self.instance, self.request.user)

    @cached_property
    def can_edit_article_content(self) -> bool:
        if self.instance:
            return can_edit_article_content(self.instance, self.request.user)
        return False

    @cached_property
    def can_administrate_article(self) -> bool:
        if self.instance:
            return can_administrate_article(self.instance, self.request.user)
        return False


class ArticleModelViewSet(
    ModelTranslateMixin, ArticleInstancePermissionMixin, CloneMixin, RevisionMixin, ModelViewSet
):
    # LIST_DOCUMENTATION = "wbwriter/viewsets/documentation/article.md"

    serializer_class = ArticleFullModelSerializer
    queryset = Article.objects.annotate(
        is_private_icon=Case(When(is_private=False, then=Value(WBIcon.VIEW.icon)), default=Value(WBIcon.IGNORE.icon))
    )

    button_config_class = ArticleModelButtonConfig
    display_config_class = ArticleDisplayConfig
    filterset_class = ArticleFilter

    search_fields = (
        "tags__title",
        "type__label",
        "type__slug",
        "content",
        "title",
        "name",
    )
    ordering = ("-modified",)
    ordering_fields = (
        "title",
        "status",
        "type",
        "created",
        "modified",
        "id",
        "author",
        "reviewer",
        "peer_reviewer",
        "qa_reviewer",
    )

    @cached_property
    def content_type(self):
        return ContentType.objects.get(app_label="wbwriter", model="article")

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.has_perm("wbwriter.administrate_article") and not self.profile.is_internal:
            qs = qs.filter(is_private=False)
        return qs.select_related(
            "type", "feedback_contact", "reviewer", "peer_reviewer", "qa_reviewer", "author"
        ).prefetch_related("tags")

    @action(detail=True, methods=["POST"], authentication_classes=[JWTCookieAuthentication])
    def generate_pdf(self, request, pk):
        """
        NOTE: JWTCookieAuthentication only works, if the frontend is served under the same URL as the backend due to
              the cookie.
        """
        article = get_object_or_404(Article, pk=pk)

        if not can_access_article(article, request.user):
            return Response({}, status=status.HTTP_403_FORBIDDEN)

        generate_pdf_as_task.delay(pk, user_id=request.user.id)
        return Response(
            {"__notification": {"title": "PDF is going to be created"}},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["POST"], authentication_classes=[JWTCookieAuthentication])
    def edit(self, request, pk):
        """Sets the current user to be the author of the specified article."""
        article = get_object_or_404(Article, pk=pk)
        article.author = request.user.profile
        article.save()
        return Response(
            {"__notification": {"title": f'You are now author of "{article.title}".'}},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["POST"], authentication_classes=[JWTCookieAuthentication])
    def reroll_peer(self, request, pk):
        """Rolls for a new peer reviewer."""
        article = get_object_or_404(Article, pk=pk)
        article.reroll_peer()
        article.save()
        return Response(
            {"__notification": {"title": f'The new peer reviewer is "{article.peer_reviewer}".'}},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["POST"], authentication_classes=[JWTCookieAuthentication])
    def reroll_qa(self, request, pk):
        """Rolls for a new QA reviewer."""
        article = get_object_or_404(Article, pk=pk)
        article.reroll_qa()
        article.save()
        return Response(
            {"__notification": {"title": f'The new QA reviewer is "{article.qa_reviewer}".'}},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["POST"], authentication_classes=[JWTCookieAuthentication])
    def reroll_peer_and_qa(self, request, pk):
        """Rolls for a new peer and a new QA reviewer."""
        article = get_object_or_404(Article, pk=pk)
        article.reroll_peer_and_qa()
        article.save()
        return Response(
            {"__notification": {"title": f'You are now author of "{article.title}".'}},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["POST"], authentication_classes=[JWTCookieAuthentication])
    def assign_new_author(self, request, pk):
        """Assigns a new author."""
        article = get_object_or_404(Article, pk=pk)
        author_id = request.POST.get("author")
        author = get_object_or_404(Person, pk=author_id)
        article.author = author
        article.save()
        return Response(
            {"__notification": {"title": f"The new author is {author}."}},
            status=status.HTTP_200_OK,
        )


class ReviewerArticleModelViewSet(ArticleModelViewSet):
    # LIST_DOCUMENTATION = "wbwriter/viewsets/documentation/article.md"

    # serializer_class = ArticleModelSerializer
    queryset = Article.objects.all()
    title_config_class = ReviewerArticleTitleConfig

    button_config_class = ArticleModelButtonConfig
    display_config_class = ArticleDisplayConfig
    endpoint_config_class = ReviewerArticleModelEndpointConfig

    search_fields = (
        "tags__title",
        "type__label",
        "type__slug",
        "content",
        "title",
        "name",
    )
    filter_fields = {
        "title": ["icontains"],
        "status": ["exact"],
        "tags": ["exact"],
        "type": ["exact", "icontains"],
        "author": ["exact"],
        "reviewer": ["exact"],
        "peer_reviewer": ["exact"],
        "qa_reviewer": ["exact"],
        "created": ["exact", "lt", "lte", "gt", "gte"],
        "modified": ["exact", "lt", "lte", "gt", "gte"],
    }
    ordering = ("-modified",)
    ordering_fields = ("title", "status", "type", "created", "modified")

    def get_queryset(self):
        return Article.objects.filter(
            Q(reviewer=self.profile, status=Article.Status.FEEDBACK)
            | Q(peer_reviewer=self.profile, status=Article.Status.PEER_REVIEW)
            | Q(qa_reviewer=self.profile, status=Article.Status.QA_REVIEW)
            | Q(author=self.profile, status=Article.Status.AUTHOR_APPROVAL)
        )

    def get_serializer_class(self):
        # TODO: Create a unique endpoint for creating instances so that we
        #       can assign a "new instance" to have better control over what
        #       serializer we want to use.
        # if self.kwargs.get("pk"):
        #     return ArticleFullModelSerializer
        # return ArticleModelSerializer
        return ArticleFullModelSerializer
