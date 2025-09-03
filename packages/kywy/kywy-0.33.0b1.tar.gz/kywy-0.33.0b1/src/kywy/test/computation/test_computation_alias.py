from ..kawa_base_e2e_test import KawaBaseTest
import pandas as pd
import uuid
import tempfile
from ...client.kawa_client import KawaClient as K


class TestComputationWithSorting(KawaBaseTest):
    cities_and_countries = pd.DataFrame([
        {'id': 'a', 'country': 'FR', 'city': 'Paris', 'measure': 1},
        {'id': 'b', 'country': 'FR', 'city': 'Lyon', 'measure': 2},
        {'id': 'c', 'country': 'FR', 'city': 'Lille', 'measure': 3},
        {'id': 'd', 'country': 'UK', 'city': 'London', 'measure': 4},
        {'id': 'e', 'country': 'UK', 'city': 'Cardiff', 'measure': 5},
        {'id': 'g', 'country': 'UK', 'city': 'Edinburgh', 'measure': 6},
        {'id': 'h', 'country': 'UK', 'city': 'Belfast', 'measure': 7},
        {'id': 'i', 'country': 'BE', 'city': 'Brussels', 'measure': 8},
        {'id': 'j', 'country': 'BE', 'city': 'Bruges', 'measure': 9},
        {'id': 'k', 'country': 'BE', 'city': 'Namur', 'measure': 10},
    ])

    @classmethod
    def setUpClass(cls):
        unique_id = 'resource_{}'.format(uuid.uuid4())
        print(tempfile.gettempdir())
        KawaBaseTest.setUpClass()
        cls.sheet_name = unique_id

    def test_that_aliases_are_taken_in_account(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader = self.kawa.new_data_loader(df=self.cities_and_countries, datasource_name=unique_id)
        loader.create_datasource(primary_keys=['id'])
        loader.load_data(reset_before_insert=True, create_sheet=True)

        # when
        df = (self.kawa.sheet(sheet_name=unique_id)
              .order_by('city', ascending=True)
              .select(K.col('measure').max().alias('max'), K.col('measure').min().alias('min'))
              .group_by('1')
              .compute())

        # then
        self.assertListEqual(list(df.columns), ['grouping(0)', 'max', 'min'])
        self.assertListEqual(list(df['grouping(0)']), ['1'])
        self.assertListEqual(list(df['max']), [10])
        self.assertListEqual(list(df['min']), [1])

    def test_that_aliases_can_be_used_in_sorting(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader = self.kawa.new_data_loader(df=self.cities_and_countries, datasource_name=unique_id)
        loader.create_datasource(primary_keys=['id'])
        loader.load_data(reset_before_insert=True, create_sheet=True)

        # when
        df = (self.kawa.sheet(sheet_name=unique_id)
              .order_by('max', ascending=True)
              .select(K.col('measure').max().alias('max'), K.col('measure').min().alias('min'))
              .compute())

        # then
        self.assertListEqual(list(df.columns), ['max', 'min'])
        self.assertListEqual(list(df['max']), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.assertListEqual(list(df['min']), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    def test_that_aliases_can_be_used_in_grouping(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader = self.kawa.new_data_loader(df=self.cities_and_countries, datasource_name=unique_id)
        loader.create_datasource(primary_keys=['id'])
        loader.load_data(reset_before_insert=True, create_sheet=True)

        # when
        df = (self.kawa
              .sheet(sheet_name=unique_id)
              .order_by('max', ascending=True)
              .select(
                K.col('measure').max().alias('max'),
                K.col('measure').min().alias('min'),
                K.col('country').alias('nation'),
              )
              .group_by('nation')
              .compute())

        # then
        self.assertListEqual(list(df.columns), ['grouping(0)', 'max', 'min', 'nation'])
        self.assertListEqual(list(df['grouping(0)']), ['FR', 'UK', 'BE'])
        self.assertListEqual(list(df['max']), [3, 7, 10])
        self.assertListEqual(list(df['min']), [1, 4, 8])
        self.assertListEqual(list(df['nation']), ['FR', 'UK', 'BE'])

    def test_that_aliases_can_be_used_in_filter(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader = self.kawa.new_data_loader(df=self.cities_and_countries, datasource_name=unique_id)
        loader.create_datasource(primary_keys=['id'])
        loader.load_data(reset_before_insert=True, create_sheet=True)

        # when
        df = (self.kawa
              .sheet(sheet_name=unique_id)
              .order_by('max', ascending=True)
              .select(
                K.col('measure').max().alias('max'),
                K.col('measure').min().alias('min'),
                K.col('country').alias('nation'),
              )
              .filter(K.col('country').eq('FR'))
              .group_by('nation')
              .compute())

        # then
        self.assertListEqual(list(df.columns), ['grouping(0)', 'max', 'min', 'nation'])
        self.assertListEqual(list(df['grouping(0)']), ['FR'])
        self.assertListEqual(list(df['max']), [3])
        self.assertListEqual(list(df['min']), [1])
        self.assertListEqual(list(df['nation']), ['FR'])

