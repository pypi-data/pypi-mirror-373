import json
import os
from abc import ABC
from datetime import date
from io import BytesIO
from typing import Iterable

from django.conf import settings
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from PIL import Image, ImageOps
from slugify import slugify
from wbcore.contrib.tags.models import Tag

from wbwriter.pdf_generator import PdfGenerator

from .typings import ArticleDTO


class ParserValidationException(Exception):
    def __init__(self, *args, errors=None, **kwargs):  # real signature unknown
        self.errors = errors


class PublicationParser(ABC):  # pragma: no cover
    def __init__(self, article: ArticleDTO, published_date: date):
        self.article = article
        self.published_date = published_date

    @property
    def template_path(self) -> str:
        if hasattr(self, "TEMPLATE_PATH"):
            return self.TEMPLATE_PATH
        raise ValueError(
            f"The attribute TEMPLATE_PATH needs to be define in the parser {self.__class__.__name__} in order to generate file"
        )

    @property
    def article_type(self) -> str:
        if hasattr(self, "ARTICLE_TYPE"):
            return self.ARTICLE_TYPE
        raise ValueError(
            f"The attribute ARTICLE_TYPE needs to be define in the parser {self.__class__.__name__} in order to generate content"
        )

    @property
    def default_section(self) -> str:
        if hasattr(self, "DEFAULT_SECTION"):
            return self.DEFAULT_SECTION
        raise ValueError(
            f"The attribute DEFAULT_SECTION needs to be define in the parser {self.__class__.__name__} in order to generate content"
        )

    @property
    def errors(self) -> list[str]:
        if not hasattr(self, "_errors"):
            raise AssertionError("You must call `.is_valid()` before accessing `.errors`.")
        return self._errors

    def _is_valid(self) -> bool:
        return True

    def is_valid(self, raise_exception: bool = True) -> bool:
        self._errors = []
        is_valid = self._is_valid()
        if self.errors and raise_exception:
            raise ParserValidationException(errors=self.errors)
        return is_valid

    def _get_additional_information(self) -> dict[str, any]:
        additional_information = {"type": self.article_type, "is-private": self.article.is_private}

        for meta_info in self.article.meta_information:
            additional_information[meta_info["meta_information__key"]] = meta_info["boolean_value"]
        return additional_information

    def get_file(self, context: dict[str, any] | None = None) -> BytesIO | None:
        """Parses the given object's data and returns the publications content
        rendered as a PDF.

        Parameters
        ----------
        context: The context data that should be used by the file. Optional. If not provided, it will be fetchted from get_file_context

        Returns
        -------
        Either None or ByteIO. The latter representing the PDF representation of the content.
        """
        if not context:
            context = self.get_file_context()
        html = render_to_string(self.template_path, context)

        if settings.DEBUG:
            if not os.path.isdir("tmp"):
                os.mkdir("tmp")
            with open(f"tmp/{slugify(self.article.title)}.html", "w") as f:
                f.write(html)

        pdf_generator = PdfGenerator(
            main_html=html,
            custom_css=[],
            side_margin=0,
            extra_vertical_margin=0,
        )

        return pdf_generator.render_pdf()

    def _get_images(self) -> tuple[None | tuple[str, ContentFile], None | tuple[str, ContentFile]]:
        """Derives the teaser image and its thumbnail form the given object.

        On the first position there is a tuple that contains the filename and
        the ContentFile for the teaser image, if it is not None.

        On the second position there is a tuple that contains the filename and
        the ContentFile for the thumbnail of the teaser image, if it is not
        None.

        Parameters
        ----------
        article: The data that should be published.

        Returns
        -------
        Returns a tuple that may contain the data for a teaser image and
        its thumbnail.

        On the first position there is a tuple that contains the filename and
        the ContentFile for the teaser image, if it is not None.

        On the second position there is a tuple that contains the filename and
        the ContentFile for the thumbnail of the teaser image, if it is not
        None.
        """
        teaser_image = self.article.teaser_image
        if not teaser_image:
            return (None, None)

        basename_parts = os.path.basename(teaser_image.name).rsplit(".", 1)
        if len(basename_parts) < 2:
            teaser_image_basename = basename_parts[0]
            teaser_image_extension = "png"
        else:
            teaser_image_basename = basename_parts[0]
            teaser_image_extension = basename_parts[1]

        if len(teaser_image_basename) > 100:
            teaser_image_basename = teaser_image_basename.substring(0, 92)
        if teaser_image_extension.upper() == "JPG":  # NOTE: Image doesn't understand "jpg"
            teaser_image_extension = "jpeg"
        pil_image_obj = Image.open(self.article.teaser_image)

        pil_image_obj = ImageOps.exif_transpose(
            pil_image_obj
        )  # We need transpose the image accoording to the Exif data for mobile phone shots

        pil_teaser_image_obj = pil_image_obj.copy()
        pil_teaser_image_obj.thumbnail((1000, 1000))
        teaser_image_tuple = None
        f_teaser = BytesIO()
        try:
            pil_teaser_image_obj.save(f_teaser, format=teaser_image_extension)
            teaser_image_tuple = (
                f"{teaser_image_basename}.{teaser_image_extension}",
                ContentFile(f_teaser.getvalue()),
            )
        finally:
            f_teaser.close()

        pil_thumbnail_image_obj = pil_image_obj.copy()
        pil_thumbnail_image_obj.thumbnail((510, 510))
        thumbnail_image_tuple = None
        f_thumbnail = BytesIO()
        try:
            pil_thumbnail_image_obj.save(f_thumbnail, format=teaser_image_extension)
            thumbnail_image_tuple = (
                f"{teaser_image_basename}_thumbnail.{teaser_image_extension}",
                ContentFile(f_thumbnail.getvalue()),
            )
        finally:
            f_thumbnail.close()

        if teaser_image_tuple and thumbnail_image_tuple:
            return (teaser_image_tuple, thumbnail_image_tuple)
        if teaser_image_tuple:
            return (teaser_image_tuple, None)
        if thumbnail_image_tuple:
            return (None, thumbnail_image_tuple)
        return (None, None)

    def _get_tags(self) -> Iterable[tuple[str, str]]:
        """Derives the necessary tags from the object data..

        Parameters
        ----------
        article: The data that should be published.

        Returns
        -------
        A list of key, label tag

        """
        for tag_id in self.article.tags:
            tag = Tag.objects.get(id=tag_id)
            yield (tag.slug, tag.title)

    def _get_target(self) -> str:
        """Returns a string that is unique for the publication target.

        Example:

            "website" if the publication goes to a companies own website.
        """
        return "website"

    def get_publication_content(self) -> str:
        return json.dumps({"content": self.article.content})

    def get_file_context(self) -> dict[str, str]:
        return self.article.to_dict()

    def parse(self, publication) -> None:
        """Parses the data given in `article` and changes (but doesn't save) the
        given publication instance accordingly.

        Parameters
        ----------
        publication: An instance of the Publication model. This instance will
        be changed based on the given data in `article`. The instance is not saved! You need to call the save method
        yourself.

        article: The data that should be parsed into a publication.

        published_date: The date that the publication should display as the
        publication date.
        """

        if self.is_valid():
            publication.additional_information = self._get_additional_information()

            publication.content = self.get_publication_content()

            file = self.get_file()
            if file:
                publication.content_file.save(f"{publication.slug}.pdf", BytesIO(file))

            (teaser_image, thumbnail_image) = self._get_images()
            if teaser_image and len(teaser_image) == 2:
                publication.teaser_image.save(teaser_image[0], teaser_image[1])
            if thumbnail_image and len(thumbnail_image) == 2:
                publication.thumbnail_image.save(thumbnail_image[0], thumbnail_image[1])

            publication.tags.clear()
            for tag_key, tag_title in self._get_tags():
                tag = Tag.objects.get_or_create(
                    slug=slugify(tag_key), content_type=None, defaults={"title": tag_title}
                )[0]
                publication.tags.add(tag)

            publication.target = self._get_target()
