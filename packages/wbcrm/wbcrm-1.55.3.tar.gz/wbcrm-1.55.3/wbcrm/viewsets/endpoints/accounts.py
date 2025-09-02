from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class ChildAccountAccountEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbcrm:account-childaccount-list",
            args=[self.view.kwargs["account_id"]],
            request=self.request,
        )


class AccountRoleAccountEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbcrm:account-accountrole-list",
            args=[self.view.kwargs["account_id"]],
            request=self.request,
        )


class InheritedAccountRoleAccountEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None
