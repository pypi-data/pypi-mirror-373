import wbcore.serializers as wb_serializers
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse, reverse_lazy
from wbcore.contrib.directory.models import Person
from wbcore.contrib.directory.serializers import (
    InternalUserProfileRepresentationSerializer,
)
from wbcore.contrib.documents.models import Document
from wbcore.contrib.tags.serializers import TagSerializerMixin
from wbcore.serializers import (
    HyperlinkField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    RepresentationSerializer,
    TemplatedJSONTextEditor,
    register_only_instance_resource,
    register_resource,
)

from wbwriter.models import (
    Article,
    ArticleType,
    DependantArticle,
    can_administrate_article,
)

from .article_type import ArticleTypeRepresentationSerializer


class ArticleRepresentionSerializer(RepresentationSerializer):
    class Meta:
        model = Article
        fields = (
            "id",
            "title",
        )


class DependantArticleModelSerializer(ModelSerializer):
    _article = ArticleRepresentionSerializer(source="article")
    article_url = HyperlinkField(reverse_name="wbwriter:article-detail", id_field_name="article_id")
    _dependant_article = ArticleRepresentionSerializer(source="dependant_article")
    dependant_article_url = HyperlinkField(
        reverse_name="wbwriter:article-detail", id_field_name="dependant_article_id"
    )

    class Meta:
        model = DependantArticle
        fields = (
            "id",
            "article",
            "_article",
            "article_url",
            "dependant_article",
            "_dependant_article",
            "dependant_article_url",
        )


from wbcore.contrib.i18n.serializers.mixins import ModelTranslateSerializerMixin


class ArticleModelSerializer(ModelTranslateSerializerMixin, TagSerializerMixin, ModelSerializer):
    """Serializes a subset of the fields of of the Article model to minimize
    workload on serializing lists of instances.
    """

    author = PrimaryKeyRelatedField(
        many=False, label="Author", queryset=lambda: Person.objects.filter_only_internal()
    )  # we lazy load queryset to know evaluate them at runtime
    _author = InternalUserProfileRepresentationSerializer(source="author")
    _qa_reviewer = InternalUserProfileRepresentationSerializer(source="qa_reviewer", many=False)

    _type = ArticleTypeRepresentationSerializer(source="type")

    @register_resource()
    def generate(self, instance, request, user):
        return {
            "generate_pdf": reverse("wbwriter:article-generate-pdf", args=[instance.id], request=request),
            "edit": reverse("wbwriter:article-edit", args=[instance.id], request=request),
        }

    @register_resource()
    def metainformationinstance(self, instance, request, user):
        return {
            "metainformationinstance": f"{reverse('wbwriter:metainformationinstancearticle-list', args=[instance.id], request=request)}",
        }

    @register_resource()
    def dependencies(self, instance, request, user):
        return {
            "dependantarticle-article": reverse(
                viewname="wbwriter:dependantarticle-article-list", args=[instance.id], request=request
            ),
            "usedarticle-article": reverse(
                viewname="wbwriter:usedarticle-article-list", args=[instance.id], request=request
            ),
        }

    @register_only_instance_resource()
    def preview(self, instance, request, user, **kwargs):
        if document := Document.get_for_object(instance).filter(system_key=instance.system_key).first():
            return {"preview": document.file.url}
        return dict()

    @register_only_instance_resource()
    def reroll_reviewers(self, instance, request, user, **kwargs):
        if can_administrate_article(instance, user):
            return {
                "reroll_peer": reverse("wbwriter:article-reroll-peer", args=[instance.id], request=request),
                "reroll_qa": reverse("wbwriter:article-reroll-qa", args=[instance.id], request=request),
                "reroll_peer_and_qa": reverse(
                    "wbwriter:article-reroll-peer-and-qa", args=[instance.id], request=request
                ),
                "assign_new_author": reverse(
                    "wbwriter:article-assign-new-author", args=[instance.id], request=request
                ),
            }
        else:
            return {}

    @register_only_instance_resource()
    def publications(self, instance, request, user, view=None, **kwargs):
        if view and instance.publications.exists():
            return {
                "publications": f"{reverse('wbwriter:publication-list', request=request)}?content_type={view.content_type.id}&object_id={instance.id}"
            }
        return {}

    def create(self, validated_data):
        if request := self.context.get("request"):
            validated_data["author"] = request.user.profile
        return super().create(validated_data)

    def validate(self, data):
        articles = Article.objects.filter(name=data.get("name"))
        if self.instance is not None:
            articles = articles.exclude(id=self.instance.id)
            if data.get("title") in ["", None] and self.instance.title is None:
                data["title"] = data.get("name")

        if articles.exists():
            raise ValidationError({"name": ["Name already exists."]})

        return data

    class Meta:
        model = Article
        fields = (
            "id",
            "name",
            "title",
            "slug",
            "type",
            "_type",
            "status",
            "teaser_image",
            "created",
            "modified",
            "author",
            "_author",
            "qa_reviewer",
            "_qa_reviewer",
            "tags",
            "_tags",
            "_additional_resources",
            "_i18n",
        )


