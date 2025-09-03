import pandas as pd


class KawaReporting:

    def __init__(self, kawa_client):
        self._k = kawa_client

    def generate_user_list_report(self):
        kawa = self._k
        principals = kawa.entities.principals().list_entities()
        principal_descriptions = []
        for principal in principals:
            principal_descriptions.append({
                'internal_id': principal.get('id'),
                'email': principal.get('email'),
                'name': principal.get('displayInformation').get('displayName'),
                'unique_id': principal.get('uniqueId'),
                'forbidden_data_source_types': principal.get('forbiddenDataSourceTypes'),
                'is_admin': principal.get('role') != 'READER_ROLE',
                'status': principal.get('status'),
                'global_permissions': principal.get('permissions'),
            })

        return pd.DataFrame(principal_descriptions)

    def generate_workspace_member_list_report(self):
        kawa = self._k
        workspaces = kawa.entities.workspaces().list_entities()
        principals = kawa.entities.principals().list_entities()

        principal_descriptions = {}
        for principal in principals:
            principal_description = {
                'internal_id': principal.get('id'),
                'email': principal.get('email'),
                'name': principal.get('displayInformation').get('displayName'),
                'unique_id': principal.get('uniqueId'),
                'forbidden_data_source_types': principal.get('forbiddenDataSourceTypes'),
                'is_admin': principal.get('role') != 'READER_ROLE',
                'status': principal.get('status'),
                'global_permissions': principal.get('permissions'),
            }
            principal_descriptions[principal.get('id')] = principal_description

        members = []
        for workspace in workspaces:
            for member in workspace.get('members'):
                member_id = member.get('principalId')

                member_description = principal_descriptions.get(member_id)
                if not member_description:
                    print(f'One member does not correspond to a registered user: {member_id}')
                else:
                    is_admin = member_description.get('is_admin', False)
                    members.append({
                        'workspace': workspace.get('displayInformation').get('displayName'),
                        'name': member_description.get('name'),
                        'email': member_description.get('email'),
                        'unique_id': member_description.get('unique_id'),
                        'is_admin': member_description.get('is_admin'),
                        'can_see_all_data': is_admin or 'MANAGE_DATA_SOURCES' in member.get('permissions'),
                        'can_manage_security': is_admin or 'ROW_LEVEL_SECURITY_POLICY' in member.get('permissions'),
                        'can_manage_users': is_admin or 'MANAGE_USERS' in member.get('permissions'),
                        'workspace_permissions': ','.join(member.get('permissions')),
                    })

        return pd.DataFrame(members)
