from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class MetaInformationInstanceEndpointConfig(EndpointViewConfig):
    def get_create_endpoint(self, **kwargs):
        return None

    def get_endpoint(self, **kwargs):
        if article_id := self.view.kwargs.get("article_id", None):
            return reverse(
                "wbwriter:metainformationinstancearticle-list", kwargs={"article_id": article_id}, request=self.request
            )
        return reverse("wbwriter:metainformationinstance-list", request=self.request)
