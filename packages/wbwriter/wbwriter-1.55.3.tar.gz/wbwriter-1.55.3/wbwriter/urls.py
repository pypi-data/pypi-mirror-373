from django.urls import include, path
from wbcore.routers import WBCoreRouter

from wbwriter import viewsets

router = WBCoreRouter()
router.register(r"publication", viewsets.PublicationModelViewSet, basename="publication")
router.register(
    r"publicationrepresentation", viewsets.PublicationRepresentationViewSet, basename="publicationrepresentation"
)
router.register(
    r"publicationparserrepresentation",
    viewsets.PublicationParserRepresentationViewSet,
    basename="publicationparserrepresentation",
)
router.register(
    r"publicationparser",
    viewsets.PublicationParserModelViewSet,
    basename="publicationparser",
)

router.register(r"article", viewsets.ArticleModelViewSet, basename="article")
router.register(r"articlerepresentation", viewsets.ArticleRepresentionViewSet, basename="articlerepresentation")
# router.register(r"ddq", viewsets.DDQArticleModelViewSet, basename="ddq")
router.register(r"review-article", viewsets.ReviewerArticleModelViewSet, basename="review-article")
router.register(
    r"articletyperepresentation",
    viewsets.ArticleTypeRepresentationViewSet,
    basename="articletyperepresentation",
)
router.register(
    r"articletype",
    viewsets.ArticleTypeModelViewSet,
    basename="articletype",
)
router.register(
    r"in-editor-template",
    viewsets.InEditorTemplateModelViewSet,
    basename="in-editor-template",
)
router.register(
    r"in-editor-template-representation",
    viewsets.InEditorTemplateRepresentationViewSet,
    basename="in-editor-template-representation",
)
router.register(
    r"metainformation",
    viewsets.MetaInformationRepresentationViewSet,
    basename="metainformation",
)
router.register(
    r"metainformationinstance",
    viewsets.MetaInformationInstanceModelViewSet,
    basename="metainformationinstance",
)
router.register(
    r"dependantarticle",
    viewsets.DependantArticleModelViewSet,
    basename="dependantarticle",
)
article_router = WBCoreRouter()
article_router.register(
    r"metainformationinstancearticle",
    viewsets.MetaInformationInstanceModelViewSet,
    basename="metainformationinstancearticle",
)
article_router.register(
    r"dependantarticle",
    viewsets.DependantArticleModelViewSet,
    basename="dependantarticle-article",
)

used_article_router = WBCoreRouter()
used_article_router.register(
    r"usedarticle",
    viewsets.DependantArticleModelViewSet,
    basename="usedarticle-article",
)

urlpatterns = [
    path("", include(router.urls)),
    path("article/<int:article_id>/", include(article_router.urls)),
    path("article/<int:used_article_id>/", include(used_article_router.urls)),
]
