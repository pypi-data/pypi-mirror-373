import pandas as pd
from datetime import date
import uuid

from ..kawa_base_e2e_test import KawaBaseTest


class TestPartitionManagement(KawaBaseTest):

    def test_that_primary_keys_order_is_respected_on_datasource_creation(self):
        # given
        unique_id = 'resource_{}'.format(uuid.uuid4())
        dtf1 = pd.DataFrame([{
            'int1': 1,
            'date': date(2024, 1, 1),
            'int3': 1,
            'int2': 1,
            'int4': 1}])

        loader = self.kawa.new_data_loader(
            df=dtf1,
            datasource_name=unique_id)

        # when
        datasource = loader.create_datasource(primary_keys=['int1', 'date', 'int3', 'int2', 'int4'])
        create_table_before_indexing = self.kawa.entities.get_datasource_schema(
            datasource_id=datasource.get('id')).get('schema')

        # then
        self.assertIn('PRIMARY KEY (int1, date, int3, int2, int4)', create_table_before_indexing)
        self.assertIn('ORDER BY (int1, date, int3, int2, int4)', create_table_before_indexing)

    def test_that_primary_keys_order_is_respected_when_updating_them(self):
        # given
        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader = self.kawa.new_data_loader(
            df=pd.DataFrame([{
                'int1': 1,
                'date': date(2024, 1, 1),
                'int3': 1,
                'int2': 1,
                'int4': 1}]),
            datasource_name=unique_id)

        # when
        datasource = loader.create_datasource(primary_keys=['int1', 'date', 'int2'])
        create_table_before_indexing = self.kawa.entities.get_datasource_schema(
            datasource_id=datasource.get('id')).get('schema')

        # and
        self.commands.replace_datasource_primary_keys(
            datasource=datasource,
            new_primary_keys=['int2', 'int1', 'int4', 'date', 'int3'])
        create_table_after_indexing = self.kawa.entities.get_datasource_schema(
            datasource_id=datasource.get('id')).get('schema')

        # then
        self.assertIn('PRIMARY KEY (int1, date, int2)', create_table_before_indexing)
        self.assertIn('ORDER BY (int1, date, int2)', create_table_before_indexing)
        self.assertIn('PRIMARY KEY (int2, int1, int4, date, int3)', create_table_after_indexing)
        self.assertIn('ORDER BY (int2, int1, int4, date, int3)', create_table_after_indexing)

    def test_that_a_partition_is_correctly_dropped(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        dtf1 = pd.DataFrame([
            {'date': date(2024, 1, 1), 'int': 1},
            {'date': date(2024, 1, 1), 'int': 2},
            {'date': date(2024, 1, 1), 'int': 3},
            {'date': date(2024, 1, 2), 'int': 4},
            {'date': date(2024, 1, 2), 'int': 5},
            {'date': date(2024, 1, 3), 'int': 6},
            {'date': date(2024, 1, 3), 'int': 7},
        ])

        loader = self.kawa.new_data_loader(df=dtf1, datasource_name=unique_id)
        loader.create_datasource()
        datasource = loader.load_data(reset_before_insert=True, create_sheet=True)
        self.commands.replace_datasource_primary_keys(datasource=datasource,
                                                      new_primary_keys=['date', 'record_id'],
                                                      partition_key='date')

        create_table = self.kawa.entities.get_datasource_schema(datasource_id=datasource.get('id')).get('schema')

        # given
        computed_df_before_partition_drop = self.kawa.sheet(sheet_name=unique_id).select('date', 'int').compute()

        # when
        self.commands.drop_date_partition(datasource=datasource, date_partition=date(2024, 1, 1))
        computed_df_after_partition_drop = self.kawa.sheet(sheet_name=unique_id).select('date', 'int').compute()

        # then: computation before drop is correct
        self.assertListEqual(list(computed_df_before_partition_drop['int']), list(range(1, 8)))
        self.assertListEqual(list(computed_df_before_partition_drop['date']), [
            date(2024, 1, 1),
            date(2024, 1, 1),
            date(2024, 1, 1),
            date(2024, 1, 2),
            date(2024, 1, 2),
            date(2024, 1, 3),
            date(2024, 1, 3)
        ])

        # and: computation after drop is correct
        self.assertListEqual(list(computed_df_after_partition_drop['int']), [4, 5, 6, 7])
        self.assertListEqual(list(computed_df_after_partition_drop['date']), [
            date(2024, 1, 2),
            date(2024, 1, 2),
            date(2024, 1, 3),
            date(2024, 1, 3)
        ])

        # and: check the schema
        self.assertIn('PRIMARY KEY (date, record_id)', create_table)
        self.assertIn('ORDER BY (date, record_id)', create_table)
        self.assertIn('PARTITION BY date', create_table)

    def test_that_a_partition_is_created_with_up_sampling(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        dtf1 = pd.DataFrame([
            {'date': date(2024, 1, 1), 'int': 1},
            {'date': date(2024, 1, 1), 'int': 2},
            {'date': date(2024, 1, 1), 'int': 3},
            {'date': date(2024, 1, 2), 'int': 4},
            {'date': date(2024, 1, 2), 'int': 5},
            {'date': date(2024, 1, 3), 'int': 6},
            {'date': date(2024, 1, 3), 'int': 7},
        ])

        loader = self.kawa.new_data_loader(df=dtf1, datasource_name=unique_id)
        loader.create_datasource()
        datasource = loader.load_data(reset_before_insert=True, create_sheet=True)

        # when
        self.commands.replace_datasource_primary_keys(datasource=datasource,
                                                      new_primary_keys=['date', 'record_id'],
                                                      partition_key='date',
                                                      partition_sampler='YEAR')

        create_table = self.kawa.entities.get_datasource_schema(datasource_id=datasource.get('id')).get('schema')

        # and: check the schema
        self.assertIn('PRIMARY KEY (date, record_id)', create_table)
        self.assertIn('ORDER BY (date, record_id)', create_table)
        self.assertIn('PARTITION BY toString(toYear(addDays(toDate32(0), date)))', create_table)

    def test_that_a_partition_is_maintained_after_reset_data(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        dtf1 = pd.DataFrame([
            {'date': date(2024, 1, 1), 'int': 1},
            {'date': date(2024, 1, 1), 'int': 2},
            {'date': date(2024, 1, 1), 'int': 3},
            {'date': date(2024, 1, 2), 'int': 4},
            {'date': date(2024, 1, 2), 'int': 5},
            {'date': date(2024, 1, 3), 'int': 6},
            {'date': date(2024, 1, 3), 'int': 7},
        ])

        loader = self.kawa.new_data_loader(df=dtf1, datasource_name=unique_id)
        loader.create_datasource()
        datasource = loader.load_data(reset_before_insert=True, create_sheet=True)
        self.commands.replace_datasource_primary_keys(datasource=datasource,
                                                      new_primary_keys=['date', 'record_id'],
                                                      partition_key='date',
                                                      partition_sampler='YEAR')

        # when
        loader2 = self.kawa.new_data_loader(df=dtf1, datasource_name=unique_id)
        datasource = loader2.load_data(reset_before_insert=True, create_sheet=False)

        create_table = self.kawa.entities.get_datasource_schema(datasource_id=datasource.get('id')).get('schema')

        # and: check the schema
        self.assertIn('PRIMARY KEY (date, record_id)', create_table)
        self.assertIn('ORDER BY (date, record_id)', create_table)
        self.assertIn('PARTITION BY toString(toYear(addDays(toDate32(0), date)))', create_table)

    def test_that_replace_datasource_primary_keys_is_idempotent(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        dtf1 = pd.DataFrame([
            {'date': date(2024, 1, 1), 'int': 1},
            {'date': date(2024, 1, 1), 'int': 2},
            {'date': date(2024, 1, 1), 'int': 3},
            {'date': date(2024, 1, 2), 'int': 4},
            {'date': date(2024, 1, 2), 'int': 5},
            {'date': date(2024, 1, 3), 'int': 6},
            {'date': date(2024, 1, 3), 'int': 7},
        ])

        loader = self.kawa.new_data_loader(df=dtf1, datasource_name=unique_id)
        loader.create_datasource()
        ds0 = loader.load_data(reset_before_insert=True, create_sheet=True)

        # when
        ds1 = self.commands.replace_datasource_primary_keys(datasource=ds0,
                                                            new_primary_keys=['date', 'record_id'],
                                                            partition_key='date')

        ds2 = self.commands.replace_datasource_primary_keys(datasource=ds1,
                                                            new_primary_keys=['date', 'record_id'],
                                                            partition_key='date')

        ds3 = self.commands.replace_datasource_primary_keys(datasource=ds1,
                                                            new_primary_keys=['date', 'record_id'],
                                                            partition_key='date',
                                                            partition_sampler='MONTH')

        ds4 = self.commands.replace_datasource_primary_keys(datasource=ds3,
                                                            new_primary_keys=['date', 'record_id'],
                                                            partition_key='date',
                                                            partition_sampler='MONTH')

        ds5 = self.commands.replace_datasource_primary_keys(datasource=ds4,
                                                            new_primary_keys=['record_id', 'date'],
                                                            partition_key='date',
                                                            partition_sampler='MONTH')

        ds6 = self.commands.replace_datasource_primary_keys(datasource=ds5,
                                                            new_primary_keys=['record_id', 'date'])

        ds7 = self.commands.replace_datasource_primary_keys(datasource=ds6,
                                                            new_primary_keys=['record_id', 'date'])

        ds8 = self.commands.replace_datasource_primary_keys(datasource=ds6,
                                                            new_primary_keys=['date', 'record_id'])

        # then
        self.assertEqual(ds0['version'] + 1, ds1['version'])
        self.assertEqual(ds1['version'], ds2['version'])  # Version did not change there
        self.assertEqual(ds2['version'] + 1, ds3['version'])
        self.assertEqual(ds3['version'], ds4['version'])
        self.assertEqual(ds4['version'] + 1, ds5['version'])
        self.assertEqual(ds5['version'] + 1, ds6['version'])
        self.assertEqual(ds6['version'], ds7['version'])
        self.assertEqual(ds7['version'] + 1, ds8['version'])
