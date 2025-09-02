from django.db import models
from django.template import Context
from django.template import Template as DjangoTemplate
from slugify import slugify


class Block(models.Model):
    title = models.CharField(max_length=512)
    key = models.CharField(max_length=512, null=True, blank=True)
    html = models.TextField(default="")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.key = slugify(self.title)
        super().save(*args, **kwargs)

    def parse_parameters(self, parameters):
        for index, parameter in enumerate(self.parameters.all().order_by("order")):
            yield parameter.title, parameter.parse_parameter(parameters[index])

    def render(self, parameters):
        return DjangoTemplate(self.html).render(Context(dict(self.parse_parameters(parameters))))
