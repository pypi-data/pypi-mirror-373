from wbcore.serializers import ModelSerializer, RepresentationSerializer

from wbwriter.models import ArticleType


class ArticleTypeModelSerializer(ModelSerializer):
    class Meta:
        model = ArticleType
        fields = ("id", "label", "peer_reviewers", "qa_reviewers")


class ArticleTypeRepresentationSerializer(RepresentationSerializer):
    class Meta:
        model = ArticleType
        fields = ("id", "label")