def _get_plugin_configs(request):
    return {
        "plugins": " ".join(
            [
                "advlist autolink lists link image charmap print preview anchor",
                "searchreplace visualblocks fullscreen noneditable template",
                "insertdatetime table advtable help wordcount code",
                "pagebreak hr imagetools powerpaste lance flite",
            ]
        ),
        "toolbar": " ".join(
            [
                "undo redo | formatselect | bold italic underline strikethrough backcolor | ",
                "alignleft aligncenter alignright alignjustify | ",
                "bullist numlist outdent indent | pastetext removeformat | help | code fullscreen | lance | ",
                "flite-toggletracking flite-toggleshow | flite-acceptone flite-rejectone | flite-acceptall flite-rejectall",
            ]
        ),
        "menu": {
            "file": {
                "title": "File",
                "items": "newdocument restoredraft | preview | print",
            },
            "edit": {
                "title": "Edit",
                "items": "undo redo | cut copy paste | selectall | searchreplace",
            },
            "view": {
                "title": "View",
                "items": "visualaid visualchars visualblocks | spellchecker | preview fullscreen",
            },
            "insert": {
                "title": "Insert",
                "items": " | ".join(
                    [
                        "image link template codesample inserttable",
                        "charmap emoticons hr",
                        "pagebreak nonbreaking anchor toc",
                        "insertdatetime",
                    ]
                ),
            },
            "format": {
                "title": "Format",
                "items": "bold italic underline strikethrough superscript subscript codeformat | formats blockformats"
                + " fontformats fontsizes align lineheight | forecolor backcolor | removeformat",
            },
            "tools": {
                "title": "Tools",
                "items": "code | spellchecker spellcheckerlanguage | wordcount",
            },
            "table": {
                "title": "Table",
                "items": "inserttable | cell row column | tableprops deletetable",
            },
            # "tc": {"title": "Comments", "items": "addcomment showcomments deleteallconversations"},
            "help": {"title": "Help", "items": "help"},
        },
        "paste_as_text": True,
        "powerpaste_word_import": "clean",
        "powerpaste_googledocs_import": "clean",
        "powerpaste_html_import": "clean",
        "browser_spellcheck": True,
        "atp": {
            "templates": reverse_lazy("wbwriter:in-editor-template-list", request=request),
        },
        "content_style": "body{margin:0px 12px;}",
        "deprecation_warnings": False,
    }


