import random

import factory
from django.contrib.contenttypes.models import ContentType
from wbcore.contrib.authentication.factories.users import InternalUserFactory
from wbcore.contrib.directory.factories.entries import PersonFactory

from wbwriter.models import (
    Article,
    ArticleType,
    Block,
    BlockParameter,
    DependantArticle,
    InEditorTemplate,
    Publication,
    PublicationParser,
    Template,
)
from wbwriter.publication_parser import PublicationParser as PublicationParserClass


class Parser(PublicationParserClass):
    def is_valid(self):
        return True


def content() -> dict:
    return {
        "sectionOrder": ["section-1"],  # A list of section keys that will be used in the `sections` dict.
        "sections": {
            "section-1": {
                "id": "section-1",
                "templateID": None,  # `null` means no InEditorTemplate instance, otherwise the ID of the instance.
                "configuration": None,  # `null` means no config. This is otherwise a dict: dict[str, Any]
                "content": {  # This is a dict: dict[str, str]. The actual content depends on the chosen template and user input.
                    "content": "lorem ipsum dolor...",
                },
            }
        },
    }


class ArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Article

    name = factory.Sequence(lambda n: f"article {n}")
    title = factory.Sequence(lambda n: f"title {n}")
    content = content()
    type = factory.SubFactory("wbwriter.factories.article.ArticleTypeFactory")
    author = factory.LazyAttribute(lambda o: InternalUserFactory.create().profile)
    feedback_contact = factory.LazyAttribute(lambda o: InternalUserFactory.create().profile)
    reviewer = factory.SubFactory("wbcore.contrib.directory.factories.entries.PersonFactory")
    peer_reviewer = factory.LazyAttribute(lambda o: InternalUserFactory.create().profile)
    peer_reviewer_approved = True
    qa_reviewer = factory.LazyAttribute(lambda o: InternalUserFactory.create().profile)
    template = factory.SubFactory("wbwriter.factories.article.TemplateFactory")
    status = Article.Status.DRAFT

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for tag in extracted:
                self.tags.add(tag)


class DependantArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DependantArticle

    article = factory.SubFactory(ArticleFactory)
    dependant_article = factory.SubFactory(ArticleFactory)


class ArticleTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ArticleType

    label = factory.Sequence(lambda n: f"articletype {n}")

    @factory.post_generation
    def parsers(self, create, extracted, **kwargs):
        self.parsers.add(PublicationParserFactory.create())

    @factory.post_generation
    def peer_reviewers(self, create, extracted, **kwargs):
        if not create:
            return

        self.peer_reviewers.add(PersonFactory())
        if extracted:
            for peer in extracted:
                self.peer_reviewers.add(peer)

    @factory.post_generation
    def qa_reviewers(self, create, extracted, **kwargs):
        if not create:
            return

        self.qa_reviewers.add(PersonFactory())
        if extracted:
            for peer in extracted:
                self.qa_reviewers.add(peer)


class TemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Template

    title = factory.Sequence(lambda n: f"template {n}")
    template = factory.Faker("paragraph")

    @factory.post_generation
    def styles(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for style in extracted:
                self.styles.add(style)


class BlockFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Block

    title = factory.Sequence(lambda n: f"block {n}")
    html = factory.Faker("paragraph")


class BlockParameterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BlockParameter

    block = factory.SubFactory(BlockFactory)
    title = factory.Sequence(lambda n: f"blockparameter {n}")
    order = random.randint(1, 9999)


class InEditorTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InEditorTemplate

    uuid = factory.Sequence(lambda n: f"uid {n}")
    title = factory.Sequence(lambda n: f"title {n}")
    description = factory.Faker("paragraph")
    style = factory.Faker("paragraph")
    template = factory.Faker("paragraph")


class AbstractPublicationFactory(factory.django.DjangoModelFactory):
    object_id = factory.SelfAttribute("content_object.id")
    content_type = factory.LazyAttribute(lambda o: ContentType.objects.get_for_model(o.content_object))

    class Meta:
        exclude = ["content_object"]
        abstract = True


class PublicationParserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PublicationParser
        django_get_or_create = ("parser_path",)

    title = factory.Sequence(lambda n: f"publicationparser {n}")
    parser_path = "wbwriter.factories.article"


class PublicationFactory(AbstractPublicationFactory):
    class Meta:
        model = Publication

    title = factory.Sequence(lambda n: f"publication {n}")
    # author = factory.SubFactory("wbcore.contrib.directory.factories.PersonFactory")
    content = factory.Faker("paragraph")
    parser = factory.SubFactory(PublicationParserFactory)
    content_object = factory.SubFactory(ArticleFactory)
    description = factory.Faker("paragraph")
    target = factory.Faker("pystr")
