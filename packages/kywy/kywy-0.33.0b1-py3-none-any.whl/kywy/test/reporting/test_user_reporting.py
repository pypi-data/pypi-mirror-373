from ..kawa_base_e2e_test import KawaBaseTest


class TestReporting(KawaBaseTest):

    def test_workspace_member_reporting(self):
        r = self.kawa.reporting().generate_workspace_member_list_report()
        self.assertListEqual(list(r.columns), [
            'workspace',
            'name',
            'email',
            'unique_id',
            'is_admin',
            'can_see_all_data',
            'can_manage_security',
            'can_manage_users',
            'workspace_permissions'
        ])

    def test_principal_reporting(self):
        r = self.kawa.reporting().generate_user_list_report()
        print(list(r.columns))
        self.assertListEqual(list(r.columns), [
            'internal_id',
            'email',
            'name',
            'unique_id',
            'forbidden_data_source_types',
            'is_admin',
            'status',
            'global_permissions'
        ])
