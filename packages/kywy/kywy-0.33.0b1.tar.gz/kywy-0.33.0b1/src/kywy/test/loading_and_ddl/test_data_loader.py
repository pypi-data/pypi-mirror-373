import pandas as pd
from datetime import date, datetime
import zoneinfo
import uuid
import math
import time

from ..kawa_base_e2e_test import KawaBaseTest


class TestDataLoader(KawaBaseTest):

    def test_that_datasource_is_properly_defined(self):
        # setup
        loader = self.kawa.new_data_loader(
            df=pd.DataFrame([{'boolean1': True, 'text1': 'bar', 'measure1': 1.124}]),
            datasource_name=' Orders')

        # when
        ds = loader._define_data_source_from_df(primary_keys=['text1'])

        # then
        self.assertFalse(ds['shared'])
        self.assertEqual(ds['displayInformation']['displayName'], 'Orders')
        self.assertEqual(ds['storageConfiguration']['loadingAdapterName'], 'CLICKHOUSE')
        self.assertEqual(len(ds['indicators']), 3)

        self.assertEqual(ds['indicators'][0]['displayInformation']['displayName'], 'boolean1')
        self.assertEqual(ds['indicators'][0]['indicatorId'], 'boolean1')
        self.assertEqual(ds['indicators'][0]['type'], 'boolean')
        self.assertIsNone(ds['indicators'][0].get('key'))
        self.assertFalse(ds['indicators'][0]['storageConfig']['indexed'])

        self.assertEqual(ds['indicators'][1]['displayInformation']['displayName'], 'text1')
        self.assertEqual(ds['indicators'][1]['indicatorId'], 'text1')
        self.assertEqual(ds['indicators'][1]['type'], 'text')
        self.assertEqual(ds['indicators'][1]['key']['keyType'], 'PRIMARY_SHARDING_KEY')
        self.assertTrue(ds['indicators'][1]['storageConfig']['indexed'])

        self.assertEqual(ds['indicators'][2]['displayInformation']['displayName'], 'measure1')
        self.assertEqual(ds['indicators'][2]['indicatorId'], 'measure1')
        self.assertEqual(ds['indicators'][2]['type'], 'decimal')
        self.assertIsNone(ds['indicators'][2].get('key'))
        self.assertFalse(ds['indicators'][2]['storageConfig']['indexed'])

    def test_that_an_auto_increment_is_added(self):
        # setup
        loader = self.kawa.new_data_loader(
            df=pd.DataFrame([{'boolean1': True, 'text1': 'bar', 'measure1': 1.124}]),
            datasource_name='Orders')

        # when
        ds = loader._define_data_source_from_df()

        # then
        self.assertFalse(ds['shared'])
        self.assertEqual(ds['displayInformation']['displayName'], 'Orders')
        self.assertEqual(ds['storageConfiguration']['loadingAdapterName'], 'CLICKHOUSE')
        self.assertEqual(len(ds['indicators']), 4)

        self.assertEqual(ds['indicators'][0]['displayInformation']['displayName'], 'record_id')
        self.assertEqual(ds['indicators'][0]['indicatorId'], 'record_id')
        self.assertEqual(ds['indicators'][0]['type'], 'integer')
        self.assertIsNotNone(ds['indicators'][0].get('key'))
        self.assertEqual(ds['indicators'][0]['key']['keyType'], 'PRIMARY_SHARDING_KEY')
        self.assertTrue(ds['indicators'][0]['storageConfig']['indexed'])

        self.assertEqual(ds['indicators'][1]['displayInformation']['displayName'], 'boolean1')
        self.assertEqual(ds['indicators'][1]['indicatorId'], 'boolean1')
        self.assertEqual(ds['indicators'][1]['type'], 'boolean')
        self.assertIsNone(ds['indicators'][1].get('key'))
        self.assertFalse(ds['indicators'][1]['storageConfig']['indexed'])

        self.assertEqual(ds['indicators'][2]['displayInformation']['displayName'], 'text1')
        self.assertEqual(ds['indicators'][2]['indicatorId'], 'text1')
        self.assertEqual(ds['indicators'][2]['type'], 'text')
        self.assertIsNone(ds['indicators'][2].get('key'))
        self.assertFalse(ds['indicators'][2]['storageConfig']['indexed'])

        self.assertEqual(ds['indicators'][3]['displayInformation']['displayName'], 'measure1')
        self.assertEqual(ds['indicators'][3]['indicatorId'], 'measure1')
        self.assertEqual(ds['indicators'][3]['type'], 'decimal')
        self.assertIsNone(ds['indicators'][3].get('key'))
        self.assertFalse(ds['indicators'][3]['storageConfig']['indexed'])

    def test_that_array_types_are_correctly_introspected(self):
        # setup
        df = pd.DataFrame([
            {
                'array_of_texts_1': None,
                'array_of_texts_2': ['foo'],
                'array_of_decimals_1': None,
            },
            {
                'array_of_texts_1': [],
                'array_of_texts_2': [1],
                'array_of_decimals_1': [1.0, 2.0, 3.0],
            },
            {
                'array_of_texts_1': [None, 'bar'],
                'array_of_texts_3': ['foo', 1],
                'array_of_integers_1': [1],
            },
        ])
        loader = self.kawa.new_data_loader(df=df, datasource_name='Foo')

        # when
        introspection = loader._introspect_df()

        # then
        self.assertEqual(introspection['array_of_texts_1'], 'list(integer,text)')
        self.assertEqual(introspection['array_of_texts_2'], 'list(integer,text)')
        self.assertEqual(introspection['array_of_texts_3'], 'list(integer,text)')
        self.assertEqual(introspection['array_of_decimals_1'], 'list(integer,decimal)')
        self.assertEqual(introspection['array_of_integers_1'], 'list(integer,integer)')

    def test_that_basic_types_are_correctly_introspected(self):
        # setup
        df = pd.DataFrame([
            {'boolean': True},
            {'boolean': True, 'text1': 'bar'},
            {'boolean': True},
            {'boolean': True, 'text1': None},
        ])
        df['text2'] = df['text1'].astype('string')
        loader = self.kawa.new_data_loader(df=df, datasource_name='Foo')

        # when
        introspection = loader._introspect_df()

        # then
        self.assertEqual(introspection['boolean'], 'boolean')
        self.assertEqual(introspection['text1'], 'text')
        self.assertEqual(introspection['text2'], 'text')

    def test_that_numeric_types_are_correctly_introspected(self):
        # setup
        df = pd.DataFrame([{'int': 12, 'float': 1.23}])
        df['int8'] = df['int'].astype('int8')
        df['int16'] = df['int'].astype('int16')
        df['int32'] = df['int'].astype('int32')
        df['int64'] = df['int'].astype('int64')
        df['uint8'] = df['int'].astype('uint8')
        df['uint16'] = df['int'].astype('uint16')
        df['uint32'] = df['int'].astype('uint32')
        df['uint64'] = df['int'].astype('uint64')
        df['float16'] = df['float'].astype('float16')
        df['float32'] = df['float'].astype('float32')
        df['float64'] = df['float'].astype('float64')
        loader = self.kawa.new_data_loader(df=df, datasource_name='Foo')

        # when
        introspection = loader._introspect_df()

        # then
        self.assertEqual(introspection['int'], 'integer')
        self.assertEqual(introspection['int8'], 'integer')
        self.assertEqual(introspection['int16'], 'integer')
        self.assertEqual(introspection['int32'], 'integer')
        self.assertEqual(introspection['int64'], 'integer')
        self.assertEqual(introspection['uint8'], 'integer')
        self.assertEqual(introspection['uint16'], 'integer')
        self.assertEqual(introspection['uint32'], 'integer')
        self.assertEqual(introspection['uint64'], 'integer')
        self.assertEqual(introspection['float'], 'decimal')
        self.assertEqual(introspection['float16'], 'decimal')
        self.assertEqual(introspection['float32'], 'decimal')
        self.assertEqual(introspection['float64'], 'decimal')

    def test_that_temporal_types_are_correctly_introspected(self):
        # setup
        pacific = zoneinfo.ZoneInfo('US/Pacific')
        utc = zoneinfo.ZoneInfo('UTC')
        df = pd.DataFrame([{
            # DATE TYPE
            'date': date(2023, 1, 1),
            # DATE TIME TYPE
            'date_time_us_pacific': datetime(2023, 1, 1, 23, 23, 2, tzinfo=pacific),
            'date_time_utc': datetime(2023, 1, 1, 23, 23, 2, tzinfo=utc),
            'date_time_no_tz': datetime(2023, 1, 1, 23, 23, 2),
            # TIMESTAMP TYPE
            'ts_us_pacific': pd.Timestamp(year=2023, month=1, day=1, hour=23, minute=23, second=2, tz='US/Pacific'),
            'ts_utc': pd.Timestamp(year=2023, month=1, day=1, hour=23, minute=23, second=2, tz='utc'),
            'ts_no_tz': pd.Timestamp(year=2023, month=1, day=1, hour=23, minute=23, second=2),
        }])
        loader = self.kawa.new_data_loader(df=df, datasource_name='Foo')

        # when
        introspection = loader._introspect_df()

        # then
        self.assertEqual(introspection['date'], 'date')
        self.assertEqual(introspection['date_time_us_pacific'], 'date_time')
        self.assertEqual(introspection['date_time_utc'], 'date_time')
        self.assertEqual(introspection['date_time_no_tz'], 'date_time')
        self.assertEqual(introspection['ts_us_pacific'], 'date_time')
        self.assertEqual(introspection['ts_utc'], 'date_time')
        self.assertEqual(introspection['ts_no_tz'], 'date_time')

    def test_that_ingestion_without_primary_key_correctly_uses_auto_increment(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        dtf1 = pd.DataFrame([
            {'boolean1': True, 'text1': 'bar', 'integer1': 1},
            {'boolean1': True, 'text1': 'bar', 'integer1': 1},
            {'boolean1': True, 'text1': 'bar', 'integer1': 1},
        ])
        loader = self.kawa.new_data_loader(df=dtf1, datasource_name=unique_id)
        loader.create_datasource()

        # when
        loader.load_data(reset_before_insert=True, create_sheet=True)
        loader.load_data(reset_before_insert=False)
        loader.load_data(reset_before_insert=False)

        # then
        computed_df = (self.kawa
                       .sheet(sheet_name=unique_id)
                       .select('boolean1', 'text1', 'integer1', 'record_id')
                       .compute())
        self.assertEqual(computed_df.shape[0], 9)
        for row_id in range(9):
            self.assertTrue(computed_df['boolean1'][row_id])
            self.assertEqual(computed_df['text1'][row_id], 'bar')
            self.assertEqual(computed_df['integer1'][row_id], 1)
            self.assertEqual(computed_df['record_id'][row_id], row_id + 1)

    def test_that_optimize_after_insert_remove_duplicate_pk(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader1 = self.kawa.new_data_loader(
            df=pd.DataFrame([
                {'key': 'k1', 'value': 11},
                {'key': 'k2', 'value': 12},
                {'key': 'k3', 'value': 13},
            ]),
            datasource_name=unique_id
        )
        loader1.create_datasource(primary_keys=['key'])
        loader1.load_data(reset_before_insert=True, create_sheet=True)

        loader2 = self.kawa.new_data_loader(
            df=pd.DataFrame([
                {'key': 'k4', 'value': 24},
                {'key': 'k5', 'value': 25},
                {'key': 'k3', 'value': 23},
            ]),
            datasource_name=unique_id
        )

        # when
        loader2.load_data(reset_before_insert=False, optimize_after_insert=True)

        # then
        computed_df = (self.kawa
                       .sheet(sheet_name=unique_id)
                       .select('key', 'value')
                       .compute())
        self.assertEqual(computed_df.shape[0], 5)
        self.assertListEqual(list(computed_df['key']), ['k1', 'k2', 'k3', 'k4', 'k5'])
        self.assertListEqual(list(computed_df['value']), [11, 12, 23, 24, 25])

    def test_that_optimize_after_insert_does_not_remove_duplicate_pk_when_not_optimized(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader1 = self.kawa.new_data_loader(
            df=pd.DataFrame([
                {'key': 'k1', 'value': 11},
                {'key': 'k2', 'value': 12},
                {'key': 'k3', 'value': 13},
            ]),
            datasource_name=unique_id
        )
        loader1.create_datasource(primary_keys=['key'])
        loader1.load_data(reset_before_insert=True, create_sheet=True)

        loader2 = self.kawa.new_data_loader(
            df=pd.DataFrame([
                {'key': 'k4', 'value': 24},
                {'key': 'k5', 'value': 25},
                {'key': 'k3', 'value': 23},
            ]),
            datasource_name=unique_id
        )

        # when
        loader2.load_data(reset_before_insert=False)

        # then
        computed_df = (self.kawa
                       .sheet(sheet_name=unique_id)
                       .select('key', 'value')
                       .compute())
        self.assertEqual(computed_df.shape[0], 6)
        self.assertListEqual(list(computed_df['key']), ['k1', 'k2', 'k3', 'k3', 'k4', 'k5'])
        self.assertListEqual(list(computed_df['value']), [11, 12, 23, 13, 24, 25])

    def test_that_command_force_entries_deduplication_removes_duplicates(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader1 = self.kawa.new_data_loader(
            df=pd.DataFrame([
                {'key': 'k1', 'value': 11},
                {'key': 'k2', 'value': 12},
                {'key': 'k3', 'value': 13},
            ]),
            datasource_name=unique_id
        )
        ds = loader1.create_datasource(primary_keys=['key'])
        loader1.load_data(reset_before_insert=True, create_sheet=True)

        loader2 = self.kawa.new_data_loader(
            df=pd.DataFrame([
                {'key': 'k4', 'value': 24},
                {'key': 'k5', 'value': 25},
                {'key': 'k3', 'value': 23},
            ]),
            datasource_name=unique_id
        )

        # when
        loader2.load_data(reset_before_insert=False)

        # then
        computed_df = (self.kawa
                       .sheet(sheet_name=unique_id)
                       .select('key', 'value')
                       .compute())
        self.assertEqual(computed_df.shape[0], 6)
        self.assertListEqual(list(computed_df['key']), ['k1', 'k2', 'k3', 'k3', 'k4', 'k5'])
        self.assertListEqual(list(computed_df['value']), [11, 12, 23, 13, 24, 25])

        # after
        self.kawa.commands.force_entries_deduplication(datasource=ds)

        # then
        computed_df = (self.kawa
                       .sheet(sheet_name=unique_id)
                       .select('key', 'value')
                       .compute())
        self.assertEqual(computed_df.shape[0], 5)
        self.assertListEqual(list(computed_df['key']), ['k1', 'k2', 'k3', 'k4', 'k5'])
        self.assertListEqual(list(computed_df['value']), [11, 12, 23, 24, 25])

    def test_that_reset_data_clears_data_between_each_load(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        dtf1 = pd.DataFrame([
            {'boolean1': True, 'text1': 'bar', 'integer1': 1},
            {'boolean1': True, 'text1': 'bar', 'integer1': 1},
            {'boolean1': True, 'text1': 'bar', 'integer1': 1},
        ])
        loader = self.kawa.new_data_loader(df=dtf1, datasource_name=unique_id)
        loader.create_datasource()

        # when
        loader.load_data(reset_before_insert=True, create_sheet=True)
        loader.load_data(reset_before_insert=True)
        loader.load_data(reset_before_insert=True)

        # then
        computed_df = (self.kawa
                       .sheet(sheet_name=unique_id)
                       .select('boolean1', 'text1', 'integer1', 'record_id')
                       .compute())
        self.assertEqual(computed_df.shape[0], 3)
        for row_id in range(3):
            self.assertTrue(computed_df['boolean1'][row_id])
            self.assertEqual(computed_df['text1'][row_id], 'bar')
            self.assertEqual(computed_df['integer1'][row_id], 1)
            self.assertEqual(computed_df['record_id'][row_id], row_id + 1)

    def test_that_ingestion_works_when_omitting_columns(self):
        # setup
        utc = zoneinfo.ZoneInfo('UTC')
        unique_id = 'resource_{}'.format(uuid.uuid4())
        row1 = pd.DataFrame([{
            'boolean': True,
            'text': 'bar',
            'integer': 1,
            'decimal': 3.14,
            'date': date(2023, 1, 1),
            'date_time': datetime(2023, 1, 1, 23, 23, 2),
        }])
        row2 = pd.DataFrame([{}])

        loader1 = self.kawa.new_data_loader(df=row1, datasource_name=unique_id)
        loader2 = self.kawa.new_data_loader(df=row2, datasource_name=unique_id)

        loader1.create_datasource()

        # when
        loader1.load_data(reset_before_insert=True, create_sheet=True)
        loader2.load_data(reset_before_insert=False)

        # then
        computed_df = (self.kawa
                       .sheet(sheet_name=unique_id)
                       .select('boolean', 'text', 'integer', 'decimal', 'date', 'date_time', 'record_id')
                       .compute())

        self.assertTrue(computed_df['boolean'][0])
        self.assertEqual(computed_df['text'][0], 'bar')
        self.assertEqual(computed_df['integer'][0], 1)
        self.assertEqual(computed_df['decimal'][0], 3.14)
        self.assertEqual(computed_df['date'][0], date(2023, 1, 1))
        self.assertEqual(computed_df['decimal'][0], 3.14)
        self.assertEqual(computed_df['date_time'][0].timestamp(),
                         datetime(2023, 1, 1, 23, 23, 2, tzinfo=utc).timestamp())

        self.assertIsNone(computed_df['boolean'][1])
        self.assertEqual(computed_df['text'][1], '')
        self.assertTrue(math.isnan(computed_df['integer'][1]))
        self.assertTrue(math.isnan(computed_df['decimal'][1]))
        self.assertEqual(computed_df['date'][1], date(1970, 1, 1))
        self.assertEqual(computed_df['date_time'][1].timestamp(), 0)

    def test_that_every_data_type_is_properly_ingested(self):
        # setup
        pacific = zoneinfo.ZoneInfo('US/Pacific')
        utc = zoneinfo.ZoneInfo('UTC')
        unique_id = 'resource_{}'.format(uuid.uuid4())
        dtf = pd.DataFrame([{
            # Arrays
            # FIXME: Bug when computing arrays of texts, returns empty text values
            'array_of_texts': ['foo', 'bar'],
            'array_of_numbers': [1.1, -2.2],
            'array_of_integers': [1, -2],

            # Date
            'date': date(2023, 1, 1),  # No idea why this works perfectly - need to investigate

            # Date + Time
            "date_time_utc": datetime(2023, 1, 1, 23, 23, 2, tzinfo=utc),
            "date_time_us_pacific": datetime(2023, 1, 1, 23, 23, 2, tzinfo=pacific),
            "date_time_no_tz": datetime(2023, 1, 1, 23, 23, 2),

            "ts_us_pacific": pd.Timestamp(year=2023, month=1, day=1, hour=23, minute=23, second=2, tz='US/Pacific'),
            "ts_utc": pd.Timestamp(year=2023, month=1, day=1, hour=23, minute=23, second=2, tz='utc'),
            "ts_no_tz": pd.Timestamp(year=2023, month=1, day=1, hour=23, minute=23, second=2),

            # Basic types
            'boolean1': True,
            'text1': 'bar',
            'integer1': 1,
            'measure1': 4.4
        }])

        dtypes = dtf.dtypes.to_dict()

        m = ''
        for col_name, typ in dtypes.items():
            m += f'dataframe[{col_name}].dtype == {typ}\n'

        loader = self.kawa.new_data_loader(df=dtf, datasource_name=unique_id)
        loader.create_datasource(primary_keys=['text1'])

        # when
        loader.load_data(reset_before_insert=False, create_sheet=True)

        # then
        computed_df = self.kawa.sheet(sheet_name=unique_id).select(
            'date',
            'boolean1',
            'text1',
            'measure1',
            'integer1',
            'array_of_texts',
            'array_of_numbers',
            'array_of_integers',
            'date_time_utc',
            'date_time_no_tz',
            'date_time_us_pacific',
            'ts_us_pacific',
            'ts_utc',
            'ts_no_tz').compute()

        self.assertTrue(computed_df['boolean1'][0])
        self.assertEqual(computed_df['text1'][0], 'bar')
        self.assertEqual(computed_df['measure1'][0], 4.4)
        self.assertEqual(computed_df['integer1'][0], 1)
        self.assertListEqual(list(computed_df['array_of_numbers'][0]), [1.1, -2.2])
        self.assertListEqual(list(computed_df['array_of_integers'][0]), [1, -2])
        self.assertEqual(computed_df['date'][0], date(2023, 1, 1))
        self.assertEqual(computed_df['date'][0], date(2023, 1, 1))
        self.assertEqual(computed_df['date_time_utc'][0].timestamp(),
                         datetime(2023, 1, 1, 23, 23, 2, tzinfo=utc).timestamp())
        self.assertEqual(computed_df['date_time_us_pacific'][0].timestamp(),
                         datetime(2023, 1, 1, 23, 23, 2, tzinfo=pacific).timestamp())
        self.assertEqual(computed_df['date_time_no_tz'][0].timestamp(),
                         datetime(2023, 1, 1, 23, 23, 2, tzinfo=utc).timestamp())
        self.assertEqual(computed_df['ts_utc'][0].timestamp(),
                         datetime(2023, 1, 1, 23, 23, 2, tzinfo=utc).timestamp())
        self.assertEqual(computed_df['ts_us_pacific'][0].timestamp(),
                         datetime(2023, 1, 1, 23, 23, 2, tzinfo=pacific).timestamp())
        self.assertEqual(computed_df['ts_no_tz'][0].timestamp(),
                         datetime(2023, 1, 1, 23, 23, 2, tzinfo=utc).timestamp())

    def test_that_data_is_properly_ingested_on_multiple_threads_with_auto_increment(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader1 = self.kawa.new_data_loader(
            df=pd.DataFrame([
                {'date': date(2024, 1, 1), 'int': 1},
                {'date': date(2024, 1, 1), 'int': 2},
                {'date': date(2024, 1, 1), 'int': 3},
                {'date': date(2024, 1, 2), 'int': 4},
                {'date': date(2024, 1, 2), 'int': 5},
                {'date': date(2024, 1, 3), 'int': 6},
                {'date': date(2024, 1, 3), 'int': 7},
            ]),
            datasource_name=unique_id)
        loader2 = self.kawa.new_data_loader(
            df=pd.DataFrame([
                {'date': date(2024, 1, 1), 'int': 8},
                {'date': date(2024, 1, 1), 'int': 9},
                {'date': date(2024, 1, 1), 'int': 10},
                {'date': date(2024, 1, 2), 'int': 11},
                {'date': date(2024, 1, 2), 'int': 12},
                {'date': date(2024, 1, 3), 'int': 13},
                {'date': date(2024, 1, 3), 'int': 14},
            ]),
            datasource_name=unique_id)
        loader1.create_datasource()

        # when
        loader1.load_data(nb_threads=3, create_sheet=True)
        loader2.load_data(nb_threads=4)

        # then
        computed_df = self.kawa.sheet(sheet_name=unique_id).select('date', 'int', 'record_id').compute()
        self.assertListEqual(list(computed_df['int']), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
        self.assertListEqual(list(computed_df['record_id']), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
        self.assertListEqual(list(computed_df['date']), [
            date(2024, 1, 1),
            date(2024, 1, 1),
            date(2024, 1, 1),
            date(2024, 1, 2),
            date(2024, 1, 2),
            date(2024, 1, 3),
            date(2024, 1, 3),
            date(2024, 1, 1),
            date(2024, 1, 1),
            date(2024, 1, 1),
            date(2024, 1, 2),
            date(2024, 1, 2),
            date(2024, 1, 3),
            date(2024, 1, 3)
        ])

    def test_that_data_is_properly_ingested_on_multiple_threads_without_auto_increment(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader1 = self.kawa.new_data_loader(
            df=pd.DataFrame([
                {'date': date(2024, 1, 1), 'int': 1},
                {'date': date(2024, 1, 1), 'int': 2},
                {'date': date(2024, 1, 1), 'int': 3},
                {'date': date(2024, 1, 2), 'int': 4},
                {'date': date(2024, 1, 2), 'int': 5},
                {'date': date(2024, 1, 3), 'int': 6},
                {'date': date(2024, 1, 3), 'int': 7},
            ]),
            datasource_name=unique_id)
        loader2 = self.kawa.new_data_loader(
            df=pd.DataFrame([
                {'date': date(2024, 1, 1), 'int': 8},
                {'date': date(2024, 1, 1), 'int': 9},
                {'date': date(2024, 1, 1), 'int': 10},
                {'date': date(2024, 1, 2), 'int': 11},
                {'date': date(2024, 1, 2), 'int': 12},
                {'date': date(2024, 1, 3), 'int': 13},
                {'date': date(2024, 1, 3), 'int': 14},
            ]),
            datasource_name=unique_id
        )
        loader1.create_datasource(primary_keys=['int'])

        # when
        loader1.load_data(nb_threads=3, create_sheet=True)
        loader2.load_data(nb_threads=4)

        # then
        computed_df = self.kawa.sheet(sheet_name=unique_id).select('date', 'int').compute()
        self.assertListEqual(list(computed_df['int']), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
        self.assertListEqual(list(computed_df['date']), [
            date(2024, 1, 1),
            date(2024, 1, 1),
            date(2024, 1, 1),
            date(2024, 1, 2),
            date(2024, 1, 2),
            date(2024, 1, 3),
            date(2024, 1, 3),
            date(2024, 1, 1),
            date(2024, 1, 1),
            date(2024, 1, 1),
            date(2024, 1, 2),
            date(2024, 1, 2),
            date(2024, 1, 3),
            date(2024, 1, 3)
        ])

    def test_that_computation_results_change_after_new_loads(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        dtf1 = pd.DataFrame([
            {'boolean1': True, 'text1': 'bar', 'integer1': 1},
            {'boolean1': True, 'text1': 'bar', 'integer1': 1},
            {'boolean1': True, 'text1': 'bar', 'integer1': 1},
        ])
        loader = self.kawa.new_data_loader(df=dtf1, datasource_name=unique_id)
        loader.create_datasource()

        # when: compute 1
        loader.load_data(reset_before_insert=True, create_sheet=True)
        computed_df_1 = (self.kawa
                         .sheet(sheet_name=unique_id)
                         .select('boolean1', 'text1', 'integer1', 'record_id')
                         .compute())

        # when: compute 2
        loader.load_data(reset_before_insert=False)
        time.sleep(1)
        computed_df_2 = (self.kawa
                         .sheet(sheet_name=unique_id)
                         .select('boolean1', 'text1', 'integer1', 'record_id')
                         .compute())

        # when: compute 3
        loader.load_data(reset_before_insert=False)
        time.sleep(1)
        computed_df_3 = (self.kawa
                         .sheet(sheet_name=unique_id)
                         .select('boolean1', 'text1', 'integer1', 'record_id')
                         .compute())

        # then
        self.assertEqual(computed_df_1.shape[0], 3)
        for row_id in range(3):
            self.assertTrue(computed_df_1['boolean1'][row_id])
            self.assertEqual(computed_df_1['text1'][row_id], 'bar')
            self.assertEqual(computed_df_1['integer1'][row_id], 1)
            self.assertEqual(computed_df_1['record_id'][row_id], row_id + 1)

        self.assertEqual(computed_df_2.shape[0], 6)
        for row_id in range(6):
            self.assertTrue(computed_df_2['boolean1'][row_id])
            self.assertEqual(computed_df_2['text1'][row_id], 'bar')
            self.assertEqual(computed_df_2['integer1'][row_id], 1)
            self.assertEqual(computed_df_2['record_id'][row_id], row_id + 1)

        self.assertEqual(computed_df_3.shape[0], 9)
        for row_id in range(9):
            self.assertTrue(computed_df_3['boolean1'][row_id])
            self.assertEqual(computed_df_3['text1'][row_id], 'bar')
            self.assertEqual(computed_df_3['integer1'][row_id], 1)
            self.assertEqual(computed_df_3['record_id'][row_id], row_id + 1)

    def test_that_reindexing_preserves_auto_increment_behaviour(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader = self.kawa.new_data_loader(df=pd.DataFrame([
            {'text': 'bar', 'int': 1},
            {'text': 'foo', 'int': 2},
            {'text': 'bar', 'int': 3},
        ]), datasource_name=unique_id)
        ds = loader.create_datasource()
        loader.load_data(reset_before_insert=True, create_sheet=True)
        schema_1 = self.kawa.entities.get_datasource_schema(datasource_id=ds.get('id'))

        # when: change key and compute
        self.kawa.commands.replace_datasource_primary_keys(datasource=ds,
                                                           new_primary_keys=['text', 'record_id'])
        schema_2 = self.kawa.entities.get_datasource_schema(datasource_id=ds.get('id'))

        computed_df1 = (self.kawa
                        .sheet(sheet_name=unique_id)
                        .select('text', 'record_id', 'int')
                        .compute())

        # and: feed and compute once more
        loader.load_data(reset_before_insert=False, create_sheet=False)
        loader.load_data(reset_before_insert=False, create_sheet=False)
        time.sleep(5)  # Need time for cache to clear ... this is eventually consistent
        computed_df2 = (self.kawa
                        .sheet(sheet_name=unique_id)
                        .select('text', 'record_id', 'int')
                        .compute())
        # then
        self.assertListEqual(list(computed_df1['text']), ['bar', 'foo', 'bar'])
        self.assertListEqual(list(computed_df1['int']), [1, 2, 3])
        self.assertListEqual(list(computed_df1['record_id']), [1, 2, 3])
        self.assertListEqual(list(computed_df2['record_id']), [1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertListEqual(list(computed_df2['int']), [1, 2, 3, 1, 2, 3, 1, 2, 3])
        self.assertListEqual(list(computed_df2['text']),
                             ['bar', 'foo', 'bar', 'bar', 'foo', 'bar', 'bar', 'foo', 'bar'])

        # and: check the schemas
        self.assertIn('PRIMARY KEY record_id', schema_1['schema'])
        self.assertIn('ORDER BY record_id', schema_1['schema'])
        self.assertIn('PRIMARY KEY (text, record_id)', schema_2['schema'])
        self.assertIn('ORDER BY (text, record_id)', schema_2['schema'])

    def test_that_new_indicators_are_taken_into_account(self):
        # given
        unique_id = 'resource_{}'.format(uuid.uuid4())

        # when
        loader1 = self.kawa.new_data_loader(
            df=pd.DataFrame([{'dim': 'v1'}, {'dim': 'v2'}]),
            datasource_name=unique_id)
        loader1.create_datasource()
        ds1 = loader1.load_data(create_sheet=True)
        computed_df1 = self.kawa.sheet(sheet_name=unique_id).select('dim', 'record_id').compute()

        # and
        loader2 = self.kawa.new_data_loader(
            df=pd.DataFrame([{'dim': 'v1', 'num': 1}, {'dim': 'v2', 'num': 2}]),
            datasource_name=unique_id)
        loader2.add_new_indicators_to_datasource()
        ds2 = loader2.load_data()
        computed_df2 = self.kawa.sheet(sheet_name=unique_id).select('dim', 'num', 'record_id').compute()

        # then
        self.assertListEqual(list(computed_df1['dim']), ['v1', 'v2'])
        self.assertListEqual(list(computed_df1['record_id']), [1, 2])

        # and
        self.assertListEqual(list(computed_df2['dim']), ['v1', 'v2', 'v1', 'v2'])
        self.assertListEqual(list(computed_df2['record_id']), [1, 2, 3, 4])
        self.assertTrue(math.isnan(list(computed_df2['num'])[0]))
        self.assertTrue(math.isnan(list(computed_df2['num'])[1]))
        self.assertListEqual(list(computed_df2['num'][2:]), [1.0, 2.0])

        # and
        self.assertEqual(len(ds1.get('indicators')), 2)
        self.assertEqual(len(ds2.get('indicators')), 3)

    def test_that_new_indicators_are_taken_into_account_with_existing_pk(self):
        # given
        unique_id = 'resource_{}'.format(uuid.uuid4())

        # when
        loader1 = self.kawa.new_data_loader(
            df=pd.DataFrame([
                {'k': 1, 'dim': 'v1'},
                {'k': 2, 'dim': 'v2'}]),
            datasource_name=unique_id)
        loader1.create_datasource(primary_keys=['k'])
        ds1 = loader1.load_data(create_sheet=True)
        computed_df1 = self.kawa.sheet(sheet_name=unique_id).select('dim').compute()

        # and
        loader2 = self.kawa.new_data_loader(
            df=pd.DataFrame([
                {'k': 3, 'dim': 'v1', 'num': 1},
                {'k': 4, 'dim': 'v2', 'num': 2}
            ]),
            datasource_name=unique_id)
        loader2.add_new_indicators_to_datasource()
        ds2 = loader2.load_data()
        computed_df2 = self.kawa.sheet(sheet_name=unique_id).select('dim', 'num').compute()

        # then
        self.assertListEqual(list(computed_df1['dim']), ['v1', 'v2'])

        # and
        self.assertListEqual(list(computed_df2['dim']), ['v1', 'v2', 'v1', 'v2'])
        self.assertTrue(math.isnan(list(computed_df2['num'])[0]))
        self.assertTrue(math.isnan(list(computed_df2['num'])[1]))
        self.assertListEqual(list(computed_df2['num'][2:]), [1.0, 2.0])

        # and
        self.assertEqual(len(ds1.get('indicators')), 2)
        self.assertEqual(len(ds2.get('indicators')), 3)

    def test_that_new_indicators_are_taken_into_account_when_previous_one_is_removed(self):
        # given
        unique_id = 'resource_{}'.format(uuid.uuid4())
        dtf1 = pd.DataFrame([{'dim': 'v1'}, {'dim': 'v2'}])
        dtf2 = pd.DataFrame([{'num': 1}, {'num': 2}])

        # when
        loader1 = self.kawa.new_data_loader(df=dtf1, datasource_name=unique_id)
        loader1.create_datasource()
        ds1 = loader1.load_data(create_sheet=True)
        computed_df1 = self.kawa.sheet(sheet_name=unique_id).select('dim', 'record_id').compute()

        # and
        loader2 = self.kawa.new_data_loader(df=dtf2, datasource_name=unique_id)
        loader2.add_new_indicators_to_datasource()
        ds2 = loader2.load_data()
        computed_df2 = self.kawa.sheet(sheet_name=unique_id).select('dim', 'num', 'record_id').compute()

        # then
        self.assertListEqual(list(computed_df1['dim']), ['v1', 'v2'])
        self.assertListEqual(list(computed_df1['record_id']), [1, 2])

        # and
        self.assertListEqual(list(computed_df2['dim']), ['v1', 'v2', '', ''])
        self.assertListEqual(list(computed_df2['record_id']), [1, 2, 3, 4])
        self.assertTrue(math.isnan(list(computed_df2['num'])[0]))
        self.assertTrue(math.isnan(list(computed_df2['num'])[1]))
        self.assertListEqual(list(computed_df2['num'][2:]), [1.0, 2.0])

        # and
        self.assertEqual(len(ds1.get('indicators')), 2)
        self.assertEqual(len(ds2.get('indicators')), 3)

    def test_that_an_exception_is_raised_when_loading_in_a_non_existent_datasource(self):
        # given
        dtf1 = pd.DataFrame([{'dim': 'v1'}, {'dim': 'v2'}])

        # when
        loader1 = self.kawa.new_data_loader(df=dtf1, datasource_name='non existant')
        with self.assertRaises(Exception) as context:
            loader1.load_data(create_sheet=True)

        # then
        self.assertTrue('No datasource with name' in context.exception.args[0])

    def test_that_unicity_with_record_id_is_preserved_with_duplicate_indexes(self):
        # given
        unique_id = 'resource_{}'.format(uuid.uuid4())
        dtf1 = pd.DataFrame([
            {'index': 1},
            {'index': 1},
            {'index': 1},
            {'index': 1},
            {'index': 1},
            {'index': 1},
            {'index': 1},
            {'index': 1},
            {'index': 1},
            {'index': 1},
            {'index': 1},
            {'index': 1},
        ], index=([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]))

        # when
        loader1 = self.kawa.new_data_loader(df=dtf1, datasource_name=unique_id)
        loader1.create_datasource()
        loader1.load_data(create_sheet=True, nb_threads=2)
        computed_df1 = self.kawa.sheet(sheet_name=unique_id).select('index', 'record_id').compute()

        # then
        self.assertListEqual(list(computed_df1['index']), [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        self.assertListEqual(list(computed_df1['record_id']), list(range(1, 13)))

    def test_that_unicity_with_record_id_is_preserved_with_duplicate_indexes_with_in_place(self):
        # given
        unique_id = 'resource_{}'.format(uuid.uuid4())
        dtf1 = pd.DataFrame([
            {'index': 1},
            {'index': 1},
            {'index': 1},
            {'index': 1},
            {'index': 1},
            {'index': 1},
            {'index': 1},
            {'index': 1},
            {'index': 1},
            {'index': 1},
            {'index': 1},
            {'index': 1},
        ], index=([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]))

        # when
        loader1 = self.kawa.new_data_loader(df=dtf1, datasource_name=unique_id, copy_df=False)
        loader1.create_datasource()
        loader1.load_data(create_sheet=True, nb_threads=2)
        computed_df1 = self.kawa.sheet(sheet_name=unique_id).select('index', 'record_id').compute()

        # then
        self.assertListEqual(list(computed_df1['index']), [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        self.assertListEqual(list(computed_df1['record_id']), list(range(1, 13)))

    def test_that_null_datetime_are_properly_inserted(self):
        # given
        utc = zoneinfo.ZoneInfo('UTC')
        unique_id = 'resource_{}'.format(uuid.uuid4())

        dtf1 = pd.DataFrame([
            {'id': 1, 'dt': datetime(2024, 1, 1, 0, 0, 0, tzinfo=utc)},
            {'id': 2, 'dt': None},
            {'id': 3}

        ])

        # when
        loader1 = self.kawa.new_data_loader(df=dtf1, datasource_name=unique_id)
        loader1.create_datasource()
        loader1.load_data(create_sheet=True, nb_threads=2)
        computed_df1 = self.kawa.sheet(sheet_name=unique_id).select('id', 'dt').compute()

        # then
        self.assertListEqual(list(computed_df1['id']), [1, 2, 3])
        self.assertListEqual(list(computed_df1['dt']), [
            datetime(2024, 1, 1, 0, 0, 0, tzinfo=utc),
            datetime(1970, 1, 1, 0, 0, 0, tzinfo=utc),
            datetime(1970, 1, 1, 0, 0, 0, tzinfo=utc)
        ])

    def test_that_null_date_are_properly_inserted(self):
        # given
        unique_id = 'resource_{}'.format(uuid.uuid4())
        dtf1 = pd.DataFrame([
            {'id': 1, 'dd': date(2024, 1, 1)},
            {'id': 2, 'dd': None},
            {'id': 3}

        ])

        # when
        loader1 = self.kawa.new_data_loader(df=dtf1, datasource_name=unique_id)
        loader1.create_datasource()
        loader1.load_data(create_sheet=True, nb_threads=2)
        computed_df1 = self.kawa.sheet(sheet_name=unique_id).select('id', 'dd').compute()

        # then
        self.assertListEqual(list(computed_df1['id']), [1, 2, 3])
        self.assertListEqual(list(computed_df1['dd']), [
            date(2024, 1, 1),
            date(1970, 1, 1),
            date(1970, 1, 1)
        ])


