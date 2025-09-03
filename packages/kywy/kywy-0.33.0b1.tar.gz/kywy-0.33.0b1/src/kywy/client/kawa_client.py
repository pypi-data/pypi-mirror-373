import base64
import json
import os
import tempfile
import shutil

from packaging.version import Version
import importlib.metadata

import pandas as pd
import requests
import urllib3
from dotenv import load_dotenv, find_dotenv
from tzlocal import get_localzone

from .chat import KawaChat
from .commands import KawaCommands
from .configuration import KawaConfiguration
from .data import KawaData
from .data_loader import KawaDataLoader
from .data_providers import KawaDataProviders
from .dsl import KawaLazyQuery, KawaColumn, KawaFilter
from .entities import KawaEntities
from .errors import ConflictError
from .reporting import KawaReporting
from .application.application_builder import ApplicationBuilder

from .. import __version__


class KawaClient:

    @staticmethod
    def load_client_from_environment():

        dotenv_file = find_dotenv(usecwd=True)
        load_dotenv(dotenv_file, override=True)
        key = os.getenv('KAWA_API_KEY')
        url = os.getenv('KAWA_API_URL')
        workspace_id = os.getenv('KAWA_WORKSPACE', '1')

        k = KawaClient(kawa_api_url=url)
        k.set_api_key(api_key=key)
        k.set_active_workspace_id(workspace_id)

        return k

    def __init__(self, kawa_api_url=None, verify_certificates=False, tmp_files_directory=None):

        self.kawa_api_url = kawa_api_url

        # APIs
        self.data: KawaData = KawaData(kawa_client=self)
        self.commands: KawaCommands = KawaCommands(kawa_client=self)
        self.entities: KawaEntities = KawaEntities(kawa_client=self)
        self.configuration: KawaConfiguration = KawaConfiguration(kawa_client=self)
        self.data_providers: KawaDataProviders = KawaDataProviders(kawa_client=self)

        # Authentication information
        self._authentication_mode = None
        self._access_token = None
        self._api_key = None
        self._service_principle = None
        self._verify_certificates = verify_certificates

        # Workspace
        self.active_workspace_id = None

        version = Version(__version__)

        # Misc
        self._major_version = version.major
        self._minor_version = version.minor

        self.tmp_files_directory = tmp_files_directory if tmp_files_directory else tempfile.gettempdir()
        urllib3.disable_warnings()

    def login_with_kerberos(self, service_principle, workspace_id=None):
        self._authentication_mode = 'KERBEROS'
        self._service_principle = service_principle
        self.set_active_workspace_id(workspace_id)
        self.get_server_version()

    def login_with_snowflake_jwt(self, jwt):
        self._authentication_mode = 'SNOWFLAKE'
        self._access_token = jwt

    def login_with_credential(self, login, password=None, password_file=None, workspace_id=None):
        pwd = None
        if password:
            pwd = password
        elif password_file:
            with open(password_file, 'r') as f:
                pwd = f.read().strip()

        response = requests.post(url='{}/authentication/login'.format(self.kawa_api_url),
                                 headers={
                                     'Content-Type': 'application/json'
                                 },
                                 verify=self._verify_certificates,
                                 data=json.dumps({
                                     "credentialType": "LOGIN_AND_PASSWORD",
                                     "credentials": {
                                         "email": login,
                                         "password": pwd
                                     }
                                 }))

        if response.status_code != 200:
            raise Exception('Error while logging in, please check your credentials and try again')

        error = response.json().get('error')
        if error:
            raise Exception('Error while logging in: {}'.format(error))

        self._access_token = response.cookies.get('accessToken')
        self._authentication_mode = 'JWT'
        self.set_active_workspace_id(workspace_id)

    def set_api_key(self, api_key=None, api_key_file=None):
        if api_key:
            self._api_key = api_key.strip()
        if api_key_file:
            with open(api_key_file, 'r') as f:
                self._api_key = f.read().strip()

    def open_profile(self, profile):
        with open(profile, 'r') as f:
            p = json.loads(f.read())
            self.kawa_api_url = p.get('url')
            self.set_api_key(api_key=p.get('apiKey'))

    def download_file(self, file_id):
        file_url = f'{self.kawa_api_url}/uploads/files/{file_id}'
        filename = self.get(f'{file_url}/metadata').get('fileName')
        return self.get_file(file_url, filename)

    def download_file_as_id(self, file_id):
        file_url = f'{self.kawa_api_url}/uploads/files/{file_id}'
        return self.get_file(file_url, file_id)

    def delete_file(self, file_id):
        file_url = f'{self.kawa_api_url}/uploads/files/{file_id}'
        return self.delete(file_url)

    def set_active_workspace_id(self, workspace_id):
        current_user = self.get(f'{self.kawa_api_url}/authentication/current-user')
        if workspace_id:
            self.active_workspace_id = workspace_id
        else:
            current_w_id = current_user.get('currentWorkspaceId')
            associated_w_id = current_user.get('currentWorkspaceId')
            self.active_workspace_id = current_w_id if current_w_id is not None else associated_w_id

        print(f'Authentication successful on {self.kawa_api_url}, in workspace {self.active_workspace_id}')

    def get_current_user(self):
        return self.get(
            url=f'{self.kawa_api_url}/authentication/current-user'
        )

    def get_file(self, url, filename):
        local_filename = self.tmp_files_directory + '/' + filename
        with requests.get(
                url=url,
                verify=self._verify_certificates,
                headers=self._request_headers(),
                cookies=self._request_cookies(),
                stream=True) as r:
            with open(local_filename, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

        return local_filename

    def get(self, url, params=None):
        response = requests.get(url=url,
                                verify=self._verify_certificates,
                                headers=self._request_headers(),
                                cookies=self._request_cookies(),
                                params=params)

        if response.status_code != 200:
            raise Exception(
                'Error while calling {}: {} - {}'.format(url, response.reason, str(response.content, 'utf-8')))

        return response.json()

    def delete(self, url, params=None):
        response = requests.delete(url=url,
                                   verify=self._verify_certificates,
                                   headers=self._request_headers(),
                                   cookies=self._request_cookies(),
                                   params=params)

        if response.status_code != 200:
            raise Exception(
                'Error while calling {}: {} - {}'.format(url, response.reason, str(response.content, 'utf-8')))

        return response.json()

    def get_text(self, url):
        response = requests.get(url=url,
                                verify=self._verify_certificates,
                                headers=self._request_headers(),
                                cookies=self._request_cookies())

        if response.status_code != 200:
            raise Exception(
                'Error while calling {}: {} - {}'.format(url, response.reason, str(response.content, 'utf-8')))

        return response.text

    def post(self, url, data, stream=False, as_user=None):
        headers = self._request_headers()
        if as_user:
            headers['x-kawa-impersonate-user-unique-id'] = as_user

        response = requests.post(url=url,
                                 verify=self._verify_certificates,
                                 headers=headers,
                                 cookies={'accessToken': self._access_token},
                                 stream=stream,
                                 data=json.dumps(data))

        if response.status_code == 409:
            raise ConflictError('Conflict while creating an entity: it already exists')
        if response.status_code != 200 and response.status_code != 202:
            raise Exception(
                'Error while calling {}: {} - {}'.format(url, response.reason, str(response.content, 'utf-8')))

        return response if stream else response.json()

    def health(self):
        return self.get(self.kawa_api_url + '/health')

    def runner_health(self):
        return self.get(self.kawa_api_url + '/health/runner')

    def post_binary_file(self, filename, url):
        print('> Streaming file {} to KAWA'.format(filename))
        urllib3.disable_warnings()
        with open(filename, 'rb') as f:
            response = requests.post(url=url,
                                     verify=self._verify_certificates,
                                     headers=self._request_headers(),
                                     cookies={'accessToken': self._access_token},
                                     data=f)
        if response.status_code != 200:
            raise Exception(
                'Error while calling {}: {} - {}'.format(url, response.reason, str(response.content, 'utf-8')))

    def post_stream(self, stream, url):
        print('> Streaming to KAWA')
        urllib3.disable_warnings()
        headers = self._request_headers()
        headers['Content-Type'] = 'application/octet-stream'
        response = requests.post(url=url,
                                 verify=self._verify_certificates,
                                 stream=True,
                                 headers=self._request_headers(),
                                 cookies={'accessToken': self._access_token},
                                 data=stream)
        if response.status_code != 200:
            raise Exception(
                'Error while calling {}: {} - {}'.format(url, response.reason, str(response.content, 'utf-8')))

    def app(self,
            application_name,
            sidebar_color=None,
            palette=None,
            theme=None,
            create_default_components=True,
            unique_tag=None,
            ):
        return ApplicationBuilder(
            kawa_client=self,
            name=application_name,
            palette=palette,
            palette_name=theme,
            sidebar_color=sidebar_color,
            create_default_components=create_default_components,
            unique_tag=unique_tag,
        )

    def new_data_loader(self,
                        df,
                        datasource_name: str,
                        shared: bool = False,
                        copy_df: bool = True,
                        ):
        """
        Creates a new data loader object that can be used to create, update and feed a kawa datasource.

        :param: df:
        The dataframe to send. Most of the value types are supported and will be translated to kawa
        types automatically.

        :param: datasource_name:
        The datasource to create, update and to inject data in will be identified by this name
        in the current workspace.

        :param: shared:
        If True, when a datasource is created through this loader, it will be shared to all users of the
        workspace.

        :param: copy_df:
        If set to True (default value), the loader will start by creating a copy of the dataframe (df argument).
        If set to False, possible modifications in the df will happen in place - this increases performances.

        :return:
        A data loader object.
        Call the load_data method to perform the load.
        """
        return KawaDataLoader(
            kawa_client=self,
            df=df,
            datasource_name=datasource_name,
            datasource_is_shared=shared,
            copy_df=copy_df,
        )

    def new_arrow_data_loader(self,
                              arrow_table=None,
                              datasource_name: str = None,
                              shared: bool = False,
                              arrow_schema=None,
                              strict_mode=False,
                              copy_df=False,  # Kept for backward compatibility
                              ):
        return KawaDataLoader(
            kawa_client=self,
            df=None,
            arrow_table=arrow_table,
            arrow_schema=arrow_schema,
            datasource_name=datasource_name,
            datasource_is_shared=shared,
            strict_mode=strict_mode,
            copy_df=copy_df
        )

    def reporting(self) -> KawaReporting:
        return KawaReporting(self)

    def chat(self, copilot_type: str, conversation_id: str) -> KawaChat:
        return KawaChat(self, copilot_type=copilot_type, conversation_id=conversation_id)

    def sheet(self, sheet_name=None, sheet_id=None, force_tz=None, no_output=False):
        return KawaLazyQuery(
            kawa_client=self,
            sheet_name=sheet_name,
            sheet_id=sheet_id,
            force_tz=force_tz,
            no_output=no_output
        )

    def datasource(self, datasource_id=None, force_tz=None, no_output=False):
        return KawaLazyQuery(
            kawa_client=self,
            datasource_id=datasource_id,
            force_tz=force_tz,
            no_output=no_output
        )

    def widget(self, dashboard_name, widget_name, force_tz=None, ):
        return KawaLazyQuery(kawa_client=self, sheet_name=None, force_tz=force_tz).widget(dashboard_name, widget_name)

    def lazy_frame(self, sheet_name, force_tz=None):
        return KawaLazyQuery(kawa_client=self, sheet_name=sheet_name, force_tz=force_tz)

    def get_server_version(self):
        env = self.get(self.kawa_api_url + '/backoffice/application-environment')
        version = env.get('version', {}).get('version')

        if not version:
            return {
                'major': 0,
                'minor': 0,
                'patch': 0
            }

        s = version.split('.')
        major = int(s[0][1:])
        minor = int(s[1])
        patch = int(s[2].split('-')[0])
        return {
            'major': major,
            'minor': minor,
            'patch': patch
        }

    def get_usage_stats(self, from_date=None, to_date=None, tz=None):
        """
        Loads usage stats for all users in KAWA
        :param from_date: Loads actions from that date (default=far in the past)
        :param to_date: to that date (default=far in the future)
        :param tz: In this timezone (default=the local timezone of the python runtime)
        :return:
        """

        if not tz:
            tz = get_localzone()

        if not from_date:
            from_date = '1980-01-01'

        if not to_date:
            to_date = '2100-01-01'

        url = self.kawa_api_url + '/backoffice/usage?from={}&to={}&zoneId={}'.format(from_date, to_date, tz)
        json_data = self.get(url)

        if not json_data:
            return pd.DataFrame([])

        report = json_data.get('userUsageReports')

        return pd.DataFrame.from_records(report, index='userId')

    def run_tool(self, tool, datasource_id=None, sheet_id=None, df=None, mapping=None, **kwargs):

        if int(df is not None) + int(datasource_id is not None) + int(sheet_id is not None) != 1:
            raise Exception('Please define one and exactly one: datasource_id, sheet_id or df')

        if df is None:
            # Here, we will load data directly from KAWA
            if mapping is None:
                raise Exception('Please define a mapping to match the tool input')

            if sheet_id:
                query = self.sheet(sheet_id=sheet_id)
            else:
                # In this branch, datasource_id must be defined
                query = self.datasource(datasource_id=datasource_id)

            df = query.select(*mapping.keys()).collect()

        if mapping:
            df.rename(columns=mapping, inplace=True)

        return tool(df, **kwargs)

    def _request_cookies(self):
        if self._authentication_mode == 'JWT':
            return {'accessToken': self._access_token}
        if self._authentication_mode == 'KERBEROS':
            return {}

    def _request_headers(self):

        headers = {
            'Content-Type': 'application/json',
            'x-kawa-kywy-version': '{}.{}'.format(self._major_version, self._minor_version)
        }

        if self.active_workspace_id:
            headers['x-kawa-workspace-id'] = str(self.active_workspace_id)

        if self._api_key:
            headers['x-kawa-api-key'] = str(self._api_key)

        if self._authentication_mode == 'KERBEROS':
            import gssapi
            # Use GSS API to get the Service Token
            service_name = gssapi.Name(self._service_principle)
            client_ctx = gssapi.SecurityContext(name=service_name, usage='initiate')
            initial_client_token = client_ctx.step()
            b64_encoded = base64.b64encode(initial_client_token).decode('utf-8')
            headers['Authorization'] = 'Negotiate {}'.format(b64_encoded)

        if self._authentication_mode == "SNOWFLAKE":
            headers['Authorization'] = f'Snowflake Token={self._access_token}'

        return headers

    @staticmethod
    def col(column_name: str):
        return KawaColumn(column_name)

    @staticmethod
    def cols(regexp='.*'):
        return KawaColumn(column_name='',
                          column_regexp=regexp,
                          indicator_columns_only=False,
                          default_sheet_columns_only=False)

    @staticmethod
    def indicator_cols():
        return KawaColumn(column_name='',
                          column_regexp=None,
                          indicator_columns_only=True,
                          default_sheet_columns_only=False)

    @staticmethod
    def sheet_cols():
        return KawaColumn(column_name='',
                          column_regexp=None,
                          indicator_columns_only=False,
                          default_sheet_columns_only=True)

    @staticmethod
    def where(indicator_id):
        return KawaFilter(indicator_id=indicator_id)
