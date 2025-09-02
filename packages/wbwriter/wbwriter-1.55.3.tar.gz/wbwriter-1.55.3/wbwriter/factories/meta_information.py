import factory

from wbwriter.factories.article import ArticleTypeFactory
from wbwriter.models import MetaInformation, MetaInformationInstance


class MetaInformationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MetaInformation

    name = factory.Sequence(lambda n: f"metainfo {n}")
    key = factory.Sequence(lambda n: f"key {n}")

    @factory.post_generation
    def article_type(self, create, extracted, **kwargs):
        if not create:
            return

        self.article_type.add(ArticleTypeFactory())
        if extracted:
            for _type in extracted:
                self.article_type.add(_type)


class MetaInformationInstanceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MetaInformationInstance

    article = factory.SubFactory("wbwriter.factories.article.ArticleFactory")
    meta_information = factory.SubFactory(MetaInformationFactory)
