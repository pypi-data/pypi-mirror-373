from wbcore import filters as wb_filters

from wbwriter.models.meta_information import MetaInformationInstance


class MetaInformationInstanceFilter(wb_filters.FilterSet):
    article = wb_filters.ModelChoiceFilter(
        label="Article",
        queryset=MetaInformationInstance.objects.all(),
        endpoint=MetaInformationInstance.get_representation_endpoint(),
        value_key=MetaInformationInstance.get_representation_value_key(),
        label_key=MetaInformationInstance.get_representation_label_key(),
        method="filter_for_article",
    )

    def filter_for_article(self, queryset, name, value):
        if value:
            return MetaInformationInstance.objects.filter(article__id=value)
        return queryset

    class Meta:
        model = MetaInformationInstance
        fields = {
            "article": ["exact"],
        }
