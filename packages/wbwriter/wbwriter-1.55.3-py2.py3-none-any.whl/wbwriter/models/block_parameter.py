import json

from django.db import models


class BlockParameter(models.Model):
    block = models.ForeignKey(to="wbwriter.Block", related_name="parameters", on_delete=models.CASCADE)

    order = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    many = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.block.title}: {self.title}"

    def parse_parameter(self, parameter):
        if self.many:
            return json.loads(parameter)
        return parameter
