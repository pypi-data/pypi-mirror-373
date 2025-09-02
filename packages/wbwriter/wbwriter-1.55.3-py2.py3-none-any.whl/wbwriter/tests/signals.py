from django.dispatch import receiver
from dynamic_preferences.registries import global_preferences_registry
from wbcore.test.signals import custom_update_kwargs
from wbwriter.models import Article
from wbwriter.viewsets import ArticleModelViewSet, ReviewerArticleModelViewSet


@receiver(custom_update_kwargs, sender=ReviewerArticleModelViewSet)
def receive_kwargs_reviewer_article(sender, *args, **kwargs):
    if (obj := kwargs.get("obj_factory")) and (user := kwargs.get("user")):
        obj.reviewer = user.profile
        obj.status = Article.Status.FEEDBACK
        obj.author.employers.set({global_preferences_registry.manager()["directory__main_company"]})
        obj.save()
    return {}


@receiver(custom_update_kwargs, sender=ArticleModelViewSet)
def receive_kwargs_article(sender, *args, **kwargs):
    if obj := kwargs.get("obj_factory"):
        obj.author.employers.set({global_preferences_registry.manager()["directory__main_company"]})
        obj.save()
    return {}
