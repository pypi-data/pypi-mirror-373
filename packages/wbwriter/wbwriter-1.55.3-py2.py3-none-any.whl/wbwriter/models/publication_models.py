import datetime
from importlib import import_module

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.functional import cached_property
from modeltrans.fields import TranslationField
from rest_framework.reverse import reverse
from slugify import slugify
from wbcore.contrib.tags.models import TagModelMixin


class Publication(TagModelMixin, models.Model):
    """A publication of anything.

    A publication stores content prepared for a specific platform or use
    case. For instance, it stores an HTML string for publishing something on
    web.
    """

    class Meta:
        verbose_name = "Publication"
        verbose_name_plural = "Publications"

    title = models.CharField(max_length=1024)

    slug = models.CharField(max_length=1024, blank=True)

    target = models.CharField(max_length=256)

    teaser_image = models.ImageField(blank=True, null=True, upload_to="writer/publication/teasers")
    thumbnail_image = models.ImageField(blank=True, null=True, upload_to="writer/publication/thumbnails")

    author = models.ForeignKey(
        "directory.Person",
        related_name="publication",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    created = models.DateField(
        verbose_name="Creation Date",
        auto_now_add=True,
        help_text="The date on which this has been created.",
    )

    modified = models.DateTimeField(
        verbose_name="Last Modification Datetime",
        auto_now=True,
        help_text="The date and time on which this has been modified last.",
    )

    description = models.TextField(default="", blank=True)

    content = models.TextField(default="")

    content_file = models.FileField(
        max_length=256,
        upload_to="writer/publication/content_files",
        blank=True,
        null=True,
    )

    i18n = TranslationField(fields=["title", "slug", "content"])

    parser = models.ForeignKey(
        "wbwriter.PublicationParser",
        related_name="parsed_publication",
        on_delete=models.PROTECT,
    )

    additional_information = models.JSONField(default=dict, null=True, blank=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    @classmethod
    def create_or_update_from_parser_and_object(cls, parser, generic_object):
        if hasattr(generic_object, "_build_dto") and callable(generic_object._build_dto):
            ctype = ContentType.objects.get_for_model(generic_object)
            pub, created = cls.objects.get_or_create(parser=parser, content_type=ctype, object_id=generic_object.id)
            publ_metadata = generic_object.get_publication_metadata()
            for k, v in publ_metadata.items():
                setattr(pub, k, v)
            pub.parser.parser_class(
                generic_object._build_dto(), datetime.date.today() if created else pub.created
            ).parse(pub)
            pub.save()

    @classmethod
    def get_endpoint_basename(self):
        return "wbwriter:publication"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbwriter:publicationrepresentation-list"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_tag_detail_endpoint(self):
        return reverse("wbwriter:publication-detail", [self.id])

    def get_tag_representation(self):
        return self.title


class PublicationParser(models.Model):
    """A parser meant to be used to parse something into a publication.

    Attributes
    ----------
    title : models.CharField
        The unique title for this parser.

    parser_path : models.CharField
        A dotted path to the parser file relatoive to the projects root
        (ROOT/projects/).

    created : models.DateField
        The date on which this publication has been created.

    content : models.TextField
        The content of this publication in text form.

    content_file : models.FileField
        An optional file attachment, that represents the publications content.
    """

    class Meta:
        verbose_name = "PublicationParser"
        verbose_name_plural = "PublicationParsers"

    title = models.CharField(
        max_length=1024,
        unique=True,
    )
    slug = models.CharField(max_length=1024, blank=True)
    parser_path = models.CharField(
        max_length=1024,
        unique=True,
    )

    @cached_property
    def parser_class(self):
        return import_module(self.parser_path).Parser

    @classmethod
    def get_endpoint_basename(cls):
        return "wbwriter:publicationparser"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbwriter:publicationparserrepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{title}}"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title}"
