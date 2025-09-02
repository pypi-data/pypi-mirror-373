from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class ProductCompanyRelationshipEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbcrm:company-interestedproduct-list", args=[self.view.kwargs["company_id"]], request=self.request
        )
