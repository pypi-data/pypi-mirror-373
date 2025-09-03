import pandas as pd
import uuid
from datetime import datetime, time, timedelta
from ...kawa_base_e2e_test import KawaBaseTest
from ....client.kawa_client import KawaClient as kawa
import zoneinfo


class TestComputationDslWithVariousDataSets(KawaBaseTest):

    def test_date_time_filters(self):
        # setup
        eastern_tz = zoneinfo.ZoneInfo('US/Eastern')
        tiny_timeseries = pd.DataFrame([
            {'id': 13, 'time': datetime(2021, 1, 4, 13, 0, 0, tzinfo=eastern_tz)},
            {'id': 14, 'time': datetime(2021, 1, 4, 14, 0, 0, tzinfo=eastern_tz)},
            {'id': 15, 'time': datetime(2021, 1, 4, 15, 0, 0, tzinfo=eastern_tz)},
            {'id': 16, 'time': datetime(2021, 1, 4, 16, 0, 0, tzinfo=eastern_tz)},
        ])

        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader = self.kawa.new_data_loader(df=tiny_timeseries, datasource_name=unique_id)
        loader.create_datasource(primary_keys=['id'])
        loader.load_data(reset_before_insert=True, create_sheet=True)

        # given
        def compute(tz_id, from_inclusive=None, to_inclusive=None):
            time_filter = (kawa
                           .col('time')
                           .datetime_range(from_inclusive=from_inclusive,
                                           to_inclusive=to_inclusive))
            return list((self.kawa
                         .sheet(sheet_name=unique_id, force_tz=tz_id)
                         .select('id')
                         .filter(time_filter)
                         .compute())['id'])

        # expect
        self.assertListEqual(
            compute(
                tz_id='US/Eastern',
                from_inclusive=datetime(2021, 1, 4, 15, 0, 0, tzinfo=eastern_tz)
            ), [15, 16])
        self.assertListEqual(
            compute(
                tz_id='US/Eastern',
                to_inclusive=datetime(2021, 1, 4, 15, 0, 0, tzinfo=eastern_tz)
            ), [13, 14, 15])
        self.assertListEqual(
            compute(
                tz_id='UTC',
                to_inclusive=datetime(2021, 1, 4, 15, 0, 0, tzinfo=eastern_tz)
            ), [13, 14, 15])

    def test_date_time_filters_with_milliseconds(self):
        # setup
        eastern_tz = zoneinfo.ZoneInfo('US/Eastern')
        tiny_timeseries = pd.DataFrame([
            {'id': 1, 'time': datetime(2021, 1, 1, 0, 0, 0, tzinfo=eastern_tz)},
            {'id': 2, 'time': datetime(2021, 1, 1, 0, 0, 0, tzinfo=eastern_tz) + timedelta(milliseconds=250)},
            {'id': 3, 'time': datetime(2021, 1, 1, 0, 0, 0, tzinfo=eastern_tz) + timedelta(milliseconds=500)},
            {'id': 4, 'time': datetime(2021, 1, 1, 0, 0, 0, tzinfo=eastern_tz) + timedelta(milliseconds=750)},
            {'id': 5, 'time': datetime(2021, 1, 1, 0, 0, 1, tzinfo=eastern_tz)},
        ])

        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader = self.kawa.new_data_loader(df=tiny_timeseries, datasource_name=unique_id)
        loader.create_datasource(primary_keys=['id'])
        loader.load_data(reset_before_insert=True, create_sheet=True)

        # given
        def compute(tz_id, from_inclusive=None, to_inclusive=None):
            time_filter = (kawa
                           .col('time')
                           .datetime_range(from_inclusive=from_inclusive,
                                           to_inclusive=to_inclusive))
            return list((self.kawa
                         .sheet(sheet_name=unique_id, force_tz=tz_id)
                         .select('id')
                         .filter(time_filter)
                         .compute())['id'])

        # expect
        self.assertListEqual(
            compute(
                tz_id='US/Eastern',
                from_inclusive=datetime(2021, 1, 1, 0, 0, 0, tzinfo=eastern_tz) + timedelta(milliseconds=250)
            ), [2, 3, 4, 5])
        self.assertListEqual(
            compute(
                tz_id='US/Eastern',
                to_inclusive=datetime(2021, 1, 1, 0, 0, 0, tzinfo=eastern_tz) + timedelta(milliseconds=500)
            ), [1, 2, 3])

    def test_time_range_filters(self):
        # setup
        eastern_tz = zoneinfo.ZoneInfo('US/Eastern')
        tiny_timeseries = pd.DataFrame([
            {'id': 13, 'time': datetime(2021, 1, 4, 13, 0, 0, tzinfo=eastern_tz)},
            {'id': 14, 'time': datetime(2022, 1, 3, 14, 0, 0, tzinfo=eastern_tz)},
            {'id': 15, 'time': datetime(2023, 1, 4, 15, 0, 0, tzinfo=eastern_tz)},
            {'id': 16, 'time': datetime(2024, 1, 1, 16, 0, 0, tzinfo=eastern_tz)},
        ])

        unique_id = 'resource_{}'.format(uuid.uuid4())
        loader = self.kawa.new_data_loader(df=tiny_timeseries, datasource_name=unique_id)
        loader.create_datasource(primary_keys=['id'])
        loader.load_data(reset_before_insert=True, create_sheet=True)

        # given
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

        # expect
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
