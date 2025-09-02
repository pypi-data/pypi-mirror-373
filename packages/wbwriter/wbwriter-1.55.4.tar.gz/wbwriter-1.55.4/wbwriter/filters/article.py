import django_filters
from django.db.models import Q
from wbcore import filters

from wbwriter.models import Article, ArticleType


class ArticleFilter(filters.FilterSet):
    show_only_involved_articles = filters.BooleanFilter(
        initial=True,
        label="Show only my articles",
        method="get_my_articles",
    )
    type = filters.ModelMultipleChoiceFilter(
        label="Types",
        queryset=ArticleType.objects.all(),
        endpoint=ArticleType.get_representation_endpoint(),
        value_key=ArticleType.get_representation_value_key(),
        label_key=ArticleType.get_representation_label_key(),
    )

    def get_my_articles(self, queryset, name, value):
        if value:
            request = self.request
            user = request.user
            profile = user.profile
            return queryset.filter(
                Q(author=profile) | Q(reviewer=profile) | Q(peer_reviewer=profile) | Q(qa_reviewer=profile)
            )
        return queryset

    status = filters.MultipleChoiceFilter(
        label="Status", choices=Article.Status.choices, widget=django_filters.widgets.CSVWidget
    )

    class Meta:
        model = Article
        fields = {
            "title": ["icontains"],
            "tags": ["exact"],
            "author": ["exact"],
            "reviewer": ["exact"],
            "peer_reviewer": ["exact"],
            "qa_reviewer": ["exact"],
            "created": ["exact", "lt", "lte", "gt", "gte"],
            "modified": ["exact", "lt", "lte", "gt", "gte"],
            "is_private": ["exact"],
        }
