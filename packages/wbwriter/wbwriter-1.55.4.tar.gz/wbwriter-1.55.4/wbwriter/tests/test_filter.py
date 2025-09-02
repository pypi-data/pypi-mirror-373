import pytest
from rest_framework.test import APIRequestFactory
from wbcore.contrib.authentication.factories import InternalUserFactory
from wbwriter.factories import ArticleFactory, MetaInformationInstanceFactory
from wbwriter.filters import MetaInformationInstanceFilter
from wbwriter.models import MetaInformationInstance
from wbwriter.viewsets import ArticleModelViewSet


@pytest.mark.django_db
class TestArticleFilters:
    def test_get_my_articles_true(self):
        employee_a = InternalUserFactory().profile
        employee_b = InternalUserFactory().profile
        user_a = employee_a.user_account
        ArticleFactory(author=user_a.profile)
        ArticleFactory(author=employee_b)
        ArticleFactory(author=employee_b, reviewer=user_a.profile)

        request = APIRequestFactory().get("")
        request.user = user_a
        mvs = ArticleModelViewSet(kwargs={})
        qs = mvs.get_serializer_class().Meta.model.objects.all()
        filtered_qs = mvs.filterset_class(request=request).get_my_articles(qs, "", True)
        assert filtered_qs.count() == 2
        assert filtered_qs.count() < qs.count()

    def test_get_my_articles_false(self):
        employee_a = InternalUserFactory.create().profile
        employee_b = InternalUserFactory.create().profile
        user_a = employee_a.user_account
        ArticleFactory(author=user_a.profile)
        ArticleFactory(author=employee_b)
        ArticleFactory(author=employee_b, reviewer=user_a.profile)

        request = APIRequestFactory().get("")
        request.user = user_a
        mvs = ArticleModelViewSet(kwargs={})
        qs = mvs.get_serializer_class().Meta.model.objects.all()
        filtered_qs = mvs.filterset_class(request=request).get_my_articles(qs, "", False)
        assert filtered_qs.count() == qs.count()

    def test_filter_for_article_with_id(self):
        article = ArticleFactory()
        MetaInformationInstanceFactory(article=article)
        MetaInformationInstanceFactory.create_batch(4)
        qs = MetaInformationInstance.objects.all()
        filtered_qs = MetaInformationInstanceFilter.filter_for_article(self, queryset=qs, name="", value=article.id)
        assert filtered_qs.count() == 1
        assert filtered_qs.count() < qs.count()

    def test_filter_for_article_no_id(self):
        article = ArticleFactory()
        MetaInformationInstanceFactory(article=article)
        MetaInformationInstanceFactory.create_batch(4)
        qs = MetaInformationInstance.objects.all()
        filtered_qs = MetaInformationInstanceFilter.filter_for_article(self, queryset=qs, name="", value=None)
        assert filtered_qs.count() == qs.count()
