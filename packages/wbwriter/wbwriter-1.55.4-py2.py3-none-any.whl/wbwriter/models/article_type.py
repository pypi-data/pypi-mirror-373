from django.db import models
from slugify import slugify
from wbcore.models import WBModel


class ArticleType(WBModel):
    """An arbitrary type for articles.

    The type of an article helps filtering out undesired categories of
    articles.
    Furthermore, having the article type in a separate model allows adding,
    removing, and changing types during runtime.

    Attributes
    ----------
    label : models.CharField
        The unique label for this type.
        This is meant to be displayed to users.
    slug : models.SlugField
        A slugified version fo the label.
        This is used for searching ArticleTypes.
    parsers : models.ManyToManyField
        One or more optional parsers. The parser are used to convert the
        `content` of an article and its associated in-editor template(s)
        to something that can be published.
    """

    label = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)
    parsers = models.ManyToManyField("wbwriter.PublicationParser", related_name="publication_parsers", blank=True)
    peer_reviewers = models.ManyToManyField("directory.Person", related_name="article_type_peer_reviewers")
    qa_reviewers = models.ManyToManyField("directory.Person", related_name="article_type_qa_reviewers")

    @classmethod
    def get_endpoint_basename(self):
        return "wbwriter:articletyperepresentation"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbwriter:articletyperepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{label}}"

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        self.slug = slugify(self.label)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Article Type"
        verbose_name_plural = "Article Types"
