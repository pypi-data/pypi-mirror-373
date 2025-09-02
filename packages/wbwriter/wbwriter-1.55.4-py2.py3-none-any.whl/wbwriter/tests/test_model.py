from unittest.mock import patch

import pytest
from django.forms.models import model_to_dict
from django_fsm import has_transition_perm
from wbcore.contrib.authentication.factories import UserFactory
from wbcore.contrib.authentication.models import Permission, User
from wbwriter.factories import (
    ArticleFactory,
    ArticleTypeFactory,
    DependantArticleFactory,
    MetaInformationInstanceFactory,
)
from wbwriter.models import ArticleType, Publication
from wbwriter.models.article import (
    Article,
    DependantArticle,
    can_access_article,
    can_administrate_article,
    can_edit_article_content,
    can_edit_article_meta_data,
    can_edit_article_type,
    can_request_peer_review,
    generate_publications,
)
from wbwriter.models.meta_information import MetaInformationInstance


@pytest.mark.django_db
class TestArticleTransitions:
    @pytest.mark.parametrize("author", [True, False])
    def test_requestfeedback(self, author):
        user = UserFactory(is_superuser=False)
        if author:
            article = ArticleFactory(status=Article.Status.DRAFT, author=user.profile)
            assert has_transition_perm(article.requestfeedback, user) is True
        else:
            article = ArticleFactory(status=Article.Status.DRAFT)
            assert has_transition_perm(article.requestfeedback, user) is False

    @pytest.mark.parametrize("reviewer", [True, False])
    def test_submitfeedback(self, reviewer):
        author_user = UserFactory(is_superuser=False)
        reviewer_user = UserFactory(is_superuser=False)
        article = ArticleFactory(
            status=Article.Status.FEEDBACK,
            author=author_user.profile,
            reviewer=reviewer_user.profile if reviewer else UserFactory().profile,
        )
        if reviewer:
            assert has_transition_perm(article.submitfeedback, reviewer_user) is True
            assert has_transition_perm(article.submitfeedback, author_user) is False
        else:
            article = ArticleFactory(status=Article.Status.FEEDBACK)
            assert has_transition_perm(article.submitfeedback, reviewer_user) is False

    @pytest.mark.parametrize("author", [True, False])
    def test_requestpeerreview(self, author):
        author_user = UserFactory(is_superuser=False)
        reviewer_user = UserFactory(is_superuser=False)
        article_review_approved = ArticleFactory(
            status=Article.Status.DRAFT,
            author=author_user.profile if author else UserFactory().profile,
            reviewer=reviewer_user.profile,
            peer_reviewer_approved=True,
        )
        article_not_review_approved = ArticleFactory(
            status=Article.Status.DRAFT,
            author=author_user.profile if author else UserFactory().profile,
            reviewer=reviewer_user.profile,
            peer_reviewer_approved=False,
        )
        if author:
            assert has_transition_perm(article_review_approved.requestpeerreview, author_user) is False
            assert has_transition_perm(article_review_approved.requestpeerreview, reviewer_user) is False
            assert has_transition_perm(article_not_review_approved.requestpeerreview, author_user) is True
        else:
            assert has_transition_perm(article_review_approved.requestpeerreview, author_user) is False
            assert has_transition_perm(article_not_review_approved.requestpeerreview, author_user) is False

    @pytest.mark.parametrize("author", [True, False])
    def test_requestqareview(self, author):
        author_user = UserFactory(is_superuser=False)
        reviewer_user = UserFactory(is_superuser=False)
        article_review_approved = ArticleFactory(
            status=Article.Status.DRAFT,
            author=author_user.profile if author else UserFactory().profile,
            reviewer=reviewer_user.profile,
            peer_reviewer_approved=True,
        )
        article_not_review_approved = ArticleFactory(
            status=Article.Status.DRAFT,
            author=author_user.profile if author else UserFactory().profile,
            reviewer=reviewer_user.profile,
            peer_reviewer_approved=False,
        )
        if author:
            assert has_transition_perm(article_review_approved.requestqareview, author_user) is True
            assert has_transition_perm(article_not_review_approved.requestqareview, author_user) is False
            assert has_transition_perm(article_review_approved.requestqareview, reviewer_user) is False
        else:
            assert has_transition_perm(article_review_approved.requestqareview, author_user) is False
            assert has_transition_perm(article_not_review_approved.requestqareview, author_user) is False

    def test_peerapprove(self):
        super_user = UserFactory(is_superuser=True)
        author_user = UserFactory(is_superuser=False)
        reviewer_user = UserFactory(is_superuser=False)
        peer_reviewer_user_a = UserFactory(is_superuser=False)
        peer_reviewer_user_b = UserFactory(is_superuser=False)
        article_type_a = ArticleTypeFactory(peer_reviewers=[peer_reviewer_user_a.profile])
        ArticleTypeFactory(peer_reviewers=[peer_reviewer_user_b.profile])

        article = ArticleFactory(
            status=Article.Status.PEER_REVIEW,
            author=author_user.profile,
            reviewer=reviewer_user.profile,
            peer_reviewer=peer_reviewer_user_a.profile,
            type=article_type_a,
        )

        assert has_transition_perm(article.peerapprove, author_user) is False
        assert has_transition_perm(article.peerapprove, reviewer_user) is False
        assert has_transition_perm(article.peerapprove, peer_reviewer_user_b) is False
        assert has_transition_perm(article.peerapprove, peer_reviewer_user_a) is True
        assert has_transition_perm(article.peerapprove, super_user) is True

    def test_peerreject(self):
        super_user = UserFactory(is_superuser=True)
        author_user = UserFactory(is_superuser=False)
        reviewer_user = UserFactory(is_superuser=False)
        peer_reviewer_user_a = UserFactory(is_superuser=False)
        peer_reviewer_user_b = UserFactory(is_superuser=False)
        ArticleTypeFactory(peer_reviewers=[peer_reviewer_user_b.profile])
        article_type_a = ArticleTypeFactory(peer_reviewers=[peer_reviewer_user_a.profile])

        article = ArticleFactory(
            status=Article.Status.PEER_REVIEW,
            author=author_user.profile,
            reviewer=reviewer_user.profile,
            peer_reviewer=peer_reviewer_user_a.profile,
            type=article_type_a,
        )

        assert has_transition_perm(article.peerapprove, author_user) is False
        assert has_transition_perm(article.peerapprove, reviewer_user) is False
        assert has_transition_perm(article.peerapprove, peer_reviewer_user_b) is False
        assert has_transition_perm(article.peerapprove, peer_reviewer_user_a) is True
        assert has_transition_perm(article.peerapprove, super_user) is True

    def test_qa_reject(self):
        super_user = UserFactory(is_superuser=True)
        author_user = UserFactory(is_superuser=False)
        reviewer_user = UserFactory(is_superuser=False)
        peer_reviewer_user = UserFactory(is_superuser=False)
        qa_reviewer_user_a = UserFactory(is_superuser=False)
        qa_reviewer_user_b = UserFactory(is_superuser=False)
        ArticleTypeFactory(qa_reviewers=[qa_reviewer_user_b.profile])

        article_type_a = ArticleTypeFactory(
            peer_reviewers=[peer_reviewer_user.profile],
            qa_reviewers=[qa_reviewer_user_a.profile],
        )

        article = ArticleFactory(
            status=Article.Status.QA_REVIEW,
            author=author_user.profile,
            reviewer=reviewer_user.profile,
            peer_reviewer=peer_reviewer_user.profile,
            qa_reviewer=qa_reviewer_user_a.profile,
            type=article_type_a,
        )

        assert has_transition_perm(article.qareject, author_user) is False
        assert has_transition_perm(article.qareject, reviewer_user) is False
        assert has_transition_perm(article.qareject, peer_reviewer_user) is False
        assert has_transition_perm(article.qareject, qa_reviewer_user_b) is False
        assert has_transition_perm(article.qareject, super_user) is True
        assert has_transition_perm(article.qareject, qa_reviewer_user_a) is True

    def test_qa_approve(self):
        super_user = UserFactory(is_superuser=True)
        author_user = UserFactory(is_superuser=False)
        reviewer_user = UserFactory(is_superuser=False)
        peer_reviewer_user = UserFactory(is_superuser=False)
        qa_reviewer_user_a = UserFactory(is_superuser=False)
        qa_reviewer_user_b = UserFactory(is_superuser=False)
        ArticleTypeFactory(qa_reviewers=[qa_reviewer_user_b.profile])

        article_type_a = ArticleTypeFactory(
            peer_reviewers=[peer_reviewer_user.profile],
            qa_reviewers=[qa_reviewer_user_a.profile],
        )

        article = ArticleFactory(
            status=Article.Status.QA_REVIEW,
            author=author_user.profile,
            reviewer=reviewer_user.profile,
            peer_reviewer=peer_reviewer_user.profile,
            qa_reviewer=qa_reviewer_user_a.profile,
            type=article_type_a,
        )

        assert has_transition_perm(article.qaapprove, author_user) is False
        assert has_transition_perm(article.qaapprove, reviewer_user) is False
        assert has_transition_perm(article.qaapprove, peer_reviewer_user) is False
        assert has_transition_perm(article.qaapprove, qa_reviewer_user_b) is False
        assert has_transition_perm(article.qaapprove, super_user) is True
        assert has_transition_perm(article.qaapprove, qa_reviewer_user_a) is True

    def test_authorreject(self):
        super_user = UserFactory(is_superuser=True)
        author_user = UserFactory(is_superuser=False)
        reviewer_user = UserFactory(is_superuser=False)
        peer_reviewer_user = UserFactory(is_superuser=False)
        qa_reviewer_user = UserFactory(is_superuser=False)
        article_type_a = ArticleTypeFactory(
            peer_reviewers=[peer_reviewer_user.profile],
            qa_reviewers=[qa_reviewer_user.profile],
        )
        article = ArticleFactory(
            status=Article.Status.AUTHOR_APPROVAL,
            author=author_user.profile,
            reviewer=reviewer_user.profile,
            peer_reviewer=peer_reviewer_user.profile,
            qa_reviewer=qa_reviewer_user.profile,
            type=article_type_a,
        )

        assert has_transition_perm(article.authorreject, reviewer_user) is False
        assert has_transition_perm(article.authorreject, peer_reviewer_user) is False
        assert has_transition_perm(article.authorreject, qa_reviewer_user) is False
        assert has_transition_perm(article.authorreject, super_user) is True
        assert has_transition_perm(article.authorreject, author_user) is True

    def test_authorapprove(self):
        super_user = UserFactory(is_superuser=True)
        author_user = UserFactory(is_superuser=False)
        reviewer_user = UserFactory(is_superuser=False)
        peer_reviewer_user = UserFactory(is_superuser=False)
        qa_reviewer_user = UserFactory(is_superuser=False)
        article_type_a = ArticleTypeFactory(
            peer_reviewers=[peer_reviewer_user.profile],
            qa_reviewers=[qa_reviewer_user.profile],
        )
        article = ArticleFactory(
            status=Article.Status.AUTHOR_APPROVAL,
            author=author_user.profile,
            reviewer=reviewer_user.profile,
            peer_reviewer=peer_reviewer_user.profile,
            qa_reviewer=qa_reviewer_user.profile,
            type=article_type_a,
        )

        assert has_transition_perm(article.authorapprove, reviewer_user) is False
        assert has_transition_perm(article.authorapprove, peer_reviewer_user) is False
        assert has_transition_perm(article.authorapprove, qa_reviewer_user) is False
        assert has_transition_perm(article.authorapprove, super_user) is True
        assert has_transition_perm(article.authorapprove, author_user) is True

    def test_publish(self):
        super_user = UserFactory(is_superuser=True)
        author_user = UserFactory(is_superuser=False)
        reviewer_user = UserFactory(is_superuser=False)
        peer_reviewer_user = UserFactory(is_superuser=False)
        qa_reviewer_user = UserFactory(is_superuser=False)
        can_publish_user: User = UserFactory(is_superuser=False)
        can_publish_user.user_permissions.add(Permission.objects.get(codename="administrate_article"))

        article_type = ArticleTypeFactory(
            peer_reviewers=[peer_reviewer_user.profile],
            qa_reviewers=[qa_reviewer_user.profile],
            label="one-off-article",
        )
        article = ArticleFactory(
            status=Article.Status.APPROVED,
            author=author_user.profile,
            reviewer=reviewer_user.profile,
            peer_reviewer=peer_reviewer_user.profile,
            qa_reviewer=qa_reviewer_user.profile,
            type=article_type,
        )
        assert has_transition_perm(article.publish, reviewer_user) is False
        assert has_transition_perm(article.publish, peer_reviewer_user) is False
        assert has_transition_perm(article.publish, qa_reviewer_user) is False
        assert has_transition_perm(article.publish, author_user) is False
        assert has_transition_perm(article.publish, super_user) is True
        assert has_transition_perm(article.publish, can_publish_user) is True

    def test_unpublish(self):
        super_user = UserFactory(is_superuser=True)
        author_user = UserFactory(is_superuser=False)
        reviewer_user = UserFactory(is_superuser=False)
        peer_reviewer_user = UserFactory(is_superuser=False)
        qa_reviewer_user = UserFactory(is_superuser=False)
        can_publish_user: User = UserFactory(is_superuser=False)
        can_publish_user.user_permissions.add(Permission.objects.get(codename="administrate_article"))

        article_type = ArticleTypeFactory(
            peer_reviewers=[peer_reviewer_user.profile],
            qa_reviewers=[qa_reviewer_user.profile],
            label="one-off-article",
        )
        article = ArticleFactory(
            status=Article.Status.PUBLISHED,
            author=author_user.profile,
            reviewer=reviewer_user.profile,
            peer_reviewer=peer_reviewer_user.profile,
            qa_reviewer=qa_reviewer_user.profile,
            type=article_type,
        )
        assert has_transition_perm(article.unpublish, reviewer_user) is False
        assert has_transition_perm(article.unpublish, peer_reviewer_user) is False
        assert has_transition_perm(article.unpublish, qa_reviewer_user) is False
        assert has_transition_perm(article.unpublish, author_user) is False
        assert has_transition_perm(article.unpublish, super_user) is True
        assert has_transition_perm(article.unpublish, can_publish_user) is True

    def test_authorrevise(self):
        super_user = UserFactory(is_superuser=True)
        author_user = UserFactory(is_superuser=False)
        reviewer_user = UserFactory(is_superuser=False)
        peer_reviewer_user = UserFactory(is_superuser=False)
        qa_reviewer_user = UserFactory(is_superuser=False)
        administrate_user: User = UserFactory(is_superuser=False)
        administrate_user.user_permissions.add(Permission.objects.get(codename="administrate_article"))

        article_type = ArticleTypeFactory(
            peer_reviewers=[peer_reviewer_user.profile],
            qa_reviewers=[qa_reviewer_user.profile],
            label="one-off-article",
        )
        article = ArticleFactory(
            status=Article.Status.APPROVED,
            author=author_user.profile,
            reviewer=reviewer_user.profile,
            peer_reviewer=peer_reviewer_user.profile,
            qa_reviewer=qa_reviewer_user.profile,
            type=article_type,
        )
        assert has_transition_perm(article.authorrevise, reviewer_user) is False
        assert has_transition_perm(article.authorrevise, peer_reviewer_user) is False
        assert has_transition_perm(article.authorrevise, qa_reviewer_user) is False
        assert has_transition_perm(article.authorrevise, author_user) is True
        assert has_transition_perm(article.authorrevise, super_user) is True
        assert has_transition_perm(article.authorrevise, administrate_user) is True

    def test_qarevise(self):
        super_user = UserFactory(is_superuser=True)
        author_user = UserFactory(is_superuser=False)
        reviewer_user = UserFactory(is_superuser=False)
        peer_reviewer_user = UserFactory(is_superuser=False)
        qa_reviewer_user_a = UserFactory(is_superuser=False)
        qa_reviewer_user_b = UserFactory(is_superuser=False)
        administrate_user: User = UserFactory(is_superuser=False)
        administrate_user.user_permissions.add(Permission.objects.get(codename="administrate_article"))

        article_type = ArticleTypeFactory(
            peer_reviewers=[peer_reviewer_user.profile],
            qa_reviewers=[qa_reviewer_user_a.profile, qa_reviewer_user_b.profile],
            label="one-off-article",
        )
        article = ArticleFactory(
            status=Article.Status.APPROVED,
            author=author_user.profile,
            reviewer=reviewer_user.profile,
            peer_reviewer=peer_reviewer_user.profile,
            qa_reviewer=qa_reviewer_user_a.profile,
            type=article_type,
        )
        assert has_transition_perm(article.qarevise, reviewer_user) is False
        assert has_transition_perm(article.qarevise, peer_reviewer_user) is False
        assert has_transition_perm(article.qarevise, qa_reviewer_user_a) is True
        assert has_transition_perm(article.qarevise, qa_reviewer_user_b) is True
        assert has_transition_perm(article.qarevise, author_user) is False
        assert has_transition_perm(article.qarevise, super_user) is True
        assert has_transition_perm(article.qarevise, administrate_user) is True


