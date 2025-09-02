from wbcore.metadata.configs.endpoints import EndpointViewConfig


class ConsolidatedInvoiceEndpointConfig(EndpointViewConfig):
    def _get_instance_endpoint(self, **kwargs):
        return "{{casted_endpoint}}"
