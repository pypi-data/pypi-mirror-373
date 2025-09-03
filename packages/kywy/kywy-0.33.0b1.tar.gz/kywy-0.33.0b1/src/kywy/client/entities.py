import urllib.parse


class KawaEntities:

    def __init__(self, kawa_client):
        self._k = kawa_client
        self._entity_kind = None

    def entities_of_kind(self, entity_kind):
        self._entity_kind = entity_kind
        return self

    def conversations(self):
        self._entity_kind = 'conversations'
        return self

    def perimeters(self):
        self._entity_kind = 'perimeters'
        return self

    def attributes(self):
        self._entity_kind = 'attributes'
        return self

    def layouts(self):
        self._entity_kind = 'layouts'
        return self

    def scripts(self):
        self._entity_kind = 'scripts'
        return self

    def etl_pipelines(self):
        self._entity_kind = 'etl-pipelines'
        return self

    def applications(self):
        self._entity_kind = 'applications'
        return self

    def extended_applications(self):
        self._entity_kind = 'extended-applications'
        return self

    def data_categories(self):
        self._entity_kind = 'data-categories'
        return self

    def data_providers(self):
        self._entity_kind = 'data-providers'
        return self

    def datasources(self):
        self._entity_kind = 'datasources'
        return self

    def control_panels(self):
        self._entity_kind = 'extended-control-panels/sheets'
        return self

    def dashboards(self):
        self._entity_kind = 'dashboards'
        return self

    def sheets(self):
        self._entity_kind = 'sheets'
        return self

    def views(self):
        self._entity_kind = 'extended-views'
        return self

    def principals(self):
        self._entity_kind = 'principals'
        return self

    def workspaces(self):
        self._entity_kind = 'workspaces'
        return self

    def script_runners(self):
        self._entity_kind = 'script-runners'
        return self

    def secrets(self):
        self._entity_kind = 'secret'
        return self

    def python_private_joins(self):
        self._entity_kind = 'python-private-joins'
        return self

    def agents(self):
        self._entity_kind = 'agents'
        return self

    def list_entities(self):
        return self._k.get('{}/backoffice/{}'.format(self._k.kawa_api_url, self._entity_kind.lower()))

    def list_entities_by_name(self, name):
        return self._k.get(
            f'{self._k.kawa_api_url}/backoffice/{self._entity_kind.lower()}',
            params={'name': name}
        )

    def find_entity_by_tag(self, tag):
        try:
            url_encoded_tag = urllib.parse.quote_plus(tag)
            url = '{}/backoffice/{}?tag={}'.format(
                self._k.kawa_api_url,
                self._entity_kind.lower(),
                url_encoded_tag
            )
            entities = self._k.get(url)
            return entities[0] if entities else None
        except Exception:
            return None

    def find_entity_by_id(self, id):
        try:
            return self.get_entity_by_id(id)
        except Exception:
            return None

    def get_entity_by_id(self, id):
        return self._k.get('{}/backoffice/{}/{}'.format(self._k.kawa_api_url, self._entity_kind.lower(), id))

    def list_entity_names(self):
        return [e.get('displayInformation').get('displayName') for e in self.list_entities()]

    def get_extraction_metadata(self, extraction_adapter_name: str, extraction_adapter_configuration: dict):
        json = {'extractionAdapterName': extraction_adapter_name,
                'extractionAdapterConfiguration': extraction_adapter_configuration,
                'indicators': [],
                'rowMapperConfigList': []}
        return self._k.post('{}/backoffice/extraction/metadata'.format(self._k.kawa_api_url), data=json)

    def get_datasource_schema(self, datasource_id=None):
        return self._k.get('{}/backoffice/datasources/{}/schema'.format(self._k.kawa_api_url, datasource_id))

    def get_datasource_health_report(self, datasource_id=None):
        return self._k.get('{}/backoffice/datasources/health-report/v2/{}'.format(self._k.kawa_api_url, datasource_id))

    def get_sheet_schema(self, sheet_id=None):
        return (self._k
                .get('{}/backoffice/sheets/{}/schema'.format(self._k.kawa_api_url, sheet_id))
                .get('schema'))

    def get_sheet_parameters(self, sheet_id=None):
        control_panel = self._k.get(f'{self._k.kawa_api_url}/backoffice/extended-control-panels/sheets/{sheet_id}')

        all_parameters = []
        for control in control_panel.get('controls', []):
            parameter_id = control.get('parameterId')
            control_name = control.get('displayInformation').get('displayName')

            for parameter in control_panel.get('parameters', []):
                if parameter.get('id') == parameter_id:
                    parameter_type = parameter.get('type')
                    all_parameters.append({
                        'type': parameter_type,
                        'name': control_name,
                        'id': parameter_id
                    })

        return all_parameters

    def get_entity(self, entity_id_or_name=None):
        if not entity_id_or_name:
            return None

        entity_id_or_name = str(entity_id_or_name)

        if self._entity_kind == 'attributes':
            # Attributes are saved in upper case so if we want to search for some,
            # we need to translate the searched for name to upper case as well.
            entity_name = entity_id_or_name.upper()

        entities_with_matching_name = self.list_entities_by_name(entity_id_or_name)

        if entities_with_matching_name:
            return entities_with_matching_name[0]

        return self.find_entity_by_id(entity_id_or_name)

    def get_entity_id(self, entity_name):
        entity = self.get_entity(entity_name)
        if entity:
            return entity.get('id')

    def find_first_entity_by_attribute(self, attribute, value):
        for entity in self.list_entities():
            if entity.get(attribute) == value:
                return entity

    def find_entities_by_attribute(self, attribute, value_list):
        res = []
        value_set = set(value_list)
        for entity in self.list_entities():
            if entity.get(attribute) in value_set:
                res.append(entity)
        return res
