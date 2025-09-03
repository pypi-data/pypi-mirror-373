from ..kawa_base_e2e_test import KawaBaseTest
import pandas as pd
import uuid
import tempfile


class TestSheetProfiling(KawaBaseTest):
    cities_and_countries = pd.DataFrame([
        {'id': 'a', 'country': 'FR', 'measure': 2},
        {'id': 'b', 'country': 'FR', 'city': 'Lyon', 'measure': 2},
        {'id': 'c', 'country': 'FR', 'city': 'Lille', 'measure': 2},
        {'id': 'd', 'country': 'UK', 'city': 'London', 'measure': 2},
        {'id': 'e', 'country': 'UK', 'city': 'Cardiff', 'measure': 2},
        {'id': 'g', 'country': 'UK', 'city': 'Edinburgh', 'measure': 2},
        {'id': 'h', 'country': 'UK', 'city': 'Belfast', 'measure': 2},
        {'id': 'i', 'country': 'BE', 'city': 'Brussels', 'measure': 2},
        {'id': 'j', 'country': 'BE', 'city': 'Bruges', 'measure': 2},
    ])

    @classmethod
    def setUpClass(cls):
        unique_id = 'resource_{}'.format(uuid.uuid4())
        print(tempfile.gettempdir())
        KawaBaseTest.setUpClass()
        cls.sheet_name = unique_id

    def test_that_sheet_profiling_works_on_a_given_column(self):
        # setup
        df = self.cities_and_countries
        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader = self.kawa.new_data_loader(df=df, datasource_name=unique_id)
        loader.create_datasource(primary_keys=['id'])
        loader.load_data(reset_before_insert=True, create_sheet=True)

        # when
        profile = (self.kawa
                   .sheet(sheet_name=unique_id)
                   .profile(column_name='city'))

        # then
        self.assertEqual(len(profile), 1)
        self.assertDictEqual(profile['city'], {
            'COUNT': 8,
            'COUNT_UNIQUE': 8,
            'COUNT_EMPTY': 1,
        })

    def test_that_sheet_profiling_works_on_all_columns(self):
        # setup
        df = self.cities_and_countries
        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader = self.kawa.new_data_loader(df=df, datasource_name=unique_id)
        loader.create_datasource(primary_keys=['id'])
        loader.load_data(reset_before_insert=True, create_sheet=True)

        # when
        profile = self.kawa.sheet(sheet_name=unique_id).profile()

        # then
        self.assertEqual(len(profile), 4)
        self.assertDictEqual(profile['city'], {
            'COUNT': 8,
            'COUNT_UNIQUE': 8,
            'COUNT_EMPTY': 1,
        })
        self.assertDictEqual(profile['country'], {
            'COUNT': 9,
            'COUNT_UNIQUE': 3,
            'COUNT_EMPTY': 0,
        })
        self.assertDictEqual(profile['id'], {
            'COUNT': 9,
            'COUNT_UNIQUE': 9,
            'COUNT_EMPTY': 0,
        })
        self.assertDictEqual(profile['measure'], {
            'STD_DEV_POP': 0,
            'MIN': 2,
            'HIGHEST_DECILE': 2,
            'AVERAGE': 2,
            'MAX': 2,
            'LOWEST_QUARTILE': 2,
            'LOWEST_DECILE': 2,
            'SUM': 18,
            'MEDIAN': 2,
            'VAR_POP': 0,
            'HIGHEST_QUARTILE': 2,
        })
