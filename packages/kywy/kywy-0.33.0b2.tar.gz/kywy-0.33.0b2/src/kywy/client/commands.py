import datetime
from enum import Enum
from typing import Optional, List

import tzlocal

from .errors import ConflictError
import json
from datetime import date


class SourceControlType(Enum):
    GIT_LAB = 'GIT_LAB'
    GIT_HUB = 'GIT_HUB'
    KAWA_FILE_STORE = 'KAWA_FILE_STORE'


class KawaCommands:

    def __init__(self, kawa_client):
        self._k = kawa_client
        self._secured_commands_url_fragment = '/commands/secured/run'

    def _run_command(self, command_name, command_parameters, as_user=None):
        url = '{}/{}'.format(self._k.kawa_api_url, self._secured_commands_url_fragment)
        r = self._k.post(url, {
            'command': command_name,
            'parameters': command_parameters
        }, as_user=as_user)
        return r

    def _run_idempotent_command(self, command_name, command_parameters, idempotency_key, entity_kind):
        try:
            return self._run_command(command_name, command_parameters)
        except ConflictError:
            # Idempotency: in case of conflict, fetch the entity
            return self._k.entities \
                .entities_of_kind(entity_kind) \
                .get_entity(idempotency_key)

    @staticmethod
    def _entity_id(entity_or_entity_id):
        return entity_or_entity_id if isinstance(entity_or_entity_id, str) else entity_or_entity_id.get('id')

    def run_command(self,
                    command_name: str,
                    command_parameters,
                    as_user=None
                    ):
        return self._run_command(command_name, command_parameters, as_user)

    """ Misc commands """

    def replace_communication_provider_type(self, configuration_provider_type='LOG'):
        """
        :param configuration_provider_type: accepted values are:
            LOG: No message is sent, just printed out in the server logs (default)
            SMTP: Send emails via SMTP
            MAILGUN: Send email vio the Mailgun REST API
        :return:
        """
        return self._run_command(command_name='ReplaceCommunicationProviderType',
                                 command_parameters={
                                     'communicationProviderType': configuration_provider_type,
                                 })

    def replace_configuration(self, configuration_type, payload):
        return self._run_command(command_name='ReplaceConfiguration',
                                 command_parameters={
                                     'configurationClassSimpleName': configuration_type,
                                     'configurationContent': payload
                                 })

    def toggle_feature(self, feature_name, is_enabled=True):
        return self._run_command(command_name='ToggleFeature',
                                 command_parameters={
                                     'featureName': feature_name,
                                     'enabled': is_enabled
                                 })

    def add_script_runner(self, name, host, port, private_key=None, tls=False):
        return self._run_idempotent_command(command_name='CreateScriptRunner',
                                            idempotency_key=name,
                                            entity_kind='script-runners',
                                            command_parameters={
                                                'name': name,
                                                'host': host,
                                                'port': port,
                                                'tls': tls,
                                                'clearTextPrivateKey': private_key
                                            })

    def toggle_script_runner(self, enabled=True):
        runners = self._k.entities.script_runners().list_entities()
        if not runners:
            raise Exception('No runner found in the workspace')
        return self._run_command(command_name='ToggleScriptRunner',
                                 command_parameters={
                                     'scriptRunnerEntityId': runners[0].get('id'),
                                     'enabled': enabled
                                 })

    def replace_script_runner_location(self, host='localhost', port=8815, tls=True):
        runners = self._k.entities.script_runners().list_entities()
        if not runners:
            raise Exception('No runner found in the workspace')
        return self._run_command(command_name='ReplaceScriptRunnerLocation',
                                 command_parameters={
                                     'scriptRunnerEntityId': runners[0].get('id'),
                                     'host': host,
                                     'port': port,
                                     'tls': tls,
                                 })

    def replace_script_runner_private_key(self, private_key):
        runners = self._k.entities.script_runners().list_entities()
        if not runners:
            raise Exception('No runner found in the workspace')
        return self._run_command(command_name='ReplaceScriptRunnerPrivateKey',
                                 command_parameters={
                                     'scriptRunnerEntityId': runners[0].get('id'),
                                     'clearTextPrivateKey': private_key,
                                 })

    """User and permission management"""

    def get_principal(self, email_or_unique_id: str):
        principal = self._k.entities.principals().find_first_entity_by_attribute('uniqueId', email_or_unique_id)
        if not principal:
            principal = self._k.entities.principals().find_first_entity_by_attribute('email', email_or_unique_id)
        if not principal:
            raise ValueError(f'Principal with email or unique ID {email_or_unique_id} was not found')

        return principal

    def get_principal_entity_id(self, email_or_unique_id: str) -> str:
        principal = self.get_principal(email_or_unique_id)
        return self._entity_id(principal)

    def replace_user_role(self, email_or_unique_id: str, new_role: str):
        return self._run_command(command_name='ReplaceUserRole',
                                 command_parameters={
                                     'principalId': self.get_principal_entity_id(email_or_unique_id),
                                     'role': new_role
                                 })

    def change_user_status(self, email_or_unique_id: str, active: bool = True):
        return self._run_command(command_name='ReplaceUserStatus',
                                 command_parameters={
                                     'principalId': self.get_principal_entity_id(email_or_unique_id),
                                     'active': active
                                 })

    def toggle_users_status(self, user_email_or_id_list: list[str], active: bool = False):
        for email_or_unique_id in user_email_or_id_list:
            self._run_command(command_name='ReplaceUserStatus',
                              command_parameters={
                                  'principalId': self.get_principal_entity_id(email_or_unique_id),
                                  'active': active
                              })

    def replace_access_policy_for_datasource(self, datasource, email_or_unique_id: str, access_policy):
        return self._run_command(command_name='ReplaceAccessPolicyForDataSource',
                                 command_parameters={
                                     "principalId": self.get_principal_entity_id(email_or_unique_id),
                                     "dataSourceId": self._entity_id(datasource),
                                     "accessPolicy": access_policy
                                 })

    def assign_user_to_perimeters(self, email_or_unique_id: str, perimeter_names):
        return self._run_command(command_name='AssignPrincipalToPerimeters',
                                 command_parameters={
                                     'principalEntityId': self.get_principal_entity_id(email_or_unique_id),
                                     'memberOfPerimeterNames': perimeter_names or []
                                 })

    def create_users(self, user_id_list: list[str]):
        return self._run_command(command_name='CreateActivePrincipals',
                                 command_parameters={
                                     'principalIds': user_id_list
                                 })

    def change_user_password(self, email_or_unique_id: str, new_password: str):
        return self._run_command(command_name='AdminChangeUserPassword',
                                 command_parameters={
                                     'principalId': self.get_principal_entity_id(email_or_unique_id),
                                     'newPassword': new_password,
                                 })

    def create_user_with_email_and_password(self, email, password, first_name=None, last_name=None):
        user_tech_id = self._k.entities.principals().find_entities_by_attribute('uniqueId', [email])
        if user_tech_id:
            return
        return self._run_command(command_name='CreateActivePrincipalWithPassword',
                                 command_parameters={
                                     'email': email.lower(),
                                     'password': password,
                                     'firstName': first_name or email,
                                     'lastName': last_name or email
                                 })

    def replace_forbidden_data_types(self, user_email_or_id_list: list[str], forbidden_types):
        for email_or_unique_id in user_email_or_id_list:
            self._run_command(command_name='ReplaceForbiddenDataTypes',
                              command_parameters={
                                  'principalId': self.get_principal_entity_id(email_or_unique_id),
                                  'forbiddenTypes': forbidden_types
                              })

    def replace_permissions(self, user_email_or_id_list: list[str], permissions):
        for email_or_unique_id in user_email_or_id_list:
            self._run_command(command_name='ReplaceApplicationWidePermissions',
                              command_parameters={
                                  'principalId': self.get_principal_entity_id(email_or_unique_id),
                                  'permissions': permissions
                              })

    def toggle_workspace_visibility(self, workspace_id, public=False):
        return self._run_command(command_name='ToggleWorkspaceVisibility',
                                 command_parameters={
                                     'workspaceId': workspace_id,
                                     'isPublic': public
                                 })

    def add_user_to_white_list(self, user_id):
        return self._run_command(command_name='AddUserToWhiteList',
                                 command_parameters={
                                     'userId': user_id.lower(),
                                 })

    def remove_user_from_white_list(self, user_id):
        return self._run_command(command_name='RemoveUserFromWhiteList',
                                 command_parameters={
                                     'userId': user_id.lower(),
                                 })

    def create_users_in_workspace(self,
                                  workspace_name,
                                  user_list,
                                  add_users_to_whitelist=False):
        """
        Create users, create the workspace if it does not exist and put the users in it.
        :param workspace_name: Workspace name to create/load
        :param add_users_to_whitelist: If set to True, will proceed to update the whitelist
        :param user_list: a list of users:
        [{
          'email': 'lucius.fox@wayne-enterprises.com',
          'password': 'LuciusF0x123',
          'first_name': 'Lucius',
          'last_name': 'Fox',
        }]
        """
        workspace = self.create_workspace(workspace_name)
        for user in user_list:
            self.create_user_with_email_and_password(
                email=user['email'],
                password=user['password'],
                first_name=user['first_name'],
                last_name=user['last_name'],
            )
            if add_users_to_whitelist:
                self.add_user_to_white_list(user['email'])

        self.add_users_to_workspace([user['email'].lower() for user in user_list], workspace['id'], True)

    def create_workspace(self, workspace_name):
        existing_entity = self._k.entities.workspaces().get_entity(workspace_name)

        if existing_entity:
            return existing_entity

        return self._run_command(command_name='CreateWorkspace',
                                 command_parameters={
                                     'displayInformation': {
                                         'displayName': workspace_name,
                                         'description': ''
                                     },
                                 })

    def add_users_to_workspace(self, user_id_list, workspace_id, permissions=None, set_as_current_workspace=True):
        principals = self._k.entities.principals().find_entities_by_attribute('uniqueId', user_id_list)
        principal_entity_ids = [self._entity_id(principal) for principal in principals]
        members = [{'principalId': principal_entity_id, 'permissions': permissions or []} for principal_entity_id in
                   principal_entity_ids]

        self._run_command(command_name='AddMembersToWorkspace',
                          command_parameters={
                              'workspaceId': self._entity_id(workspace_id),
                              'members': members
                          })

        if set_as_current_workspace:
            self._run_command(command_name='SetCurrentWorkspaceForPrincipals',
                              command_parameters={
                                  'workspaceId': self._entity_id(workspace_id),
                                  'principalIds': principal_entity_ids
                              })

    def remove_users_from_workspace(self, user_id_list, workspace_id):
        user_tech_id = self._k.entities.principals().find_entities_by_attribute('uniqueId', user_id_list)
        self._run_command(command_name='RemoveWorkspaceMembers',
                          command_parameters={
                              'workspaceId': str(workspace_id),
                              'principalIds': [self._entity_id(user) for user in user_tech_id]
                          })

    """DataSources"""

    def delete_datasource(self, datasource):
        self._run_command(command_name='ArchiveDataSourceAndDeleteAssociatedData',
                          command_parameters={'dataSourceId': self._entity_id(datasource)})

    def create_datasource(self, datasource):
        return self._run_idempotent_command(command_name='CreatePythonDataSource',
                                            idempotency_key=datasource['displayInformation']['displayName'],
                                            entity_kind='datasources',
                                            command_parameters={'dataSource': datasource})

    def create_private_join_datasource(self, datasource):
        return self._run_idempotent_command(command_name='CreatePythonPrivateJoinDataSource',
                                            idempotency_key=datasource['displayInformation']['displayName'],
                                            # TODO THIERRY ########## python-columns: wrong?
                                            entity_kind='datasources',
                                            command_parameters={'dataSource': datasource})

    def add_indicators_to_datasource(self, datasource, new_indicators):
        return self._run_command(command_name='AddIndicatorsToDataSource',
                                 command_parameters={
                                     'dataSourceId': self._entity_id(datasource),
                                     'newIndicators': new_indicators
                                 })

    def share_datasource(self, datasource,
                         teams_ids: Optional[List[str]] = None,
                         team_ids_with_write_permission: Optional[List[str]] = None,
                         general_access: Optional[str] = None):
        if not isinstance(teams_ids, list):
            teams_ids = []
        if not isinstance(team_ids_with_write_permission, list):
            team_ids_with_write_permission = []
        if not general_access:
            if not teams_ids and not team_ids_with_write_permission:
                general_access = 'READ'
            else:
                general_access = 'RESTRICTED'

        return self._run_command(command_name='UpdateDataSourceShareStatus',
                                 command_parameters={
                                     'dataSourceId': self._entity_id(datasource),
                                     'shared': True,
                                     'advancedSharingConfiguration':
                                         {'sharedTeamIds': teams_ids,
                                          'teamIdsWithWritePermission': team_ids_with_write_permission,
                                          'generalAccess': general_access
                                          }
                                 })

    def drop_date_partition(self, datasource, date_partition: date):
        return self._run_command(command_name='DropDatePartition',
                                 command_parameters={
                                     'dataSourceId': self._entity_id(datasource),
                                     'datePartition': (date_partition - date(1970, 1, 1)).days
                                 })

    def replace_datasource_primary_keys(self, datasource, new_primary_keys, partition_key=None, partition_sampler=None):
        pk = [{'indicatorId': indicator_id} for indicator_id in new_primary_keys]
        datasource_id = self._entity_id(datasource)
        datasource = self._k.entities.datasources().get_entity(datasource_id)
        warehouse_storage_config = datasource.get('storageConfiguration', {}).get('warehouseStorageConfiguration')

        if warehouse_storage_config:
            current_keys = warehouse_storage_config.get('sortingKeys', [])
            current_partition_key = warehouse_storage_config.get('partitionIndicator')
            current_sampler = warehouse_storage_config.get('partitionSampler', {}).get('dateSamplerType')

            if (current_keys == new_primary_keys
                    and partition_key == current_partition_key
                    and current_sampler == partition_sampler):
                # Idempotency: Configuration did not change
                return datasource

        return self._run_command(command_name='ReplaceDataSourcePrimaryKeys',
                                 command_parameters={
                                     'dataSourceId': self._entity_id(datasource),
                                     'newPrimaryKeys': pk,
                                     'partitionIndicator': partition_key,
                                     'partitionSampler': partition_sampler
                                 })

    def delete_data(self, datasource, delete_where):
        filters = [where.to_dict() for where in delete_where]
        return self._run_command(command_name='DeleteData',
                                 command_parameters={
                                     'dataSourceId': self._entity_id(datasource),
                                     'deleteDataFilters': filters
                                 })

    def force_entries_deduplication(self, datasource):
        return self._run_command(command_name='ForceEntriesDeduplication',
                                 command_parameters={
                                     'dataSourceId': self._entity_id(datasource)
                                 })

    def force_entries_deduplication_on_partition(self, datasource, partition_id):
        return self._run_command(command_name='ForceEntriesDeduplication',
                                 command_parameters={
                                     'dataSourceId': self._entity_id(datasource),
                                     'partitionId': partition_id
                                 })

    """Data providers"""

    def replace_data_provider_connection_security_parameters(self, data_provider, ssl, kerberos):
        return self._run_command(command_name='ReplaceDataProviderConnectionSecurityParameters',
                                 command_parameters={
                                     'dataProviderId': self._entity_id(data_provider),
                                     'connectionSecurityParameters': {
                                         'useSsl': ssl,
                                         'useKerberos': kerberos
                                     }
                                 })

    def replace_data_provider_connection_parameters(self, data_provider, connection_parameters):
        return self._run_command(command_name='ReplaceDataProviderConnectionParameters',
                                 command_parameters={
                                     'dataProviderId': self._entity_id(data_provider),
                                     'connectionParameters': connection_parameters
                                 })

    def archive_data_provider(self, data_provider):
        return self._run_command(command_name='DeleteDataProvider',
                                 command_parameters={
                                     'dataProviderId': self._entity_id(data_provider)
                                 })

    def create_data_provider(self,
                             provider_name,
                             connection_parameters,
                             provider_type='JDBC',
                             restricted=False,
                             ssl=False,
                             kerberos=False):
        return self._run_idempotent_command(command_name='CreateDataProvider',
                                            idempotency_key=provider_name,
                                            entity_kind='data-providers',
                                            command_parameters={
                                                'displayInformation': {
                                                    'displayName': provider_name,
                                                    'description': ''
                                                },
                                                'connectionSecurityParameters': {
                                                    'useSsl': ssl,
                                                    'useKerberos': kerberos
                                                },
                                                'restricted': restricted,
                                                'dataProviderType': provider_type,
                                                'connectionParameters': connection_parameters
                                            })

    def create_or_update_data_provider(self,
                                       provider_name,
                                       connection_parameters,
                                       provider_type='JDBC',
                                       check_health=True,
                                       restricted=False,
                                       ssl=False,
                                       kerberos=False):

        provider = self.create_data_provider(provider_name, connection_parameters, provider_type, restricted, ssl,
                                             kerberos)

        self.replace_data_provider_connection_security_parameters(provider, ssl, kerberos)
        self.replace_data_provider_connection_parameters(provider, connection_parameters)

        if check_health:
            print('Testing connection...')
            health = self._k.data_providers.check_provider_health(provider)
            print(health)

    """Data and Connections"""

    def load_data(self, datasource_id, rows, is_incremental, auto_increment_offset=0, loading_session_id=None):
        return self._run_command(command_name='LoadExternalData',
                                 command_parameters={
                                     'loadingMode': 'INCREMENTAL' if is_incremental else 'RESET_BEFORE_INSERT',
                                     'loadingAdapterName': 'CLICKHOUSE',
                                     'rows': rows,
                                     'loadingSessionId': loading_session_id,
                                     'autoIncrementOffset': auto_increment_offset,
                                     'dataSourceId': self._entity_id(datasource_id)
                                 })

    def set_health_check_result(self, datasource_id, is_healthy: bool, message: Optional[str]):
        return self._run_command(command_name='ReplaceDatasourceHealthCheckResult',
                                 command_parameters={
                                     'dataSourceId': self._entity_id(datasource_id),
                                     'healthCheckResult': {
                                         'checkTime': int(
                                             datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000),
                                         'checkPassed': is_healthy,
                                         'message': message
                                     }
                                 })

    """Layouts, Sheets and Attributes"""

    def create_attribute(self, attribute_name):
        return self._run_idempotent_command(command_name='CreateAttribute',
                                            idempotency_key=attribute_name,
                                            entity_kind='attributes',
                                            command_parameters={
                                                'attribute': {
                                                    'displayInformation': {
                                                        'displayName': attribute_name
                                                    }
                                                }
                                            })

    def delete_sheet(self, sheet):
        self._run_command(command_name='DeleteSheet',
                          command_parameters={
                              'sheetId': self._entity_id(sheet),
                          })

    def create_sheet(self, sheet_name, datasource):
        created_sheet = self._run_command(command_name='CreateSimpleSheet',
                                          command_parameters={
                                              'shared': False,
                                              'createDefaultLayout': True,
                                              'displayInformation': {
                                                  'displayName': sheet_name,
                                                  'description': ''
                                              },
                                              'datasourceId': [{
                                                  'targetDataSourceId': self._entity_id(datasource),
                                                  'foreignKeyNames': [],
                                                  'defaultValueForAttributes': []
                                              }]})

        print('Sheet {} was created: {}/workspaces/{}/sheets/{}/views/{}'.format(sheet_name,
                                                                                 self._k.kawa_api_url,
                                                                                 self._k.active_workspace_id,
                                                                                 created_sheet.get('id'),
                                                                                 created_sheet.get('layoutIds', [])[0]))

        return created_sheet

    def delete_view(self, view):
        self._run_command(command_name='DeleteLayout',
                          command_parameters={'layoutId': self._entity_id(view)})

    def share_sheet_and_layouts(self, sheet_id: str,
                                layout_id_list: list,
                                teams_ids: list = None,
                                team_ids_with_write_permission: list = None,
                                general_access: str = None):
        """
                Change the share status flag to true for the given sheet and the given list of layouts
                in the workspace
                :param sheet_id: id of the sheet to share
                :param layout_id_list: list of sheet layout to share
                :param teams_ids: list of teams to share in read with
                :param team_ids_with_write_permission: list of teams to share in edit with
                :param general_access: general access can be: RESTRICTED / READ / EDIT
                """
        if not isinstance(teams_ids, list):
            teams_ids = []
        if not isinstance(team_ids_with_write_permission, list):
            team_ids_with_write_permission = []
        if not general_access:
            if not teams_ids and not team_ids_with_write_permission:
                general_access = 'READ'
            else:
                general_access = 'RESTRICTED'

        self._run_command(command_name='UpdateSheetAndLayoutsShareStatus',
                          command_parameters={
                              'sheetId': sheet_id,
                              'shared': True,
                              'layoutsShareStatuses': {layout_id: True for layout_id in layout_id_list},
                              'advancedSharingConfiguration':
                                  {'sharedTeamIds': teams_ids,
                                   'teamIdsWithWritePermission': team_ids_with_write_permission,
                                   'generalAccess': general_access
                                   }
                          })

    def save_layout(self, layout_id: str):
        self._run_command(command_name='SaveLayout',
                          command_parameters={
                              'layoutId': layout_id,
                          })

    def replace_layout_locked_status(self, layout_id: str, locked: bool):
        self._run_command(command_name='ReplaceLayoutLockedStatus',
                          command_parameters={
                              'layoutId': layout_id,
                              'locked': locked
                          })

    """Scripts"""

    def create_script(self, name, tool_kit_name: str, tool_name: str):
        return self._run_command(command_name='CreateScript',
                                 command_parameters={
                                     'name': name,
                                     'sourceControlToolConfiguration': {
                                         'toolKitName': tool_kit_name,
                                         'toolName': tool_name
                                     }
                                 })

    def create_script_with_content(self, name, content: str):
        return self._run_command(command_name='CreateScript',
                                 command_parameters={
                                     'name': name,
                                     'content': content
                                 })

    def replace_script(self, script_id, name, tool_kit_name, tool_name):
        return self._run_command(command_name='ReplaceScript',
                                 command_parameters={
                                     'scriptId': script_id,
                                     'name': name,
                                     'sourceControlToolConfiguration': {
                                         'toolKitName': tool_kit_name,
                                         'toolName': tool_name
                                     }
                                 })

    def create_python_private_join(self, name, sheet_id, origin_layout_id, script_id, param_mapping):
        return self._run_command(command_name='CreatePythonPrivateJoin',
                                 command_parameters={
                                     'name': name,
                                     'sheetId': sheet_id,
                                     'originLayoutId': origin_layout_id,
                                     'scriptId': script_id,
                                     'paramMapping': param_mapping
                                 })

    def start_python_private_join(self, python_private_join_entity_id,
                                  zone_id=None,
                                  script_parameters_values: Optional[dict] = None):
        if script_parameters_values is None:
            script_parameters_values = {}

        script_parameters_values = [
            {
                'scriptParameterName': param_name,
                'value': self._convert_parameter_value(param_value)
            }
            for param_name, param_value in script_parameters_values.items()
        ]

        if not zone_id:
            zone_id = tzlocal.get_localzone()
        return self._run_command(command_name='StartPythonPrivateJoin',
                                 command_parameters={
                                     'pythonPrivateJoinId': python_private_join_entity_id,
                                     'zoneId': str(zone_id),
                                     'scriptParametersValues': script_parameters_values
                                 })

    def start_runnable_tool(self,
                            script_id,
                            zone_id=None,
                            script_parameters_values: Optional[dict] = None):
        if script_parameters_values is None:
            script_parameters_values = {}

        script_parameters_values = [
            {
                'scriptParameterName': param_name,
                'value': self._convert_parameter_value(param_value)
            }
            for param_name, param_value in script_parameters_values.items()
        ]

        if not zone_id:
            zone_id = tzlocal.get_localzone()
        return self._run_command(command_name='StartRunnablePythonTool',
                                 command_parameters={
                                     'scriptId': script_id,
                                     'zoneId': str(zone_id),
                                     'scriptParametersValues': script_parameters_values
                                 })

    @staticmethod
    def _convert_parameter_value(parameter_value):
        if isinstance(parameter_value, datetime.datetime):
            return parameter_value.timestamp() * 1000
        if isinstance(parameter_value, datetime.date):
            return (parameter_value - datetime.date(1970, 1, 1)).days
        return parameter_value

    def replace_python_private_join_mapping_and_prefix(self, python_private_join_entity_id, param_mapping, prefix_name):
        return self._run_command(command_name='ReplacePythonPrivateJoinMappingAndPrefix',
                                 command_parameters={
                                     'pythonPrivateJoinId': python_private_join_entity_id,
                                     'paramMapping': param_mapping,
                                     'name': prefix_name
                                 })

    def create_secret_if_not_exist(self, key, value, description):
        return self._run_idempotent_command(command_name='CreateSecret',
                                            command_parameters={
                                                'key': key,
                                                'value': value,
                                                'description': description
                                            },
                                            entity_kind='secrets',
                                            idempotency_key=key)

    """SourceControl"""

    def set_source_control_config_to_workspace(self,
                                               workspace_id: str,
                                               api_end_point: str,
                                               token: str,
                                               repo_name: str,
                                               branch_name: str,
                                               source_control_type: SourceControlType):
        return self._run_command(command_name='SetSourceControlApiConfigurationToWorkspace',
                                 command_parameters={
                                     'workspaceId': workspace_id,
                                     'apiEndpoint': api_end_point,
                                     'token': token,
                                     'repoName': repo_name,
                                     'branchName': branch_name,
                                     'sourceControlType': source_control_type.value,
                                 })

    """License"""

    def set_license(self, path_to_license_file):
        with open(path_to_license_file, 'r') as f:
            licence = json.loads(f.read())
            self.run_command(
                command_name='SetLicense',
                command_parameters=licence
            )
