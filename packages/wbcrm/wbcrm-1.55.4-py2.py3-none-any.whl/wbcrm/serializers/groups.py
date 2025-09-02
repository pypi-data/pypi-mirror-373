from wbcore import serializers as wb_serializers
from wbcore.contrib.directory.serializers import EntryRepresentationSerializer

from ..models import Group


class GroupRepresentationSerializer(wb_serializers.RepresentationSerializer):
    endpoint = "wbcrm:grouprepresentation-list"
    _detail = wb_serializers.HyperlinkField(reverse_name="wbcrm:group-detail")

    class Meta:
        model = Group
        fields = (
            "id",
            "_detail",
            "title",
        )


class GroupModelSerializer(wb_serializers.ModelSerializer):
    _members = EntryRepresentationSerializer(source="members", many=True)

    class Meta:
        model = Group
        fields = (
            "id",
            "title",
            "members",
            "_members",
        )
