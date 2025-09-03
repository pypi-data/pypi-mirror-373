import inspect
import ast

from typing import Callable
from .application_building_utils import IMPORTS, info
from .app_synchronizer import Synchronizer


class DataSet:

    def __init__(self, kawa, reporter, name: str, application, generator: Callable = None, datasource_id=None):
        self._k = kawa
        self._reporter = reporter
        self._name = name
        self._generator = generator
        self._datasource_id = datasource_id
        self._application = application
        self._sheet = None

    @property
    def name(self):
        return self._name

    @property
    def datasource_id(self):
        return self._datasource_id

    @property
    def sheet_id(self):
        return self._sheet['id'] if self._sheet else None

    @property
    def sheet(self):
        return self._sheet

    @property
    def tag(self):
        return f'{self._application.tag}|{self._name}'

    def sync(self):

        self._datasource_id = DataSet._DataSynchronizer(
            kawa=self._k,
            dataset=self,
        ).sync()

        self._sheet = DataSet._SheetSynchronizer(
            kawa=self._k,
            dataset=self,
        ).sync()

        self._reporter.report(
            object_type='DataSet',
            name=self._name,
        )

    def extract_script_source_code(self):
        return '{}\n\n{}'.format(
            '\n'.join(IMPORTS),
            inspect.getsource(self._generator)
        )

    def extract_indicator_types_from_script(self):
        source_code = self.extract_script_source_code()
        return self._extract_outputs(source_code)

    @staticmethod
    def _extract_outputs(source_code):
        tree = ast.parse(source_code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for deco in node.decorator_list:
                    if isinstance(deco, ast.Call) and getattr(deco.func, 'id', '') == 'kawa_tool':
                        for keyword in deco.keywords:
                            if keyword.arg == 'outputs':
                                outputs_node = keyword.value
                                outputs_src = ast.unparse(outputs_node)
                                safe_globals = {
                                    'str': 'text',
                                    'float': 'decimal',
                                    'date': 'date',
                                    'datetime': 'date_time',
                                    'bool': 'boolean',
                                }
                                return eval(outputs_src, safe_globals, {})

        return None

    class _DataSynchronizer(Synchronizer):

        def __init__(self, kawa, dataset):
            super().__init__(
                kawa=kawa,
                icon='💿',
                entity_description=f'Dataset "{dataset.name}"',
                entity_tag=dataset.tag
            )
            self._dataset = dataset
            self._new_datasource_id = None

        def _load_state(self):
            existing_datasource = self._k.entities.datasources().find_entity_by_tag(tag=self._tag)
            existing_script = self._k.entities.scripts().find_entity_by_tag(tag=self._tag)
            existing_etl_pipeline = self._k.entities.etl_pipelines().find_entity_by_tag(tag=self._tag)
            return {
                'datasource': existing_datasource,
                'script': existing_script,
                'etl': existing_etl_pipeline
            }

        def _raise_if_state_invalid(self):
            # The state is valid only if nothing is defined or if everything is defined
            num_defined = self._num_defined_entities()
            if num_defined != 0 and num_defined != len(self._state):
                raise Exception('The state for the DataSet is not consistent')

        def _should_create(self):
            return self._num_defined_entities() == 0

        def _create_new_entity(self):
            self._script_id = self._k.commands.run_command(
                command_name='createScript',
                command_parameters={
                    'name': self._dataset.name,
                    'tag': self._tag,
                    'content': self._dataset.extract_script_source_code()
                }
            )['id']

            indicator_types = self._dataset.extract_indicator_types_from_script()
            if not indicator_types:
                raise Exception('No indicators were found in the the underlying script')

            indicators = [self._build_indicator_from_id_and_type(indicator_id, indicator_type)
                          for indicator_id, indicator_type in indicator_types.items()]

            created_datasource_id = self._k.commands.run_command(
                command_name='createEtlAndDatasource',
                command_parameters=self._build_datasource_definition(indicators)
            )['dataSource']['id']

            self._new_datasource_id = created_datasource_id

        def _update_entity(self):
            self._update_script_if_necessary()
            self._update_datasource_if_necessary()

        def _build_new_state(self):
            datasource_state = self._state['datasource']
            return datasource_state['id'] if datasource_state else self._new_datasource_id

        def _update_script_if_necessary(self):
            existing_script = self._state['script']
            existing_etl_pipeline = self._state['etl']
            script_file_id = existing_script['sourceControlToolConfiguration']['toolName']
            existing_script_tmp_file = self._k.download_file_as_id(script_file_id)
            with open(existing_script_tmp_file, "r", encoding="utf-8") as file:
                existing_content = file.read()

            new_content = self._dataset.extract_script_source_code()

            if new_content != existing_content:
                self._k.commands.run_command('replaceScript', {
                    'content': new_content,
                    'name': existing_script['displayInformation']['displayName'],
                    'scriptId': str(existing_script['id'])
                })
                self._k.commands.run_command('runEtl', {
                    "etlPipelineId": str(existing_etl_pipeline['id']),
                    "fullRefresh": False,
                })

        def _update_datasource_if_necessary(self):
            existing_datasource = self._state['datasource']
            new_indicators = self._dataset.extract_indicator_types_from_script()
            existing_indicators = {
                i['displayInformation']['displayName']: i['type']
                for i in existing_datasource['indicators']
                if i['indicatorId'] != 'record_id'
            }

            # Indicators that are in the existing datasource but not in the new generator function
            # (Nothing to do, it just means that some indicators will no longer have a value)
            missing_indicator_names = []

            # Indicators that are in the new generator function but not in the existing data source
            # (We will need to add them)
            indicators_to_add = {}

            # Incompatible indicator: Indicators whose type changed
            # Records the name and the type that the indicator should have
            incompatible_indicators = {}

            # Looking at the new indicators, we are able to detect the ones that were not here initially
            # and the ones whose type has changed
            for new_indicator_name, new_indicator_type in new_indicators.items():
                if new_indicator_name not in existing_indicators:
                    indicators_to_add[new_indicator_name] = new_indicator_type
                else:
                    existing_indicator_type = existing_indicators[new_indicator_name]
                    if existing_indicator_type != new_indicator_type:
                        incompatible_indicators[new_indicator_name] = existing_indicator_type

            # Looking at the existing indicators, we are able to detect what is missing in the new generator function
            for existing_indicator_name in existing_indicators.keys():
                if existing_indicator_name not in new_indicators:
                    missing_indicator_names.append(existing_indicator_name)

            if incompatible_indicators:
                raise Exception(
                    'These indicators should have the following types, please check it: {}'
                    .format(incompatible_indicators))
            elif indicators_to_add:
                info('- Datasource: Adding {} indicators'.format(len(indicators_to_add)))
                self._k.commands.run_command(
                    command_name='addIndicatorsToDataSource',
                    command_parameters={
                        'dataSourceId': str(existing_datasource['id']),
                        'newIndicators': [
                            {
                                'displayInformation': {'displayName': name},
                                'includedInDefaultLayout': True,
                                'indicatorId': name,
                                'type': kawa_type,
                            }
                            for name, kawa_type in indicators_to_add.items()
                        ],
                    }
                )

        def _num_defined_entities(self):
            return len([val for val in self._state.values() if val])

        def _build_datasource_definition(self, indicators):
            return {
                "doNotCreateSheet": True,
                "isMapping": False,
                "displayInformation": {
                    "displayName": self._dataset.name,
                    "description": "",
                    "extraInformation": {
                        "immutableTag": self._tag
                    }
                },
                "loadingAdapterName": 'CLICKHOUSE',
                "loadingMode": "RESET_BEFORE_INSERT",
                "extractionAdapterName": "PYTHON_SCRIPT",
                "extractionAdapterConfiguration": {
                    "scriptId": str(self._script_id),
                    "scriptParametersValues": []
                },
                "indicators": indicators,
                "jobTrigger": {
                    "enabled": False,
                    "scheduleType": "INTERVAL",
                    "onlyOnBusinessDays": None,
                    "interval": 3,
                    "timeUnit": "HOURS",
                    "timeZone": None,
                    "initialDelay": 0
                },
                "rowMapperConfigList": [],
                "defaultGlobalPolicy": "ALLOW_ALL",
                "createAssociatedTimeSeriesDataSource": False,
                "needsQueryCostCheck": False
            }

        @staticmethod
        def _build_indicator_from_id_and_type(indicator_id, indicator_type):
            return {
                "elementDataModel": None,
                "displayInformation": {
                    "displayName": indicator_id,
                    "description": ""
                },
                "possibleValues": [],
                "indicatorId": indicator_id,
                "indicatorKind": "TABLE",
                "indicatorStatus": "ACTIVE",
                "includedInDefaultLayout": True,
                "type": indicator_type
            }

    class _SheetSynchronizer(Synchronizer):

        def __init__(self, kawa, dataset):
            super().__init__(
                kawa=kawa,
                icon='📙',
                entity_description=f'Sheet "{dataset.name}"',
                entity_tag=dataset.tag,
            )
            self._dataset = dataset
            self._new_sheet = None

        def _load_state(self):
            existing_datasource = self._k.entities.datasources().find_entity_by_tag(tag=self._tag)
            existing_sheet = self._k.entities.sheets().find_entity_by_tag(tag=self._tag)
            return {
                'datasource': existing_datasource,
                'sheet': existing_sheet,
            }

        def _raise_if_state_invalid(self):
            sheet_is_defined = bool(self._state['sheet'])
            data_is_defined = bool(self._state['datasource'])
            if sheet_is_defined and not data_is_defined:
                raise Exception('The Sheet is defined but not the datasource')

        def _should_create(self):
            return not self._state['sheet']

        def _create_new_entity(self):
            datasource_id = self._state['datasource']['id']
            self._new_sheet = self._k.commands.run_command(
                command_name='createSheet',
                command_parameters={
                    "createDefaultLayout": True,
                    "sheet": {
                        "displayInformation": {
                            "displayName": self._dataset.name,
                            "description": "",
                            "extraInformation": {
                                "immutableTag": self._tag
                            }
                        },
                        "dataSourceLinks": [{"targetDataSourceId": str(datasource_id)}],
                        "shared": False,
                        "generalAccess": "RESTRICTED"
                    }
                }
            )

        def _update_entity(self):
            self._new_sheet = self._k.commands.run_command(
                command_name='resetSheet',
                command_parameters={
                    "sheetId": str(self._state['sheet']['id'])
                }
            )

        def _build_new_state(self):
            return self._k.entities.sheets().find_entity_by_tag(tag=self._tag)
