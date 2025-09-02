import datetime
import json
import re
from contextlib import suppress
from copy import deepcopy
from datetime import date, timedelta

from celery import shared_task
from django import template
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.db import models
from django.db.models import Count, Max, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.utils.translation import gettext_lazy
from django_fsm import FSMField, transition
from dynamic_preferences.registries import global_preferences_registry
from modeltrans.fields import TranslationField
from rest_framework.reverse import reverse
from slugify import slugify
from wbcore.contrib.directory.models import Person
from wbcore.contrib.documents.models import Document, DocumentType
from wbcore.contrib.i18n.translation import translate_string
from wbcore.contrib.icons import WBIcon
from wbcore.contrib.notifications.dispatch import send_notification
from wbcore.contrib.notifications.utils import create_notification_type
from wbcore.contrib.tags.models import TagModelMixin
from wbcore.enums import RequestType
from wbcore.markdown.template import resolve_content
from wbcore.metadata.configs.buttons import ActionButton, ButtonDefaultColor
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
)
from wbcore.models import WBModel
from wbcore.utils.models import CloneMixin
from weasyprint import CSS

from wbwriter.models.publication_models import Publication
from wbwriter.pdf_generator import PdfGenerator
from wbwriter.publication_parser import ParserValidationException
from wbwriter.typings import ArticleDTO

from .mixins import PublishableMixin


@shared_task
def generate_publications(article_id):
    with suppress(Article.DoesNotExist):
        article = Article.objects.get(id=article_id)
        if article.can_be_published():
            for parser in article.type.parsers.all():
                # Create the publication
                Publication.create_or_update_from_parser_and_object(parser, article)


def can_administrate_article(instance, user):
    """Allow only superusers and article admins to admin articles."""
    is_superuser = user.is_superuser
    is_article_admin = user.has_perm("wbwriter.administrate_article")

    return is_superuser or is_article_admin


def can_access_article(instance, user):
    """Allow access to superusers always, and to others when their position is appropriate."""
    return (
        can_administrate_article(instance, user)
        or user.is_superuser
        or user.profile.is_internal
        or is_reviewer(instance, user)
        or is_qa_reviewer(instance, user)
        or is_peer_reviewer(instance, user)
    )


def can_edit_article_author(instance, user) -> bool:
    """Allow the author and admins to edit the author."""
    if instance.author is None:
        return True

    return can_administrate_article(instance, user)


def can_edit_article_content(instance, user) -> bool:
    """Allow the appropriate role to edit content based on the state of the article."""
    if instance.author is None:
        return True

    if instance.status == Article.Status.DRAFT:
        return is_author(instance, user)

    if instance.status == Article.Status.FEEDBACK:
        return is_reviewer(instance, user)

    if instance.status == Article.Status.PEER_REVIEW:
        return is_peer_reviewer(instance, user)

    if instance.status == Article.Status.QA_REVIEW:
        return is_qa_reviewer(instance, user)

    return can_administrate_article(instance, user)


def can_edit_article_meta_data(instance, user) -> bool:
    """Allow the author to change the meta data of the article."""
    return (
        is_author(instance, user)
        or (is_reviewer(instance, user) and instance.status == Article.Status.FEEDBACK)
        or (is_peer_reviewer(instance, user) and instance.status == Article.Status.PEER_REVIEW)
        or (is_qa_reviewer(instance, user) and instance.status == Article.Status.QA_REVIEW)
    )


def can_edit_article_type(instance, user) -> bool:
    return is_author(instance, user) and instance.status == Article.Status.DRAFT


def can_request_peer_review(instance) -> bool:
    return not instance.peer_reviewer_approved


def can_request_qa_review(instance) -> bool:
    return instance.peer_reviewer_approved


def is_author(instance, user) -> bool:
    """Confirm user is the author of the instance."""
    return instance.author is None or instance.author == user.profile or can_administrate_article(instance, user)


def is_reviewer(instance, user) -> bool:
    """Confirm user is the reviewer of the instance."""
    return instance.reviewer == user.profile or can_administrate_article(instance, user)


def is_peer_reviewer(instance, user) -> bool:
    """Confirm user is ine of the peer reviewer of the instance's type."""
    if can_administrate_article(instance, user):
        return True
    return (
        instance.peer_reviewer is not None and instance.peer_reviewer.id == user.profile.id
    ) or instance.type.peer_reviewers.filter(id=user.profile.id).exists()


def is_qa_reviewer(instance, user) -> bool:
    """Confirm user is the quality assurance reviewer of the instance's type."""
    if can_administrate_article(instance, user):
        return True
    return (
        instance.qa_reviewer is not None and instance.qa_reviewer.id == user.profile.id
    ) or instance.type.qa_reviewers.filter(id=user.profile.id).exists()