@pytest.mark.django_db
class TestArticlePermissions:
    def test_can_administrate_article(self):
        super_user: User = UserFactory(is_superuser=True)
        article_admin_user: User = UserFactory(is_superuser=False)
        article_admin_user.user_permissions.add(Permission.objects.get(codename="administrate_article"))
        unalligned_user: User = UserFactory(is_superuser=False)

        article = ArticleFactory()
        assert can_administrate_article(article, super_user)
        assert can_administrate_article(article, article_admin_user)
        assert not can_administrate_article(article, unalligned_user)

    def test_can_publish_articles(self):
        super_user: User = UserFactory(is_superuser=True)
        article_admin_user: User = UserFactory(is_superuser=False)
        article_admin_user.user_permissions.add(Permission.objects.get(codename="administrate_article"))
        unalligned_user: User = UserFactory(is_superuser=False)

        article: Article = ArticleFactory()
        assert can_administrate_article(article, super_user)
        assert can_administrate_article(article, article_admin_user)
        assert not can_administrate_article(article, unalligned_user)

    @patch.object(Publication, "create_or_update_from_parser_and_object")
    def test_can_be_published(self, mock_fct):
        article_a: Article = ArticleFactory(type=ArticleTypeFactory(label="One Off Article"))

        assert article_a.can_be_published() is False
        generate_publications(article_a.id)
        assert mock_fct.call_count == 0

        article_a.status = Article.Status.APPROVED
        article_a.save()
        assert article_a.can_be_published()
        generate_publications(article_a.id)
        assert mock_fct.call_count == 1

        article_b: Article = ArticleFactory(
            status=Article.Status.APPROVED, type=ArticleTypeFactory(label="Deep Dive Article")
        )
        article_c: Article = ArticleFactory(
            status=Article.Status.APPROVED, type=ArticleTypeFactory(label="Mid Year Review")
        )
        article_d: Article = ArticleFactory(
            status=Article.Status.APPROVED, type=ArticleTypeFactory(label="Unalligned Article")
        )
        assert article_a.can_be_published()
        assert article_b.can_be_published()
        assert article_c.can_be_published()
        generate_publications(article_a.id)
        generate_publications(article_b.id)
        generate_publications(article_c.id)
        assert mock_fct.call_count == 4
        assert not article_d.can_be_published()
        generate_publications(article_d.id)
        assert mock_fct.call_count == 4

    def test_can_access_article(self):
        super_user: User = UserFactory(is_superuser=True)
        reviewer_user: User = UserFactory(is_superuser=False)
        is_qa_reviewer_user: User = UserFactory(is_superuser=False)
        is_peer_reviewer_user: User = UserFactory(is_superuser=False)
        user_can_administrate_article: User = UserFactory(is_superuser=False)
        unalligned_user: User = UserFactory(is_superuser=False)

        user_can_administrate_article.user_permissions.add(Permission.objects.get(codename="administrate_article"))
        article_type: ArticleType = ArticleTypeFactory(
            peer_reviewers=[is_peer_reviewer_user.profile], qa_reviewers=[is_qa_reviewer_user.profile]
        )
        article: Article = ArticleFactory(type=article_type, reviewer=reviewer_user.profile)

        assert can_access_article(article, super_user)
        # assert can_access_article(article, employee_user)
        assert can_access_article(article, is_qa_reviewer_user)
        assert can_access_article(article, is_peer_reviewer_user)
        assert can_access_article(article, user_can_administrate_article)
        assert not can_access_article(article, unalligned_user)

    def test_can_edit_article_author(self):
        self.test_can_administrate_article()

    def test_can_edit_article_content(self):
        user = UserFactory(is_superuser=False)
        user_unalligned = UserFactory(is_superuser=False)
        user_su = UserFactory(is_superuser=True)

        article_type = ArticleTypeFactory(peer_reviewers=[user.profile], qa_reviewers=[user.profile])

        article_draft: Article = ArticleFactory(status=Article.Status.DRAFT, author=user.profile)
        article_feedback: Article = ArticleFactory(status=Article.Status.FEEDBACK, reviewer=user.profile)
        article_peer_review: Article = ArticleFactory(
            status=Article.Status.PEER_REVIEW, peer_reviewer=user.profile, type=article_type
        )
        article_qa_review: Article = ArticleFactory(
            status=Article.Status.QA_REVIEW, qa_reviewer=user.profile, type=article_type
        )
        article_approved: Article = ArticleFactory(status=Article.Status.APPROVED)

        assert can_edit_article_content(article_draft, user)
        assert not can_edit_article_content(article_draft, user_unalligned)
        assert can_edit_article_content(article_feedback, user)
        assert not can_edit_article_content(article_feedback, user_unalligned)
        assert can_edit_article_content(article_peer_review, user)
        assert not can_edit_article_content(article_peer_review, user_unalligned)
        assert can_edit_article_content(article_qa_review, user)
        assert not can_edit_article_content(article_qa_review, user_unalligned)
        assert can_edit_article_content(article_approved, user_su)
        assert not can_edit_article_content(article_approved, user_unalligned)

    def test_can_edit_article_meta_data(self):
        user = UserFactory(is_superuser=False)
        user_unalligned = UserFactory(is_superuser=False)

        article_type = ArticleTypeFactory(peer_reviewers=[user.profile], qa_reviewers=[user.profile])

        article_draft: Article = ArticleFactory(status=Article.Status.DRAFT, author=user.profile)
        article_feedback: Article = ArticleFactory(status=Article.Status.FEEDBACK, reviewer=user.profile)
        article_peer_review: Article = ArticleFactory(
            status=Article.Status.PEER_REVIEW, peer_reviewer=user.profile, type=article_type
        )
        article_qa_review: Article = ArticleFactory(
            status=Article.Status.QA_REVIEW, qa_reviewer=user.profile, type=article_type
        )

        assert can_edit_article_meta_data(article_draft, user=user)
        assert not can_edit_article_meta_data(article_draft, user=user_unalligned)
        assert can_edit_article_meta_data(article_feedback, user=user)
        assert not can_edit_article_meta_data(article_feedback, user=user_unalligned)
        assert can_edit_article_meta_data(article_peer_review, user=user)
        assert not can_edit_article_meta_data(article_peer_review, user=user_unalligned)
        assert can_edit_article_meta_data(article_qa_review, user=user)
        assert not can_edit_article_meta_data(article_qa_review, user=user_unalligned)

    def test_can_edit_article_type(self):
        user = UserFactory(is_superuser=False)
        user_unalligned = UserFactory(is_superuser=False)
        article_draft: Article = ArticleFactory(status=Article.Status.DRAFT, author=user.profile)
        article_feedback: Article = ArticleFactory(status=Article.Status.FEEDBACK, author=user.profile)

        assert can_edit_article_type(article_draft, user)
        assert not can_edit_article_type(article_feedback, user)
        assert not can_edit_article_type(article_draft, user_unalligned)

    @pytest.mark.parametrize("peer_reviewer_approved", [True, False])
    def test_can_request_peer_review(self, peer_reviewer_approved):
        article = ArticleFactory(peer_reviewer_approved=peer_reviewer_approved)
        if peer_reviewer_approved:
            assert not can_request_peer_review(article)
        else:
            assert can_request_peer_review(article)