class ArticleFullModelSerializer(ArticleModelSerializer):
    """Serializes the full set of the fields of of the Article model."""

    is_private_icon = wb_serializers.IconSelectField(read_only=True)

    author = wb_serializers.PrimaryKeyRelatedField(
        many=False,
        label="Author",
        read_only=lambda view: (not view.can_edit_article_author or view.instance.status == Article.Status.APPROVED)
        if view.instance
        else not view.new_mode,
        queryset=lambda: Person.objects.filter_only_internal(),
        default=wb_serializers.CurrentUserDefault("profile"),
    )
    name = wb_serializers.CharField(
        max_length=1024,
        label="Name",
        help_text="A unique name to reference this article.",
        read_only=lambda view: not view.can_edit_article_meta_data if view.instance else not view.new_mode,
    )
    title = wb_serializers.CharField(
        max_length=1024,
        label="Title",
        required=False,
        help_text="The title of the article that is going to be used when imported into other articles. "
        + "Defaults to the name of the article when not set.",
        read_only=lambda view: not view.can_edit_article_meta_data if view.instance else not view.new_mode,
    )

    teaser_image = wb_serializers.ImageField(
        label="Teaser image",
        required=False,
        read_only=lambda view: not view.can_edit_article_content if view.instance else not view.new_mode,
    )

    content = TemplatedJSONTextEditor(
        templates="wbwriter:in-editor-template-list",
        default_editor_config=_get_plugin_configs,
        default="",
        label="Content",
        read_only=lambda view: not view.can_edit_article_content if view.instance else not view.new_mode,
    )

    type = wb_serializers.PrimaryKeyRelatedField(
        label="Type",
        many=False,
        queryset=ArticleType.objects.all(),
        read_only=lambda view: not view.can_edit_article_type if view.instance else not view.new_mode,
    )
    _type = ArticleTypeRepresentationSerializer(source="type", many=False)
    feedback_contact = wb_serializers.PrimaryKeyRelatedField(
        label="Feedback Contact",
        many=False,
        required=False,
        default=wb_serializers.DefaultAttributeFromObject(source="author.id"),
        queryset=lambda: Person.objects.filter_only_internal(),  # TODO: Filter out the people from the qa reviewer person group
    )
    _feedback_contact = InternalUserProfileRepresentationSerializer(source="feedback_contact", many=False)
    reviewer = PrimaryKeyRelatedField(many=False, label="Reviewer", read_only=True)
    _reviewer = InternalUserProfileRepresentationSerializer(source="reviewer", many=False)

    peer_reviewer = PrimaryKeyRelatedField(
        many=False,
        label="Peer Reviewers",
        queryset=lambda: Person.objects.filter_only_internal(),
        read_only=lambda view: not view.can_administrate_article and not view.new_mode,
    )
    _peer_reviewer = InternalUserProfileRepresentationSerializer(source="peer_reviewer", many=False)

    qa_reviewer = PrimaryKeyRelatedField(
        many=False,
        label="QA Reviewer",
        queryset=lambda: Person.objects.filter_only_internal(),
        read_only=lambda view: not view.can_administrate_article and not view.new_mode,
    )
    _qa_reviewer = InternalUserProfileRepresentationSerializer(source="qa_reviewer", many=False)

    def validate(self, data):
        data = super().validate(data)
        if "type" in data:
            if (
                self.instance
                and data.get("type")
                and data.get("type").slug != "ddq"
                and (
                    ("author" in data and not data.get("author"))
                    or ("author" not in data and self.instance.author is None)
                )
            ):
                raise serializers.ValidationError(
                    {"type": 'This must be set to "DDQ" as long as no author has been assigned!'}
                )

        return data

    class Meta:
        model = Article
        fields = (
            "id",
            "is_private_icon",
            "name",
            "title",
            "slug",
            "type",
            "_type",
            "created",
            "modified",
            "teaser_image",
            "content",
            "status",
            "author",
            "_author",
            "feedback_contact",
            "_feedback_contact",
            "reviewer",
            "_reviewer",
            "peer_reviewer",
            "_peer_reviewer",
            "qa_reviewer",
            "_qa_reviewer",
            "is_private",
            "tags",
            "_tags",
            "_additional_resources",
            "_i18n",
        )
