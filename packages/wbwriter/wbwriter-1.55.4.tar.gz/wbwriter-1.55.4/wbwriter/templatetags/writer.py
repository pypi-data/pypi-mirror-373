from django import template
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.template import Context, Template
from slugify import slugify
from wbcore.markdown.template import load_registered_templatetags

from wbwriter.models import Article

register = template.Library()


@register.inclusion_tag("wbwriter/templatetags/table_of_contents.html", takes_context=True)
def table_of_contents(context, title="Table of contents", custom_enumeration=True):
    if "article" in context and context.get("article"):
        article = context.get("article")
        article_toc = article.get_article_structure()
        return {"title": title, "custom_enumeration": custom_enumeration, **article_toc}

    return {"not_working": "<i>Table of content is only rendered in the exported PDF Version.</i>"}


@register.simple_tag(takes_context=True)
def load_article(context, article_id, with_title=True, include_in_toc=True, enumeration_from_toc=True):
    prefix = ""
    level = 1

    article = get_object_or_404(Article, id=article_id)
    # Render the content
    template = ""
    for section in article.content["sectionOrder"]:
        template = article.content["sections"][section]["content"]["content"]

    loaded_template_tags = load_registered_templatetags()
    if with_title:
        if main_article := context.get("article"):
            if structure := main_article.article_structure.get(str(article_id)):
                prefix = structure.get("enumerator", "")
                level = structure.get("level", 1)

        anchor = "<a name='" + slugify(article.name) + "'></a>"
        template = f"<h1 class='header-{level}'>{prefix} {article.title}{anchor}</h1>\n" + template
    return Template(loaded_template_tags + template).render(Context(context))


@register.inclusion_tag("wbwriter/templatetags/cite_article.html", takes_context=True)
def cite_article(context, article_id, text="(see {e} {t})"):
    if "article" in context and context.get("article"):
        main_article = context.get("article")
        prefix = ""
        if structure := main_article.article_structure.get(str(article_id)):
            prefix = structure.get("enumerator", "")
            structure.get("level", 1)
        article = get_object_or_404(Article, id=article_id)
        return {"anchor": slugify(article.name), "text": text.format(e=prefix, t=article.title)}

    return {"not_working": "(article citations only work in a rendered pdf.)"}


def block_templatetag(block):
    def templatetag(context, *args):
        parameters = block.parameters.all().count()
        if parameters != len(args):
            raise ValidationError({"non_field_errors": "Not all fields were send to the server."})
        return block.render(args)

    return templatetag


# TODO do we need the following three lines of code? (13.07.2022 / CL)
# with suppress(ProgrammingError):
#     for block in Block.objects.all():
#         register.simple_tag(takes_context=True, name=block.key)(block_templatetag(block))
