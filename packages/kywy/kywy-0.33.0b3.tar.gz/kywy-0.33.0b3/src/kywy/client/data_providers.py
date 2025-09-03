class KawaDataProviders:

    def __init__(self, kawa_client):
        self._k = kawa_client

    def list_data_provider_types(self, details=False):
        url = '{}/backoffice/data-providers/types'.format(self._k.kawa_api_url)
        detailed_providers = self._k.get(url)

        if details:
            return detailed_providers

        provider_types = []

        for data_provider_type in detailed_providers:
            arguments = [arg.get('id') for arg in data_provider_type.get('schema')]

            provider_types.append((data_provider_type.get('name'), arguments))

        return provider_types

    def check_provider_health(self, data_provider):
        data_provider_id = data_provider if isinstance(data_provider, str) else data_provider.get('id')
        url = '{}/backoffice/extraction/provider-health/{}'.format(self._k.kawa_api_url, data_provider_id)
        return self._k.get(url)
