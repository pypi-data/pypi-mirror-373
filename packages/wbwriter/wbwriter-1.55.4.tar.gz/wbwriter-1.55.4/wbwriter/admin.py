from django.contrib import admin
from reversion_compare.admin import CompareVersionAdmin

from wbwriter.models import (
    Article,
    ArticleType,
    Block,
    BlockParameter,
    DependantArticle,
    InEditorTemplate,
    MetaInformation,
    MetaInformationInstance,
    Publication,
    PublicationParser,
    Style,
    Template,
)


class UsesArticleInline(admin.TabularInline):
    verbose_name = "Uses Article"
    fields = ["dependant_article"]
    model = DependantArticle
    fk_name = "article"
    extra = 0


class UsedArticleInline(admin.TabularInline):
    verbose_name = "Used in Article"
    fields = ["article"]
    model = DependantArticle
    fk_name = "dependant_article"
    extra = 0


@admin.register(MetaInformation)
class MetaInformationModelAdmin(admin.ModelAdmin):
    pass


@admin.register(MetaInformationInstance)
class MetaInformationInstanceModelAdmin(admin.ModelAdmin):
    pass


class MetaInformationInstanceInline(admin.TabularInline):
    model = MetaInformationInstance
    extra = 0
    list_display = ("meta_information", "boolean_value")


@admin.register(ArticleType)
class ArticleTypeModelAdmin(admin.ModelAdmin):
    list_display = ("id", "label", "slug")

    ordering = ["slug"]
    search_fields = ["id", "label", "slug"]

    autocomplete_fields = [
        "peer_reviewers",
        "qa_reviewers",
    ]

    # prepopulated_fields = {"slug": ("label",)}


@admin.register(Article)
class ArticleModelAdmin(CompareVersionAdmin, admin.ModelAdmin):
    list_display = ("id", "title", "slug")

    autocomplete_fields = [
        "author",
        "reviewer",
        "peer_reviewer",
        "qa_reviewer",
    ]

    inlines = [UsesArticleInline, UsedArticleInline, MetaInformationInstanceInline]

    def reversion_register(self, model, **options):
        options = {
            # Foreign keys that will be observed.
            # "follow": ("author", "reviewer", "peer_reviewer", "qa_reviewer"),
            # Fields to ignore when creating versions
            "exclude": ("created", "modified", "published"),
            "ignore_duplicates": True,
        }
        super().reversion_register(model, **options)


@admin.register(Style)
class StyleModelAdmin(admin.ModelAdmin):
    list_display = ("id", "title")


@admin.register(InEditorTemplate)
class InEditorTemplateModelAdmin(admin.ModelAdmin):
    list_display = ("uuid", "title", "is_stand_alone_template")

    ordering = ["uuid", "title", "is_stand_alone_template"]
    search_fields = ["uuid", "title", "description"]


@admin.register(Template)
class TemplateModelAdmin(admin.ModelAdmin):
    list_display = ("id", "title")


class BlockParameterInline(admin.StackedInline):
    model = BlockParameter
    extra = 0


@admin.register(Block)
class BlockModelAdmin(admin.ModelAdmin):
    list_display = ("title",)

    inlines = (BlockParameterInline,)


def rerender_publication(modeladmin, request, queryset):
    for pub in queryset:
        Publication.create_or_update_from_parser_and_object(pub.parser, pub.content_object)


@admin.register(Publication)
class PublicationModelAdmin(CompareVersionAdmin, admin.ModelAdmin):
    list_display = ("id", "title", "modified", "created")
    list_filter = ("created", "modified")

    ordering = ["title", "author", "created", "modified"]
    search_fields = ["title", "author__computed_str"]

    actions = [rerender_publication]


@admin.register(PublicationParser)
class PublicationParserModelAdmin(admin.ModelAdmin):
    list_display = ("title",)
    list_filter = ("title",)

    ordering = ["title", "parser_path"]
    search_fields = ["title", "slug"]
