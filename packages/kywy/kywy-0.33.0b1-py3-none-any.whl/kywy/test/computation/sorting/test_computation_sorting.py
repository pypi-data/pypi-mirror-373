from ...kawa_base_e2e_test import KawaBaseTest
import pandas as pd
import uuid
import tempfile
from ....client.kawa_client import KawaClient as K


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

    cities = ['Paris', 'Lyon', 'Lille', 'London', 'Cardiff', 'Edinburgh', 'Belfast', 'Brussels', 'Bruges', 'Namur']

    @classmethod
    def setUpClass(cls):
        unique_id = 'resource_{}'.format(uuid.uuid4())
        print(tempfile.gettempdir())
        KawaBaseTest.setUpClass()
        cls.sheet_name = unique_id

    def test_that_sort_bottom_1_can_be_extracted_when_there_is_no_grouping(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader = self.kawa.new_data_loader(df=self.cities_and_countries, datasource_name=unique_id)
        loader.create_datasource(primary_keys=['id'])
        loader.load_data(reset_before_insert=True, create_sheet=True)

        # when
        df = (self.kawa.sheet(sheet_name=unique_id)
              .order_by('city', ascending=True)
              .select(K.col('city'))
              .limit(1)
              .compute())

        # then
        self.assertListEqual(list(df.columns), ['city'])
        self.assertListEqual(list(df['city']), ['Belfast'])

    def test_that_sort_bottom_group_can_be_extracted(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader = self.kawa.new_data_loader(df=self.cities_and_countries, datasource_name=unique_id)
        loader.create_datasource(primary_keys=['id'])
        loader.load_data(reset_before_insert=True, create_sheet=True)

        # when
        df = (self.kawa.sheet(sheet_name=unique_id)
              .order_by('measure', ascending=True)
              .select(K.col('measure').sum())
              .group_by('country')
              .limit(1)
              .compute())

        # then
        self.assertListEqual(list(df.columns), ['grouping(0)', 'measure'])
        self.assertListEqual(list(df['grouping(0)']), ['FR'])
        self.assertListEqual(list(df['measure']), [6])

    def test_that_sort_top_1_can_be_extracted_when_there_is_no_grouping(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader = self.kawa.new_data_loader(df=self.cities_and_countries, datasource_name=unique_id)
        loader.create_datasource(primary_keys=['id'])
        loader.load_data(reset_before_insert=True, create_sheet=True)

        # when
        df = (self.kawa.sheet(sheet_name=unique_id)
              .order_by('city', ascending=False)
              .select(K.col('city'))
              .limit(1)
              .compute())

        # then
        self.assertListEqual(list(df.columns), ['city'])
        self.assertListEqual(list(df['city']), ['Paris'])

    def test_that_sort_top_group_can_be_extracted(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader = self.kawa.new_data_loader(df=self.cities_and_countries, datasource_name=unique_id)
        loader.create_datasource(primary_keys=['id'])
        loader.load_data(reset_before_insert=True, create_sheet=True)

        # when
        df = (self.kawa.sheet(sheet_name=unique_id)
              .order_by('measure', ascending=False)
              .select(K.col('measure').sum())
              .group_by('country')
              .limit(1)
              .compute())

        # then
        self.assertListEqual(list(df.columns), ['grouping(0)', 'measure'])
        self.assertListEqual(list(df['grouping(0)']), ['BE'])
        self.assertListEqual(list(df['measure']), [27])

    def test_that_sort_ascending_works_without_group_by(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader = self.kawa.new_data_loader(df=self.cities_and_countries, datasource_name=unique_id)
        loader.create_datasource(primary_keys=['id'])
        loader.load_data(reset_before_insert=True, create_sheet=True)

        # when
        df = (self.kawa.sheet(sheet_name=unique_id)
              .order_by('city', ascending=True)
              .select(K.col('city'))
              .compute())

        # then
        self.assertListEqual(list(df.columns), ['city'])
        self.cities.sort()
        self.assertListEqual(list(df['city']), self.cities)

    def test_that_sort_descending_works_without_group_by(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader = self.kawa.new_data_loader(df=self.cities_and_countries, datasource_name=unique_id)
        loader.create_datasource(primary_keys=['id'])
        loader.load_data(reset_before_insert=True, create_sheet=True)

        # when
        df = (self.kawa.sheet(sheet_name=unique_id)
              .order_by('city', ascending=False)
              .select(K.col('city'))
              .compute())

        # then
        self.assertListEqual(list(df.columns), ['city'])
        self.cities.sort(reverse=True)
        self.assertListEqual(list(df['city']), self.cities)

    def test_that_sort_ascending_works_with_group_by(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader = self.kawa.new_data_loader(df=self.cities_and_countries, datasource_name=unique_id)
        loader.create_datasource(primary_keys=['id'])
        loader.load_data(reset_before_insert=True, create_sheet=True)

        # when
        df = (self.kawa.sheet(sheet_name=unique_id)
              .group_by('country')
              .order_by('measure', ascending=True)
              .select(K.col('measure').sum())
              .compute())

        # then
        self.assertListEqual(list(df.columns), ['grouping(0)', 'measure'])
        self.assertListEqual(list(df['measure']), [6, 22, 27])
        self.assertListEqual(list(df['grouping(0)']), ['FR', 'UK', 'BE'])

    def test_that_sort_descending_works_with_group_by(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader = self.kawa.new_data_loader(df=self.cities_and_countries, datasource_name=unique_id)
        loader.create_datasource(primary_keys=['id'])
        loader.load_data(reset_before_insert=True, create_sheet=True)

        # when
        df = (self.kawa.sheet(sheet_name=unique_id)
              .group_by('country')
              .order_by('measure', ascending=False)
              .select(K.col('measure').sum())
              .compute())

        # then
        self.assertListEqual(list(df.columns), ['grouping(0)', 'measure'])
        self.assertListEqual(list(df['measure']), [27, 22, 6])
        self.assertListEqual(list(df['grouping(0)']), ['BE', 'UK', 'FR'])
