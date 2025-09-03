import time
import traceback

from typing import Callable

from .app_reporter import Reporter
from .app_agent import Agent
from .app_dataset import DataSet
from .app_filter import TextFilter
from .app_model import DataModel
from .app_page import ApplicationPage
from .application_building_utils import info, start_sync, \
    error, feedback, PALETTES, init_logs


class ApplicationBuilder:

    def __init__(self,
                 kawa_client,
                 name,
                 sidebar_color=None,
                 palette=None,
                 palette_name=None,
                 create_default_components=True,
                 unique_tag=None):
        self._k = kawa_client
        self._reporter = Reporter(name=name)
        self._name = name
        self._datasets = []
        self._pages = []
        self._text_filters = {}
        self._model = None
        self._application_id = None
        self._application_url = None
        self._agent = None
        self._unique_tag = unique_tag or f'#{name}'
        self._sidebar_color = sidebar_color
        self._create_default_components = create_default_components

        init_logs()

        if palette_name:
            self._palette = PALETTES.get(palette_name)
        else:
            self._palette = palette

    @property
    def application_id(self):
        return self._application_id

    @property
    def tag(self):
        return self._unique_tag

    @property
    def agent_id(self):
        if self._agent:
            return self._agent.agent_id

    @property
    def data_is_configured(self):
        return bool(self._model)

    @property
    def url(self):
        return self._application_url

    def create_model(self, dataset):
        self._model = DataModel(
            kawa=self._k,
            reporter=self._reporter,
            name=self._name,
            dataset=dataset,
            application=self,
        )
        return self._model

    def create_dataset(self, name: str, generator: Callable = None, datasource_id=None):
        existing_names = [d.name for d in self._datasets]
        if name in existing_names:
            raise Exception(f'A dataset with the name {name} already exists. Please pick a different one')

        dataset = DataSet(
            kawa=self._k,
            reporter=self._reporter,
            application=self,
            name=name,
            generator=generator,
        )
        self._datasets.append(dataset)
        return dataset

    def create_page(self, name: str):
        existing_names = [d.name for d in self._pages]
        if name in existing_names:
            raise Exception(f'A page with the name {name} already exists. Please pick a different one')

        page = ApplicationPage(
            kawa=self._k,
            reporter=self._reporter,
            data_model=self._model,
            application=self,
            name=name,
        )
        self._pages.append(page)
        return page

    def create_text_filter(self, name, filtered_column=None, source=None):
        # Merges filters with the same name
        if name not in self._text_filters:
            self._text_filters[name] = TextFilter(
                kawa=self._k,
                reporter=self._reporter,
                name=name,
            )

        self._text_filters[name].append_column(
            sheet_id_supplier=lambda: source.sheet_id if source else self._model.sheet_id,
            # If filtered column is not specified, rever to name
            column_name=filtered_column or name,
        )

    def create_ai_agent(self, name, instructions, color=None):
        self._agent = Agent(
            kawa=self._k,
            reporter=self._reporter,
            name=name,
            instructions=instructions,
            application=self,
            color=color,
        )

    def publish(self):

        info('---' * 30)
        info(f'🚀 Publishing app "{self._name}" to {self._k.kawa_api_url}')
        info('---' * 30)
        try:
            self.sync()
            self._health_check()
            export_file = self._reporter.export()
        except Exception as e:
            error_message = str(e)
            trace = traceback.format_exc()
            error(f'{error_message} - {trace}')
        finally:
            if self.data_is_configured:
                feedback(self.url, report_file=export_file)

    def sync(self):
        start_sync(f'Application {self._name}')

        existing_application = self._load_state()
        if existing_application:
            self._cleanup_existing_application(existing_application)

        if self._agent:
            self._agent.sync()

        if not self._model and not self._datasets:
            info('👻 No data configured')
            return

        for dataset in self._datasets:
            dataset.sync()

        if not self._model:
            # By default, init the model on the first dataset
            self.create_model(self._datasets[0])

        self._model.sync()

        if not self._model.sheet_id:
            raise Exception('The underlying model has not been synced')

        if existing_application:
            self._update_application_if_necessary(existing_application)
        else:
            self._create_new_application()

        extended_application = self._k.entities.extended_applications().get_entity_by_id(self._application_id)
        for text_filter in self._text_filters.values():
            text_filter.sync(
                extended_application=extended_application,
            )

        for page in self._pages:
            page.sync(application_id=self._application_id)

    def _load_state(self):
        return self._k.entities.applications().find_entity_by_tag(tag=self.tag)

    def _health_check(self, iteration=1):

        if not self.data_is_configured:
            return

        max_iter = 10
        if iteration > max_iter:
            error(f'🚨 Application is not healthy after allocated wait time')

        num_datasets = len(self._datasets)
        failures = []

        if iteration == 1:
            ds = 'datasets' if num_datasets > 1 else 'dataset'
            info(f'🚑 Running healthcheck on {num_datasets} {ds}')
            for dataset in self._datasets:
                info(f'--> {dataset.name}')

            time.sleep(1)
        else:
            info(f'🚑 Retry {iteration - 1}/{max_iter}')
            time.sleep(iteration)

        for dataset in self._datasets:
            ds_id = str(dataset.datasource_id)
            url = f'{self._k.kawa_api_url}/backoffice/datasources/health-report/v2/{ds_id}'
            health_reports = self._k.get(url)
            chronological = sorted(health_reports, key=lambda x: x['synchronizationState']['startTime'])
            last_report = chronological[-1]
            status = last_report['synchronizationState']['status']

            if status == 'SUCCESS':
                info(f'💚 Dataset {dataset.name} is healthy')
            elif status == 'RUNNING':
                info(f'🕣 Dataset {dataset.name} is still running - let\'s wait a bit and check again.')
                self._health_check(iteration + 1)
            elif status == 'FAILURE':
                error(f'🚨 Dataset {dataset.name} is NOT healthy')
                error(last_report['synchronizationState']['logAnswer']['log'])
                failures.append(dataset.name)

        if failures:
            error(f'🚨 Application is not healthy')

    def _update_application_if_necessary(self, existing_application):
        workspace_id = existing_application['workspaceId']
        base_url = self._k.kawa_api_url
        self._application_id = existing_application['id']
        self._application_url = f'{base_url}/workspaces/{workspace_id}/applications/{self._application_id}'

        required_sheet_ids = [d.sheet_id for d in self._datasets]
        self._k.commands.run_command('replaceApplicationSheetIds', {
            "applicationId": str(self._application_id),
            "sheetIds": list(required_sheet_ids),
            "createDefaultComponents": True,
            "forceCreateAllDefaultComponents": True,
        })

    def _create_new_application(self):
        if self._palette and len(self._palette) > 7:
            self._k.commands.run_command('replaceWorkspacePalette', {
                "workspaceId": self._k.active_workspace_id,
                "palette": {
                    "colors": self._palette,
                    "enabled": True
                }
            })

        created_app = self._k.commands.run_command('createApplication', {
            "displayInformation": {
                "displayName": self._name,
                "description": "",
                "extraInformation": {
                    "immutableTag": f'{self.tag}'
                }
            },
            "sheetIds": [d.sheet_id for d in self._datasets],
            "agentIds": [self.agent_id] if self.agent_id else [],
            "createDefaultComponents": self._create_default_components,
        })['application']

        workspace_id = created_app['workspaceId']
        base_url = self._k.kawa_api_url
        self._application_id = created_app['id']
        self._application_url = f'{base_url}/workspaces/{workspace_id}/applications/{self._application_id}'
        info(f'⚙️ Application {self._name} was created (id={self._application_id})')
        info(f'🏷️ New tag for application: {self._unique_tag}')

        if self._sidebar_color:
            self._k.commands.run_command('replaceApplicationDisplayParameters', {
                "applicationId": str(self._application_id),
                "displayParameters": {
                    "color": self._sidebar_color,
                }
            })

        return self._application_id

    def _cleanup_existing_application(self, existing_application):
        view_component_list = [
            str(c['componentId'])
            for c in existing_application.get('components', [])
            if c['componentType'] == 'VIEW'
        ]
        for component_id in view_component_list:
            print('Removing component')
            self._k.commands.run_command('removeComponentFromApplication', {
                "applicationId": str(existing_application['id']),
                "componentId": component_id,
            })
