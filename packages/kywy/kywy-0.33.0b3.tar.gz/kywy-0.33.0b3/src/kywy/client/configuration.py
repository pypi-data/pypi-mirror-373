class KawaConfiguration:

    def __init__(self, kawa_client):
        self._k = kawa_client
        self._configuration_resource_base_url = 'backoffice/configuration'

    def _load_configuration(self, configuration_type):
        try:
            return self._k.get(
                '{}/{}/{}'.format(self._k.kawa_api_url, self._configuration_resource_base_url, configuration_type))
        except:
            return None

    def load_flight_configuration(self):
        return self._load_configuration('ArrowFlightConfiguration')

    def replace_flight_configuration(self, host, port, tls=False, polling_interval=30):
        return self._k.commands.replace_configuration(
            configuration_type='ArrowFlightConfiguration',
            payload={
                'host': host,
                'port': int(port),
                'tls': bool(tls),
                'pollingIntervalSeconds': int(polling_interval)
            }
        )