@pytest.mark.django_db
class TestArticleCloning:
    def test_clone(self, user):
        article = ArticleFactory()
        article = Article.objects.get(
            id=article.id
        )  # To get updated tag_detail_endpoint and tag_representation from db
        meta_information_instance = MetaInformationInstanceFactory(article=article)
        dependender_relationship = DependantArticleFactory(article=article)
        dependendee_relationship = DependantArticleFactory(dependant_article=article)
        assert Article.objects.count() == 3
        assert DependantArticle.objects.count() == 2
        assert MetaInformationInstance.objects.count() == 1

        cloned_article = article.clone(user=user)

        # Article was correctly cloned
        article_dict = model_to_dict(article)
        del article_dict["id"]
        del article_dict["teaser_image"]
        article_clone_dict = model_to_dict(cloned_article)
        assert article_clone_dict
        del article_clone_dict["id"]
        del article_clone_dict["teaser_image"]
        article_dict["name"] += "_clone"
        article_dict["slug"] += "-clone"
        article_dict["slug_en_us"] += "-clone"
        article_dict["slug_i18n"] += "-clone"
        article_dict["title"] += " (Clone)"
        article_dict["title_i18n"] += " (Clone)"
        article_dict["title_en_us"] += " (Clone)"
        article_dict["author"] = user.profile.id
        assert article_dict == article_clone_dict
        assert Article.objects.count() == 4

        # Related dependant articles were correctly cloned
        dependender_relationship_dict = model_to_dict(dependender_relationship)
        del dependender_relationship_dict["id"]
        dependender_relationship_clone_dict = model_to_dict(DependantArticle.objects.get(id=3))
        assert dependender_relationship_clone_dict
        del dependender_relationship_clone_dict["id"]
        dependender_relationship_clone_dict["article"] = article.id
        assert dependender_relationship_dict == dependender_relationship_clone_dict

        dependendee_relationship_dict = model_to_dict(dependendee_relationship)
        del dependendee_relationship_dict["id"]
        dependendee_relationship_clone_dict = model_to_dict(DependantArticle.objects.get(id=4))
        assert dependendee_relationship_clone_dict
        del dependendee_relationship_clone_dict["id"]
        dependendee_relationship_clone_dict["dependant_article"] = article.id
        assert dependendee_relationship_dict == dependendee_relationship_clone_dict

        assert DependantArticle.objects.count() == 4

        # Related meta information instances were correctly cloned
        meta_information_instance_dict = model_to_dict(meta_information_instance)
        del meta_information_instance_dict["id"]
        meta_information_instance_clone_dict = model_to_dict(MetaInformationInstance.objects.last())
        assert meta_information_instance_clone_dict
        del meta_information_instance_clone_dict["id"]
        meta_information_instance_clone_dict["article"] = article.id
        assert meta_information_instance_dict == meta_information_instance_clone_dict
        assert MetaInformationInstance.objects.count() == 2
