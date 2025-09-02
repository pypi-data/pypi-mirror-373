from wbcore.metadata.configs.titles import TitleViewConfig

from wbwriter.models import Publication


class PublicationTitleConfig(TitleViewConfig):
    def get_list_title(self):
        title = "Publications"
        if self.request.GET.get("content_type") and self.request.GET.get("object_id"):
            publications = Publication.objects.filter(
                content_type__id=self.request.GET.get("content_type"), object_id=self.request.GET.get("object_id")
            )
            if publications.exists():
                pub = publications.first()
                content_type_label = pub.content_type.model
                content_title = pub.content_object.get_publication_metadata()["title"]
                title = f"{title} of {content_type_label}: {content_title}"

        return title
