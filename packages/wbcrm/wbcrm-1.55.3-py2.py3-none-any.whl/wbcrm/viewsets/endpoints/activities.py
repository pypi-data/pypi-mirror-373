from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class ActivityEndpointConfig(EndpointViewConfig):
    def get_create_endpoint(self, **kwargs):
        user_id = self.request.user.profile.id
        base_url = "wbcrm:activity-list"
        filter_url = f"?participants={user_id}"

        if participants := self.request.GET.get("participants", None):
            filter_url += f",{participants}"
        if companies := self.request.GET.get("companies", None):
            filter_url += f"&companies={companies}"
        return f"{reverse(base_url, args=[], request=self.request)}{filter_url}"

    def get_delete_endpoint(self, **kwargs):
        if "pk" in self.view.kwargs and (self.view.is_private_for_user or self.view.is_confidential_for_user):
            return None
        return super().get_delete_endpoint(**kwargs)


class ActivityParticipantModelEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse("wbcrm:activity-participant-list", args=[self.view.kwargs["activity_id"]], request=self.request)

    def get_create_endpoint(self, **kwargs):
        if "activity_id" in self.view.kwargs:
            return f"{super().get_create_endpoint(**kwargs)}?activity_id={self.view.kwargs['activity_id']}"
        return super().get_create_endpoint(**kwargs)
