from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class GroupEndpointConfig(EndpointViewConfig):
    def get_pre_change_endpoint(self, pk):
        return reverse("wbcrm:group-pre-change", args=[pk], request=self.request)
