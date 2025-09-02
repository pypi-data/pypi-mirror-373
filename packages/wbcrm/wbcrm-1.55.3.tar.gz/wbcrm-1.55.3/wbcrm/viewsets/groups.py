from rest_framework.decorators import action
from wbcore import viewsets
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
)
from wbcore.viewsets import RepresentationViewSet

from wbcrm.filters import GroupFilter
from wbcrm.models import Group
from wbcrm.serializers import GroupModelSerializer, GroupRepresentationSerializer
from wbcrm.viewsets.display import GroupModelDisplay
from wbcrm.viewsets.endpoints import GroupEndpointConfig


class GroupRepresentationViewSet(RepresentationViewSet):
    queryset = Group.objects.all()
    search_fields = ("title",)
    serializer_class = GroupRepresentationSerializer


class GroupModelViewSet(viewsets.ModelViewSet):
    LIST_DOCUMENTATION = "wbcrm/markdown/documentation/group.md"
    IDENTIFIER = "wbcrm:group"
    ordering = ("title",)
    ordering_fields = ("title", "members")
    search_fields = ("title",)
    filterset_class = GroupFilter
    queryset = Group.objects.all().prefetch_related("members")
    serializer_class = GroupModelSerializer
    display_config_class = GroupModelDisplay
    endpoint_config_class = GroupEndpointConfig

    @action(methods=["GET"], detail=True)
    def pre_change(self, request, pk=None):
        return viewsets.PreAction(
            message="Do you really want to change this?",
            instance_display=create_simple_display([["title"]]),
        ).to_response()
