from django.db import models
from django.dispatch import receiver
from wbcore.models import WBModel


class MetaInformation(WBModel):
    class MetaInformationType(models.TextChoices):
        # NOTE: This is just one value for now. However, this structure allows us to add more data type in the future.
        BOOLEAN = "BOOLEAN", "Boolean"

    article_type = models.ManyToManyField(to="wbwriter.ArticleType", related_name="meta_information")
    name = models.CharField(max_length=255, null=False, blank=False, unique=True)
    key = models.CharField(max_length=255, null=False, blank=False, unique=True)
    meta_information_type = models.CharField(
        max_length=24, choices=MetaInformationType.choices, default=MetaInformationType.BOOLEAN
    )
    boolean_default = models.BooleanField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.key})"

    class Meta:
        verbose_name = "Meta Information"
        verbose_name_plural = "Meta Information"

    @classmethod
    def get_endpoint_basename(self):
        return "wbwriter:metainformation"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbwriter:metainformation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{name}} ({{key}})"


class MetaInformationInstance(WBModel):
    article = models.ForeignKey(to="wbwriter.Article", related_name="meta_information", on_delete=models.CASCADE)

    meta_information = models.ForeignKey(
        to="wbwriter.MetaInformation", related_name="instances", on_delete=models.CASCADE
    )
    boolean_value = models.BooleanField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.meta_information} / {self.article}: {self.boolean_value}"

    class Meta:
        verbose_name = "Meta Information Instance"
        verbose_name_plural = "Meta Information Instances"

        constraints = [
            models.UniqueConstraint(fields=["meta_information", "article"], name="unique_meta_information_article")
        ]

    @classmethod
    def get_endpoint_basename(self):
        return "wbwriter:metainformationinstance"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbwriter:metainformationinstance-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{meta_information.name}}"


@receiver(models.signals.post_save, sender="wbwriter.Article")
def create_meta_information_instances(sender, instance, created, **kwargs):
    if created and instance.type:
        for meta_information in instance.type.meta_information.all():
            MetaInformationInstance.objects.get_or_create(
                meta_information=meta_information,
                article=instance,
                defaults={"boolean_value": meta_information.boolean_default},
            )
