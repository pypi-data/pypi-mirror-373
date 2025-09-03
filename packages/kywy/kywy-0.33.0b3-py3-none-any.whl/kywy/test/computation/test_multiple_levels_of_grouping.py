import pandas as pd
import uuid
from datetime import datetime, time
from ...test.kawa_base_e2e_test import KawaBaseTest
from ...client.kawa_client import KawaClient as kawa
import zoneinfo


class TestComputationDslWithVariousDataSets(KawaBaseTest):
    eastern_tz = zoneinfo.ZoneInfo('US/Eastern')
    utc_tz = zoneinfo.ZoneInfo('UTC')

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
    market_data = pd.DataFrame([
        {'id': 1, 'ticker': 'AAPL', 'price': 13.3, 'time': datetime(2024, 1, 1, 13, 14, 1, tzinfo=eastern_tz)},
        {'id': 2, 'ticker': 'AAPL', 'price': 12.4, 'time': datetime(2024, 1, 1, 13, 14, 34, tzinfo=eastern_tz)},
        {'id': 3, 'ticker': 'AAPL', 'price': 12.5, 'time': datetime(2024, 1, 1, 15, 14, 5, tzinfo=eastern_tz)},
        {'id': 4, 'ticker': 'AAPL', 'price': 12.7, 'time': datetime(2024, 1, 1, 15, 15, 43, tzinfo=eastern_tz)},
        {'id': 5, 'ticker': 'MSFT', 'price': 23.3, 'time': datetime(2024, 1, 1, 13, 14, 1, tzinfo=eastern_tz)},
        {'id': 6, 'ticker': 'MSFT', 'price': 22.4, 'time': datetime(2024, 1, 1, 13, 14, 34, tzinfo=eastern_tz)},
        {'id': 7, 'ticker': 'MSFT', 'price': 22.5, 'time': datetime(2024, 1, 1, 15, 14, 5, tzinfo=eastern_tz)},
        {'id': 8, 'ticker': 'MSFT', 'price': 22.7, 'time': datetime(2024, 1, 1, 15, 15, 43, tzinfo=eastern_tz)},
    ])
    tiny_timeseries = pd.DataFrame([
        {'id': 13, 'time': datetime(2021, 1, 4, 13, 0, 0, tzinfo=eastern_tz)},
        {'id': 14, 'time': datetime(2022, 1, 3, 14, 0, 0, tzinfo=eastern_tz)},
        {'id': 15, 'time': datetime(2023, 1, 4, 15, 0, 0, tzinfo=eastern_tz)},
        {'id': 16, 'time': datetime(2024, 1, 1, 16, 0, 0, tzinfo=eastern_tz)},
    ])

    def test_group_by_1(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader = self.kawa.new_data_loader(df=self.market_data, datasource_name=unique_id)
        loader.create_datasource(primary_keys=['id'])
        loader.load_data(reset_before_insert=True, create_sheet=True)

        # when
        df = (self.kawa.sheet(sheet_name=unique_id)
              .group_by('1')
              .select(kawa.col('price').sum(), kawa.col('id').count())
              .compute())

        # then
        self.assertListEqual(list(df.columns), ['grouping(0)', 'price', 'id'])
        self.assertListEqual(list(df['grouping(0)']), ['1'])
        self.assertListEqual(list(df['price']), [13.3 + 12.4 + 12.5 + 12.7 + 23.3 + 22.4 + 22.5 + 22.7])
        self.assertListEqual(list(df['id']), [8])

    def test_time_range_filters(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader = self.kawa.new_data_loader(df=self.tiny_timeseries, datasource_name=unique_id)
        loader.create_datasource(primary_keys=['id'])
        loader.load_data(reset_before_insert=True, create_sheet=True)

        # when
        def compute(tz_id,
                    from_inclusive=None,
                    from_exclusive=None,
                    to_inclusive=None,
                    to_exclusive=None):
            time_filter = kawa.col('time').time_range(from_inclusive=from_inclusive,
                                                      from_exclusive=from_exclusive,
                                                      to_inclusive=to_inclusive,
                                                      to_exclusive=to_exclusive)
            return list((self.kawa
                         .sheet(sheet_name=unique_id, force_tz=tz_id)
                         .select('id')
                         .filter(time_filter)
                         .compute())['id'])

        # then
        # Data contains
        # 13:00, 14:00, 15:00, 16:00 in eastern time
        # Which translates to
        # 18:00, 19:00, 20:00, 21:00 in UTC

        # ----------------
        # US/Eastern computations
        # ----------------
        self.assertListEqual(
            compute(
                tz_id='US/Eastern',
                from_inclusive=time(hour=15, minute=0, second=0)
            ), [15, 16])

        self.assertListEqual(
            compute(
                tz_id='US/Eastern',
                from_exclusive=time(hour=15, minute=0, second=0)
            ), [16])

        self.assertListEqual(
            compute(
                tz_id='US/Eastern',
                to_inclusive=time(hour=15, minute=0, second=0)
            ), [13, 14, 15])

        self.assertListEqual(
            compute(
                tz_id='US/Eastern',
                to_exclusive=time(hour=15, minute=0, second=0)
            ), [13, 14])

        self.assertListEqual(
            compute(
                tz_id='US/Eastern',
                from_exclusive=time(hour=13, minute=0, second=0),
                to_exclusive=time(hour=15, minute=0, second=0),
            ), [14])

        self.assertListEqual(
            compute(
                tz_id='US/Eastern',
                from_inclusive=time(hour=13, minute=0, second=0),
                to_exclusive=time(hour=15, minute=0, second=0),
            ), [13, 14])

        self.assertListEqual(
            compute(
                tz_id='US/Eastern',
                from_exclusive=time(hour=13, minute=0, second=0),
                to_inclusive=time(hour=15, minute=0, second=0),
            ), [14, 15])

        self.assertListEqual(
            compute(
                tz_id='US/Eastern',
                from_inclusive=time(hour=15, minute=0, second=0),
                to_inclusive=time(hour=15, minute=0, second=0),
            ), [15])

        self.assertListEqual(
            compute(
                tz_id='US/Eastern',
                from_exclusive=time(hour=15, minute=0, second=0),
                to_inclusive=time(hour=15, minute=0, second=0),
            ), [])

        # ----------------
        # UTC computations
        # ----------------
        self.assertListEqual(
            compute(
                tz_id='UTC',
                # Equivalent of 15:00 Eastern
                from_inclusive=time(hour=20, minute=0, second=0)
            ), [15, 16])

        self.assertListEqual(
            compute(
                tz_id='UTC',
                # Equivalent of 15:00 Eastern
                from_exclusive=time(hour=20, minute=0, second=0)
            ), [16])

        self.assertListEqual(
            compute(
                tz_id='UTC',
                # Equivalent of 15:00 Eastern
                to_inclusive=time(hour=20, minute=0, second=0)
            ), [13, 14, 15])

        self.assertListEqual(
            compute(
                tz_id='UTC',
                # Equivalent of 15:00 Eastern
                to_exclusive=time(hour=20, minute=0, second=0)
            ), [13, 14])

    def test_that_computation_works_with_two_levels_of_grouping_and_datetime_up_sampling(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader = self.kawa.new_data_loader(df=self.market_data, datasource_name=unique_id)
        loader.create_datasource(primary_keys=['id'])
        loader.load_data(
            reset_before_insert=True,
            create_sheet=True)

        # when
        df = (self.kawa.sheet(sheet_name=unique_id)
              .sample(column_name='time', sampler='FIFTEEN_MINUTES')
              .group_by('time', 'ticker')
              .agg(kawa.col('price').sum())
              .compute())

        # then
        self.assertListEqual(list(df.columns), ['grouping(0)', 'grouping(1)', 'price'])
        self.assertListEqual(list(df['price']), [
            13.3 + 12.4, 23.3 + 22.4,
            12.5, 22.5,
            12.7, 22.7,
        ])
        actual_ts = [ts.timestamp() for ts in df['grouping(0)']]
        expected_ts = [
            datetime(2024, 1, 1, 13, 0, 0, tzinfo=self.eastern_tz).timestamp(),
            datetime(2024, 1, 1, 13, 0, 0, tzinfo=self.eastern_tz).timestamp(),
            datetime(2024, 1, 1, 15, 0, 0, tzinfo=self.eastern_tz).timestamp(),
            datetime(2024, 1, 1, 15, 0, 0, tzinfo=self.eastern_tz).timestamp(),
            datetime(2024, 1, 1, 15, 15, 0, tzinfo=self.eastern_tz).timestamp(),
            datetime(2024, 1, 1, 15, 15, 0, tzinfo=self.eastern_tz).timestamp(),
        ]
        self.assertListEqual(actual_ts, expected_ts)
        self.assertListEqual(list(df['grouping(1)']), ['AAPL', 'MSFT', 'AAPL', 'MSFT', 'AAPL', 'MSFT'])

    def test_that_computation_works_with_two_levels_of_grouping(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader = self.kawa.new_data_loader(df=self.cities_and_countries, datasource_name=unique_id)
        loader.create_datasource(primary_keys=['id'])
        loader.load_data(reset_before_insert=True, create_sheet=True)

        # when
        df = (self.kawa.sheet(sheet_name=unique_id)
              .group_by('country', 'city')
              .agg(kawa.col('measure').sum())
              .compute())

        # then
        self.assertListEqual(list(df.columns), ['grouping(0)', 'grouping(1)', 'measure'])
        self.assertListEqual(list(df['grouping(0)']), [
            'BE', 'BE', 'BE',
            'FR', 'FR', 'FR',
            'UK', 'UK', 'UK', 'UK'])
        self.assertListEqual(list(df['grouping(1)']), [
            'Bruges', 'Brussels', 'Namur',
            'Lille', 'Lyon', 'Paris',
            'Belfast', 'Cardiff', 'Edinburgh', 'London'
        ])

    def test_that_computation_works_with_two_levels_of_grouping_keeping_group_names(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader = self.kawa.new_data_loader(df=self.cities_and_countries, datasource_name=unique_id)
        loader.create_datasource(primary_keys=['id'])
        loader.load_data(reset_before_insert=True, create_sheet=True)

        # when
        df = (self.kawa.sheet(sheet_name=unique_id)
              .group_by('country', 'city')
              .agg(kawa.col('measure').sum())
              .compute(use_group_names=True))

        # then
        self.assertListEqual(list(df.columns), ['group(0) country', 'group(1) city', 'measure'])
        self.assertListEqual(list(df['group(0) country']), [
            'BE', 'BE', 'BE',
            'FR', 'FR', 'FR',
            'UK', 'UK', 'UK', 'UK'])
        self.assertListEqual(list(df['group(1) city']), [
            'Bruges', 'Brussels', 'Namur',
            'Lille', 'Lyon', 'Paris',
            'Belfast', 'Cardiff', 'Edinburgh', 'London'
        ])