class DependantArticle(WBModel):
    article = models.ForeignKey(
        to="wbwriter.Article",
        related_name="dependant_article_connections",
        on_delete=models.CASCADE,
    )

    dependant_article = models.ForeignKey(
        to="wbwriter.Article",
        related_name="used_article_connections",
        on_delete=models.PROTECT,
    )

    @classmethod
    def get_endpoint_basename(self):
        return "wbwriter:dependantarticle"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbwriter:dependantarticle-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{ article }} - {{ dependant_article }}"


def create_dependencies(article):
    if article.id:
        for dependency in re.findall("{% load_article.* ([0-9]*) %}", json.dumps(article.content)):
            DependantArticle.objects.get_or_create(article=article, dependant_article_id=dependency)


class Article(CloneMixin, TagModelMixin, PublishableMixin, WBModel):
    class Status(models.TextChoices):
        DRAFT = ("draft", "Draft")
        FEEDBACK = ("feedback", "Feedback")
        PEER_REVIEW = ("peer_review", "Peer Review")
        QA_REVIEW = ("qa_review", "QA Review")
        AUTHOR_APPROVAL = ("author_approval", "Author approval")
        APPROVED = ("approved", "Approved")
        PUBLISHED = ("published", "Published")

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"

        permissions = [
            ("administrate_article", "Can administrate Articles."),
        ]

        notification_types = [
            create_notification_type(
                "wbwriter.article.notify",
                "Article Notification",
                "Sends a notification when something happens in a relevant article.",
                True,
                True,
                False,
            ),
        ]

    """
    /////////////////////////////////////////////////////////////////
    ///                  FSM Transition Buttons                   ///
    /////////////////////////////////////////////////////////////////
    """
    fsm_base_button_parameters = {
        "method": RequestType.PATCH,
        "identifiers": ("wbwriter:article",),
        "description_fields": "<p>{{ title }}</p>",
    }

    request_feedback_button = ActionButton(
        method=RequestType.PATCH,
        identifiers=("wbwriter:article",),
        description_fields="<p>Select a contact to ask for feedback.</p>",
        key="requestfeedback",
        label="Request Feedback",
        action_label="Request Feedback",
        color=ButtonDefaultColor.PRIMARY,
        icon=WBIcon.FEEDBACK.icon,
        instance_display=create_simple_display([["feedback_contact"]]),
    )

    submit_feedback_button = ActionButton(
        method=RequestType.PATCH,
        identifiers=("wbwriter:article",),
        description_fields="<p>Are you sure you want to<br />submit your feedback?</p>",
        key="submitfeedback",
        label="Submit Feedback",
        action_label="Submit Feedback",
        color=ButtonDefaultColor.PRIMARY,
        icon=WBIcon.SEND.icon,
    )

    request_peer_review_button = ActionButton(
        method=RequestType.PATCH,
        identifiers=("wbwriter:article",),
        description_fields="<p>Are you sure you want to<br />request a peer review?</p>",
        key="requestpeerreview",
        label="Request Peer Review",
        action_label="Request Peer Review",
        color=ButtonDefaultColor.PRIMARY,
        icon=WBIcon.PEOPLE.icon,
    )

    request_qa_review_button = ActionButton(
        method=RequestType.PATCH,
        identifiers=("wbwriter:article",),
        description_fields="<p>Are you sure you want to<br />request a QA review?</p>",
        key="requestqareview",
        label="Request QA Review",
        action_label="Request QA Review",
        color=ButtonDefaultColor.PRIMARY,
        icon=WBIcon.PEOPLE.icon,
    )

    peer_approve_button = ActionButton(
        method=RequestType.PATCH,
        identifiers=("wbwriter:article",),
        description_fields="<p>Are you sure you want to<br />approve this draft?</p>",
        key="peerapprove",
        label="Approve",
        action_label="Approve",
        color=ButtonDefaultColor.SUCCESS,
        icon=WBIcon.CONFIRM.icon,
    )

    peer_reject_button = ActionButton(
        method=RequestType.PATCH,
        identifiers=("wbwriter:article",),
        description_fields="<p>Are you sure you want to<br />reject this draft?</p>",
        key="peerreject",
        label="Request Changes",
        action_label="Request Changes",
        color=ButtonDefaultColor.WARNING,
        icon=WBIcon.REJECT.icon,
    )

    qa_approve_draft_button = ActionButton(
        method=RequestType.PATCH,
        identifiers=("wbwriter:article",),
        description_fields="<p>Are you sure you want to<br />approve this draft?</p>",
        key="qaapprove",
        label="Approve",
        action_label="Approve",
        color=ButtonDefaultColor.SUCCESS,
        icon=WBIcon.APPROVE.icon,
    )

    qa_reject_draft_button = ActionButton(
        method=RequestType.PATCH,
        identifiers=("wbwriter:article",),
        description_fields="<p>Are you sure you want to<br />reject this draft?</p>",
        key="qareject",
        label="Request Changes",
        action_label="Request Changes",
        color=ButtonDefaultColor.WARNING,
        icon=WBIcon.DENY.icon,
    )

    author_approve_button = ActionButton(
        method=RequestType.PATCH,
        identifiers=("wbwriter:article",),
        description_fields="<p>Are you sure you want to<br />approve this article?</p>",
        key="authorapprove",
        label="Approve",
        action_label="Approve",
        color=ButtonDefaultColor.SUCCESS,
        icon=WBIcon.APPROVE.icon,
    )

    author_reject_button = ActionButton(
        method=RequestType.PATCH,
        identifiers=("wbwriter:article",),
        description_fields="<p>Are you sure you want to<br />reject this article?</p>",
        key="authorreject",
        label="Reject",
        action_label="Reject",
        color=ButtonDefaultColor.WARNING,
        icon=WBIcon.DENY.icon,
    )

    authors_revise_button = ActionButton(
        method=RequestType.PATCH,
        identifiers=("wbwriter:article",),
        description_fields="<p>Are you sure you want to<br />revise this article?</p>",
        key="authorrevise",
        label="Revise Article",
        action_label="Revise Article",
        color=ButtonDefaultColor.PRIMARY,
        icon=WBIcon.SYNCHRONIZE.icon,
    )

    qas_revise_button = ActionButton(
        method=RequestType.PATCH,
        identifiers=("wbwriter:article",),
        description_fields="<p>Are you sure you want to<br />revise this article's review?</p>",
        key="qarevise",
        label="Revise Review",
        action_label="Revise Review",
        color=ButtonDefaultColor.PRIMARY,
        icon=WBIcon.SYNCHRONIZE.icon,
    )

    publish_button = ActionButton(
        method=RequestType.PATCH,
        identifiers=("wbwriter:article",),
        description_fields="<p>Are you sure you want to<br />publish this article?</p>",
        key="publish",
        label="Publish",
        action_label="Publish",
        color=ButtonDefaultColor.PRIMARY,
        icon=WBIcon.DOCUMENT.icon,
    )

    unpublish_button = ActionButton(
        method=RequestType.PATCH,
        identifiers=("wbwriter:article",),
        description_fields="<p>Are you sure you want to<br />revise this article's publication?</p>",
        key="unpublish",
        label="Unpublish",
        action_label="Unpublish",
        color=ButtonDefaultColor.PRIMARY,
        icon=WBIcon.UNDO.icon,
    )

    used_article_connections: models.QuerySet[DependantArticle]
    dependant_article_connections: models.QuerySet[DependantArticle]

    """
    /////////////////////////////////////////////////////////////////
    ///                  /FSM Transition Buttons                  ///
    /////////////////////////////////////////////////////////////////
    """

    name = models.CharField(
        max_length=1024,
        unique=True,
        help_text="A unique name to reference this article.",
    )
    slug = models.CharField(max_length=1024, null=True, blank=True)
    title = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
        help_text="The title of the article that is going to be used when imported into other articles."
        + " Defaults to the name of the article when not set.",
    )
    teaser_image = models.ImageField(blank=True, null=True, upload_to="writer/article/teasers")
    created = models.DateField(
        verbose_name="Creation Date",
        auto_now_add=True,
        help_text="The date on which this article has been created.",
    )
    modified = models.DateTimeField(
        verbose_name="Last modification date and time",
        auto_now=True,
        help_text="The last time this article has been edited.",
    )
    content = models.JSONField(
        verbose_name="Content",
        default=dict,
        blank=False,
        null=False,
    )

    i18n = TranslationField(fields=["title", "content", "slug"])

    def _translate_content(self, to_language: str) -> dict:
        new_content = deepcopy(self.content)
        for section_key in new_content.get("sections", {}):
            for content_key, content_value in new_content["sections"][section_key]["content"].items():
                new_content["sections"][section_key]["content"][content_key] = translate_string(
                    content_value, to_language
                )
        return new_content

    type = models.ForeignKey(
        "wbwriter.ArticleType",
        related_name="article",
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )

    publications = GenericRelation(Publication)

    """
    /////////////////////////////////////////////////////////////////
    ///                  Access relevant fields                   ///
    /////////////////////////////////////////////////////////////////
    TODO:
        - Protect the author field. Only the "admin role" can change this.
        - We should have an adjustable value for the minimum number of required peer reviews.
    """
    author = models.ForeignKey(
        "directory.Person",
        related_name="author_articles",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    feedback_contact = models.ForeignKey(
        "directory.Person",
        related_name="feedback_contact_articles",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    reviewer = models.ForeignKey(
        "directory.Person",
        related_name="review_articles",
        help_text="The contact that is currently working on feedback.",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,  # TODO: We should transition back to DRAFT when the contact gets deleted.
    )

    peer_reviewer = models.ForeignKey(
        "directory.Person",
        related_name="peer_review_articles",
        help_text="The peer reviewer who reviewed this article.",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    peer_reviewer_approved = models.BooleanField(default=False)
    qa_reviewer = models.ForeignKey(
        "directory.Person",
        related_name="qa_review_articles",
        help_text="The quality assurance (QA) reviewer who reviewed this article.",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )

    is_private = models.BooleanField(
        blank=False,
        null=False,
        default=False,
        help_text="Signifies whether this article can be seen by all customers on the homepage.",
    )

    """
    /////////////////////////////////////////////////////////////////
    ///                  /Access relevant fields                  ///
    /////////////////////////////////////////////////////////////////
    """

    # QUESTION: What are we going to do with this when IETs become the norm?
    template = models.ForeignKey(
        "wbwriter.Template",
        related_name="articles",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    article_structure = models.JSONField(null=True, blank=True)

    def get_publication_metadata(self) -> dict[str, str]:
        """Returns the title, slug, author, and teasre image for the
        publication as a dictionary.
        """
        return {
            "title": self.title,
            "slug": slugify(self.title),
            "author": self.author,
        }

    def get_tag_detail_endpoint(self):
        return reverse("wbwriter:article-detail", [self.id])

    def get_tag_representation(self):
        return self.name

    """
    /////////////////////////////////////////////////////////////////
    ///                      FSM Transitions                      ///
    /////////////////////////////////////////////////////////////////
    """
    status = FSMField(choices=Status.choices, default=Status.DRAFT)

    @transition(
        status,
        source=[Status.DRAFT],
        target=Status.FEEDBACK,
        permission=is_author,
        custom={"_transition_button": request_feedback_button},
    )
    def requestfeedback(self, by=None):
        """Submit a draft to a reviewer (internal or external) that may give feedback."""
        self.reviewer = self.feedback_contact
        if user := getattr(self.reviewer, "user_account", None):
            send_notification(
                code="wbwriter.article.notify",
                title="Feedback requested",
                body=f"{by.profile} has requested feedback from you.",
                user=user,
                reverse_name="wbwriter:article-detail",
                reverse_args=[self.id],
            )

    @transition(
        status,
        source=[Status.FEEDBACK],
        target=Status.DRAFT,
        permission=is_reviewer,
        custom={"_transition_button": submit_feedback_button},
    )
    def submitfeedback(self, by=None):
        """Submit the feedback to the author."""
        if user := getattr(self.author, "user_account", None):
            send_notification(
                code="wbwriter.article.notify",
                title="Feedback received",
                body=f"{by.profile} has send your their feedback.",
                user=user,
                reverse_name="wbwriter:article-detail",
                reverse_args=[self.id],
            )

    @transition(
        status,
        source=[Status.DRAFT],
        target=Status.PEER_REVIEW,
        permission=is_author,
        custom={"_transition_button": request_peer_review_button},
        conditions=[can_request_peer_review],
    )
    def requestpeerreview(self, by=None):
        """Submit a draft to a peer reviewer that may approve or reject the draft."""
        if user := getattr(self.peer_reviewer, "user_account", None):
            send_notification(
                code="wbwriter.article.notify",
                title="Selected for peer review",
                body=f'You have been selected to review the draft of "{self.title}" from {self.author}.',
                user=user,
                reverse_name="wbwriter:article-detail",
                reverse_args=[self.id],
            )

    @transition(
        status,
        source=[Status.DRAFT],
        target=Status.QA_REVIEW,
        permission=is_author,
        custom={"_transition_button": request_qa_review_button},
        conditions=[can_request_qa_review],
    )
    def requestqareview(self, by=None):
        """Submit a draft to a QA reviewer that may approve or reject the draft."""
        if user := getattr(self.qa_reviewer, "user_account", None):
            send_notification(
                code="wbwriter.article.notify",
                title="QA review requested",
                body=f'{by.profile} has requested your review of "{self.title}".',
                user=user,
                reverse_name="wbwriter:article-detail",
                reverse_args=[self.id],
            )

    @transition(
        status,
        source=[Status.PEER_REVIEW],
        target=Status.QA_REVIEW,
        permission=is_peer_reviewer,
        custom={"_transition_button": peer_approve_button},
    )
    def peerapprove(self, by=None):
        """Approve the article and send it to the QA reviewer."""
        self.peer_reviewer_approved = True
        if user := getattr(self.author, "user_account", None):
            send_notification(
                code="wbwriter.article.notify",
                title="Peer approved your article",
                body=f'{by.profile} has approved your article "{self.title}" and send it to {self.qa_reviewer} for approval.',
                user=user,
                reverse_name="wbwriter:article-detail",
                reverse_args=[self.id],
            )
        if user := getattr(self.qa_reviewer, "user_account", None):
            send_notification(
                code="wbwriter.article.notify",
                title="Selected for QA review",
                body=f'{by.profile} has approved "{self.title}" from {self.author} and you have been selected to review it.',
                user=user,
                reverse_name="wbwriter:article-detail",
                reverse_args=[self.id],
            )

    @transition(
        status,
        source=[Status.PEER_REVIEW],
        target=Status.DRAFT,
        permission=is_peer_reviewer,
        custom={"_transition_button": peer_reject_button},
    )
    def peerreject(self, by=None):
        """Reject the article and send it back to the author."""
        self.peer_reviewer_approved = False
        if user := getattr(self.author, "user_account", None):
            send_notification(
                code="wbwriter.article.notify",
                title=f"{by.profile} rejected your article",
                body=f'{by.profile} has requested changes to your article "{self.title}" and send you their feedback.',
                user=user,
                reverse_name="wbwriter:article-detail",
                reverse_args=[self.id],
            )

    @transition(
        status,
        source=[Status.QA_REVIEW],
        target=Status.DRAFT,
        permission=is_qa_reviewer,
        custom={"_transition_button": qa_reject_draft_button},
    )
    def qareject(self, by=None):
        """Reject the article and return it to the peer reviewer."""
        if user := getattr(self.author, "user_account", None):
            send_notification(
                code="wbwriter.article.notify",
                title="Your article failed the QA review",
                body=f'{by.profile} has rejected "{self.title}".',
                user=user,
                reverse_name="wbwriter:article-detail",
                reverse_args=[self.id],
            )

    @transition(
        status,
        source=[Status.QA_REVIEW],
        target=Status.AUTHOR_APPROVAL,
        permission=is_qa_reviewer,
        custom={"_transition_button": qa_approve_draft_button},
    )
    def qaapprove(self, by=None):
        """Approve the article."""
        if user := getattr(self.author, "user_account", None):
            send_notification(
                code="wbwriter.article.notify",
                title=f"{by.profile} approved your article",
                body=f'{by.profile} has approved "{self.title}". Please, review.',
                user=user,
                reverse_name="wbwriter:article-detail",
                reverse_args=[self.id],
            )

    @transition(
        status,
        source=[Status.AUTHOR_APPROVAL],
        target=Status.QA_REVIEW,
        permission=is_author,
        custom={"_transition_button": author_reject_button},
    )
    def authorreject(self, by=None):
        """Reject the article and return it to the QA reviewer."""
        if user := getattr(self.qa_reviewer, "user_account", None):
            send_notification(
                code="wbwriter.article.notify",
                title=f"{by.profile} did not approve of your review",
                body=f'{by.profile} has rejected your review of "{self.title}".',
                user=user,
                reverse_name="wbwriter:article-detail",
                reverse_args=[self.id],
            )

    @transition(
        status,
        source=[Status.AUTHOR_APPROVAL],
        target=Status.APPROVED,
        permission=is_author,
        custom={"_transition_button": author_approve_button},
        # conditions=[can_qa_approve],
    )
    def authorapprove(self, by=None):
        """Approve the reviewed article."""
        if user := getattr(self.qa_reviewer, "user_account", None):
            send_notification(
                code="wbwriter.article.notify",
                title=f"{by.profile} approved your review",
                body=f'{by.profile} has approved "{self.title}". It is now in the "Approved" state.',
                user=user,
                reverse_name="wbwriter:article-detail",
                reverse_args=[self.id],
            )

    @transition(
        status,
        source=[Status.APPROVED],
        target=Status.PUBLISHED,
        permission=can_administrate_article,
        custom={"_transition_button": publish_button},
    )
    def publish(self, by=None):
        """Publish the article."""
        if self.publications.all().count() == 0 and (user := getattr(self.author, "user_account", None)):
            # Send a notification only on the first time the article has been published.
            # Re-publishing the article should not bother the author.
            send_notification(
                code="wbwriter.article.notify",
                title="Your article has been published",
                body=f'Your article "{self.title}" has been published.',
                user=user,
                reverse_name="wbwriter:article-detail",
                reverse_args=[self.id],
            )
        if self.type is not None:
            generate_publications.delay(self.id)

    def can_publish(self) -> dict[str, str]:
        """Allow only one-off and deep-dive articles to be published."""
        errors = dict()
        if self.status not in [self.Status.APPROVED, self.Status.PUBLISHED]:
            errors["status"] = [gettext_lazy("Status needs to be approved in order to allow publication")]
        if not self.type or self.type.slug not in [
            "one-off-article",
            "deep-dive-article",
            "mid-year-review",
            "year-s-favorites",
        ]:
            errors["type"] = [gettext_lazy("unvalid type for publication")]
        # We ensure the article's parser can be published
        if article_type := self.type:
            for parser in article_type.parsers.all():
                try:
                    parser.parser_class(
                        self._build_dto(),
                        date.today(),
                    ).is_valid()
                except ParserValidationException as e:
                    errors["non_field_errors"] = e.errors
                except ModuleNotFoundError:
                    errors["non_field_errors"] = [gettext_lazy("invalid parser")]
        return errors

    def can_be_published(self) -> bool:
        return not bool(self.can_publish())

    @transition(
        status,
        source=[Status.PUBLISHED],
        target=Status.APPROVED,
        permission=can_administrate_article,
        custom={"_transition_button": unpublish_button},
    )
    def unpublish(self, by=None):
        """Move the article back to the approved state."""

        # we delete existing publication in case the user unpublish it
        Publication.objects.filter(object_id=self.id, content_type=ContentType.objects.get_for_model(self)).delete()

    # @transition(
    #     status,
    #     source=[Status.APPROVED, Status.PUBLISHED],
    #     target=Status.DRAFT,
    #     permission=can_revise,
    #     custom={"_transition_button": revise_button},
    # )
    # def revise(self, by=None):
    #     """Move the article back to the draft state."""
    #     self.peer_reviewer_approved = False
    #     self.peer_reviewer = None
    #     if self.type.slug == "ddq":
    #         self.author = None

    @transition(
        status,
        source=[Status.APPROVED],
        target=Status.DRAFT,
        permission=is_author,
        custom={"_transition_button": authors_revise_button},
    )
    def authorrevise(self, by=None):
        """Move the article back to the draft state."""
        pass

    @transition(
        status,
        source=[Status.APPROVED],
        target=Status.QA_REVIEW,
        permission=is_qa_reviewer,
        custom={"_transition_button": qas_revise_button},
    )
    def qarevise(self, by=None):
        """Move the article back to the qa_review state."""
        pass

    """
    /////////////////////////////////////////////////////////////////
    ///                     /FSM Transitions                      ///
    /////////////////////////////////////////////////////////////////
    """

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        self.article_structure = self.get_sub_article_titles()
        if self.title in ("", None):
            self.title = self.name
        # Set the reviewers
        if not self.peer_reviewer:
            self.peer_reviewer = self.roll_peer()
        if not self.qa_reviewer:
            self.qa_reviewer = self.roll_qa()

        # if self.type and self.type.slug == "ddq":
        #     with suppress(Person.DoesNotExist):
        #         self.qa_reviewer = Person.objects.get(computed_str__icontains="Stefano Rodella")

        create_dependencies(self)
        super().save(*args, **kwargs)

    def _clone(self, user=None, **kwargs) -> "Article":
        from wbwriter.models import MetaInformationInstance

        object_copy = Article.objects.get(id=self.id)
        object_copy.id = None
        object_copy.name += "_clone"
        object_copy.title += " (Clone)"
        if user and (profile := user.profile):
            object_copy.author = profile
        object_copy.save()
        for meta_rel in self.meta_information.all():
            if not MetaInformationInstance.objects.filter(
                article=object_copy, meta_information=meta_rel.meta_information
            ).exists():
                meta_rel.article = object_copy
                meta_rel.id = None
                meta_rel.save()
        for dependant_article in self.dependant_article_connections.all():
            dependant_article.article = object_copy
            dependant_article.id = None
            dependant_article.save()
        for dependant_article_relationship in self.used_article_connections.all():
            dependant_article_relationship.dependant_article = object_copy
            dependant_article_relationship.id = None
            dependant_article_relationship.save()

        return object_copy

    @property
    def system_key(self):
        return f"article-{self.id}"

    def _build_dto(self, **kwargs):
        meta_informations = kwargs.get("meta_information", {})
        tags = kwargs.get("tags", [])
        if self.id:
            if hasattr(self, "meta_information"):
                meta_informations = list(
                    self.meta_information.values(
                        "meta_information__key",
                        "meta_information__name",
                        "meta_information__meta_information_type",
                        "meta_information__boolean_default",
                        "boolean_value",
                    )
                )
            if hasattr(self, "tags"):
                tags = list(self.tags.values_list("id", flat=True))
        return ArticleDTO(
            name=self.name,
            slug=getattr(self, "slug", slugify(self.name)),
            title=getattr(self, "title", self.name),
            teaser_image=getattr(self, "teaser_image", None),
            created=getattr(self, "created", datetime.datetime.now()),
            modified=getattr(self, "modified", datetime.datetime.now()),
            content=self.content,
            is_private=self.is_private,
            article_structure=getattr(
                self, "article_structure", dict()
            ),  # todo make the logic behind article_structure agnostic to the data model.
            status=self.status,
            meta_information=meta_informations,
            tags=tags,
        )

    def roll_peer(self):
        """Return a randomly chosen user profile from the list of peer
        reviewers of the type.

        Returns the author if no type has been assigned or if there are no peer
        reviewers listed on the assigned type.
        """
        if self.type:
            days_into_the_past = global_preferences_registry.manager()["wbwriter__reviewer_roll_days_range"]
            relevant_peers_query = self.type.article.filter(
                peer_reviewer=OuterRef("pk"), created__gte=date.today() - timedelta(days=days_into_the_past)
            ).values("peer_reviewer")
            num_articles = Subquery(relevant_peers_query.annotate(c=Count("*")).values("c")[:1])

            latest_article = Subquery(relevant_peers_query.annotate(c=Max("created")).values("c")[:1])

            peers = (
                self.type.peer_reviewers.exclude(id=self.author.id)
                .annotate(
                    num_articles=Coalesce(num_articles, 0),
                    latest_article=latest_article,
                )
                .order_by("num_articles", "latest_article")
            )
            if peers.exists():
                return peers.first()
        return self.author

    def roll_qa(self):
        """Return a randomly chosen user profile from the list of QA
        reviewers of the type.

        Returns the author if no type has been assigned or if there are no QA
        reviewers listed on the assigned type.
        """
        if self.type:
            days_into_the_past = global_preferences_registry.manager()["wbwriter__reviewer_roll_days_range"]
            relevant_qas_query = self.type.article.filter(
                qa_reviewer=OuterRef("pk"), created__gte=date.today() - timedelta(days=days_into_the_past)
            ).values("qa_reviewer")
            num_articles = Subquery(relevant_qas_query.annotate(c=Count("*")).values("c")[:1])

            latest_article = Subquery(relevant_qas_query.annotate(c=Max("created")).values("c")[:1])

            qas = (
                self.type.qa_reviewers.exclude(id=self.author.id)
                .annotate(
                    num_articles=Coalesce(num_articles, 0),
                    latest_article=latest_article,
                )
                .order_by("num_articles", "latest_article")
            )

            if qas.exists():
                return qas.first()
        return self.author

        qas = self.type.qa_reviewers.exclude(id=self.author.id) if self.author else self.type.qa_reviewers.all()
        if self.type:
            days_into_the_past = global_preferences_registry.manager()["wbwriter__reviewer_roll_days_range"]
            qa_reviewer_id = (
                Article.objects.filter(
                    qa_reviewer__in=qas, created__gte=date.today() - timedelta(days=days_into_the_past)
                )
                .values("qa_reviewer")
                .annotate(num_reviews=Count("*"), latest_review=Max("created"))
                .order_by("num_reviews", "latest_review")
                .values_list("qa_reviewer", flat=True)
            )
            if qa_reviewer_id.exists():
                return Person.objects.get(id=qa_reviewer_id.first())
        return self.author

    def reroll_peer(self):
        """Rerolls the peer reviewer and saves the newly rolled profile as the
        new peer reviewer.
        """
        self.peer_reviewer = self.roll_peer()

    def reroll_qa(self):
        """Rerolls the QA reviewer and saves the newly rolled profile as the
        new QA reviewer.
        """
        self.qa_reviewer = self.roll_qa()

    def reroll_peer_and_qa(self):
        """Rerolls the peer and QA reviewers and saves the newly rolled
        profiles as the new peer and QA reviewers.
        """
        self.peer_reviewer = self.roll_peer()
        self.qa_reviewer = self.roll_qa()

    def generate_pdf(self, user=None):
        empty_template = """<html>
    <head>
        <meta charset="UTF-8">
        <title>{{ self.title }}</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link
            href="https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,300;0,500;0,700;1,300&display=swap"
            rel="stylesheet"
        >
    </head>
    <body style="margin: 0">{{ content|safe }}</body>
</html>"""
        styles = []
        pdf_content = None
        if not self.content or "sections" not in self.content:
            html = template.Template(empty_template).render(
                {"content": "<h1>There seems to be no content to render.</h1>"}
            )
        else:
            content = self.content["sections"][self.content["sectionOrder"][0]]["content"]["content"]
            resolved_content = resolve_content(content, extensions=["sane_lists"], article=self)
            template_context = template.Context({"content": resolved_content})
            if self.type:
                if "ddq" in self.type.slug:
                    # TODO: Replace self.content with the raw_contents equivalent.

                    # If there is a template defined, then render that one and use its styles.
                    if self.template and self.template.template:
                        html = template.Template(self.template.template).render(template_context)

                        styles = [CSS(string=style.style) for style in self.template.styles.all()]
                        if header := self.template.header_template:
                            styles += [CSS(string=style.style) for style in header.styles.all()]
                        if footer := self.template.footer_template:
                            styles += [CSS(string=style.style) for style in footer.styles.all()]

                        pdf_content = PdfGenerator(
                            main_html=html,
                            header_html=self.template.header_template.template,
                            footer_html=self.template.footer_template.template,
                            custom_css=styles,
                            side_margin=self.template.side_margin,
                            extra_vertical_margin=self.template.extra_vertical_margin,
                        ).render_pdf()

                elif (
                    "one-off" in self.type.slug
                    or "deep-dive" in self.type.slug
                    or "mid-year" in self.type.slug
                    or "year-s-favorites" in self.type.slug
                ):
                    parsers = self.type.parsers.all()
                    if parsers.exists():
                        parser = parsers.first().parser_class(self._build_dto(), datetime.date.today())
                        if parser.is_valid(raise_exception=False):
                            pdf_content = parser.get_file()
                        else:
                            template_context["content"] = f"""
                            <p>To generate the PDF, please correct the following errors:</p>
                            <ul>
                            {"".join([f"<li>{error}</li>" for error in parser.errors])}
                            </ul>
                            """
            html = template.Template(empty_template).render(template_context)
        if not pdf_content:
            pdf_content = PdfGenerator(
                main_html=html,
                custom_css=styles,
                side_margin=0,
                extra_vertical_margin=0,
            ).render_pdf()
        document_type, created = DocumentType.objects.get_or_create(name="article")
        filename = f"{self.slug}.pdf"
        content_file = ContentFile(pdf_content, name=filename)
        document, created = Document.objects.update_or_create(
            system_created=True,
            system_key=f"article-{self.id}",
            defaults={
                "document_type": document_type,
                "file": content_file,
                "name": filename,
                "permission_type": Document.PermissionType.INTERNAL,
            },
        )
        document.link(self)

        if not user:
            user = getattr(self.author, "user_account", None)
        if user:
            send_notification(
                code="wbwriter.article.notify",
                title="Your article has been generated",
                body=f'Your article "{self.title}" has been generated.',
                user=user,
                reverse_name="wbwriter:article-detail",
                reverse_args=[self.id],
            )

    def re_find_articles(self) -> list:
        """Search in `content` for load_article template tags using regex and return the match."""
        # TODO: Fix the regex below. I belive that this regex doesn't represent
        #       the full range of possible load_article tremplate tags.
        load_article_regex = "{%[ ]*load_article[ ]+([0-9]*)[ ]*[A-Za-z]*[ ]+(False True)?[ ]*%}"

        if not self.content or "sectionOrder" not in self.content:
            return []

        result = []
        for section_id in self.content["sectionOrder"]:
            for content in self.content["sections"][section_id]["content"].values():
                result.extend(re.findall(load_article_regex, content))

        return result

    def get_article_structure(self, level=0, enumerator=None):
        articles = {
            "title": self.title,
            "anchor": slugify(self.name),
            "enumerator": enumerator,
            "level": level,
            "articles": list(),
        }

        for index, (sub_article_id, _) in enumerate(self.re_find_articles(), start=1):
            _enumerator = f"{enumerator or ''}{index}."
            articles["articles"].append(
                Article.objects.get(id=sub_article_id).get_article_structure(level + 1, _enumerator)
            )

        return articles

    def get_sub_article_titles(self, level=0, enumerator=None):
        mapping = dict()

        for index, (sub_article_id, _) in enumerate(self.re_find_articles(), start=1):
            _enumerator = f"{enumerator or ''}{index}."
            mapping[sub_article_id] = {"enumerator": _enumerator, "level": level}
            _mapping = Article.objects.get(id=sub_article_id).get_sub_article_titles(level + 1, _enumerator)
            mapping.update(**_mapping)
        return mapping

    @classmethod
    def get_endpoint_basename(self):
        return "wbwriter:article"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbwriter:article-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{ title }}"


@shared_task
def generate_pdf_as_task(article_id, user_id=None):
    article = Article.objects.get(id=article_id)
    user = get_user_model().objects.get(id=user_id) if user_id else None
    article.generate_pdf(user=user)
