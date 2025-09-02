from django.db import models


class Template(models.Model):
    """
    A template consists of n styles and a template which holds a {{content}} templatetag where the content is rendered
    into.
    """

    title = models.CharField(max_length=255, unique=True)
    template = models.TextField(default="")

    header_template = models.ForeignKey(
        "Template",
        null=True,
        blank=True,
        related_name="header_templates",
        on_delete=models.SET_NULL,
    )
    footer_template = models.ForeignKey(
        "Template",
        null=True,
        blank=True,
        related_name="footer_templates",
        on_delete=models.SET_NULL,
    )

    styles = models.ManyToManyField(to="wbwriter.Style", related_name="templates", blank=True)

    side_margin = models.FloatField(default=2.5)
    extra_vertical_margin = models.FloatField(default=10)

    def __str__(self):
        return self.title
