from django.db import models


class Style(models.Model):
    """
    A style is a valid CSS construct.
    """

    title = models.CharField(max_length=255, unique=True)
    style = models.TextField(default="")

    def __str__(self):
        return self.title
