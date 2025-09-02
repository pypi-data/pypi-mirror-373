from django.db import models


class PublishableMixin(models.Model):
    def get_publication_metadata(self) -> dict[str, str]:
        raise NotImplementedError("You must implement get_publication_metadata")

    class Meta:
        abstract = True
