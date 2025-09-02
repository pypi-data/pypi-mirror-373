from wbcore.metadata.configs import endpoints


class StatementsEndpointViewConfig(endpoints.EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None
