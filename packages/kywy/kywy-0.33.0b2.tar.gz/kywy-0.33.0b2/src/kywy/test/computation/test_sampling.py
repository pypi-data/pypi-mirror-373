import tempfile
import uuid
import zoneinfo
from datetime import date, datetime

import pandas as pd

from ..kawa_base_e2e_test import KawaBaseTest


def utc(year, month, day, hour, minute, second):
    return datetime(year, month, day, hour, minute, second, tzinfo=zoneinfo.ZoneInfo('UTC'))


class TestComputationSample(KawaBaseTest):

    @classmethod
    def setUpClass(cls):
        unique_id = 'resource_{}'.format(uuid.uuid4())
        print(tempfile.gettempdir())
        KawaBaseTest.setUpClass()
        cls.data, df = cls.df_for_tests()
        cls.sheet_name = unique_id
        loader = cls.kawa.new_data_loader(df=df, datasource_name=unique_id)
        loader.create_datasource()
        loader.load_data(reset_before_insert=True, create_sheet=True)

    def test_date_year_and_month_sampling(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .sample(sampler='YEAR_AND_MONTH')
                       .group_by('date')
                       .agg(self.kawa.col('decimal').sum())
                       .no_limit()
                       .compute())

        # then
        self.assertListEqual(list(computed_df['grouping(0)']), ['2023-01'])
        self.assertListEqual(list(computed_df['decimal']), [1.1 + 3.1 + 2.1 + 4.1 + 5.1])

    def test_date_year_and_quarter_sampling(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .sample(sampler='YEAR_AND_QUARTER')
                       .group_by('date')
                       .agg(self.kawa.col('decimal').sum())
                       .no_limit()
                       .compute())

        # then
        self.assertListEqual(list(computed_df['grouping(0)']), ['2023-1'])
        self.assertListEqual(list(computed_df['decimal']), [1.1 + 3.1 + 2.1 + 4.1 + 5.1])

    def test_date_year_and_semester_sampling(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .sample(sampler='YEAR_AND_SEMESTER')
                       .group_by('date')
                       .agg(self.kawa.col('decimal').sum())
                       .no_limit()
                       .compute())

        # then
        self.assertListEqual(list(computed_df['grouping(0)']), ['2023-1'])
        self.assertListEqual(list(computed_df['decimal']), [1.1 + 3.1 + 2.1 + 4.1 + 5.1])

    def test_date_day_of_year_sampling(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .sample(sampler='DAY_OF_YEAR')
                       .group_by('date')
                       .agg(self.kawa.col('decimal').sum())
                       .no_limit()
                       .compute())

        # then
        self.assertListEqual(sorted(list(computed_df['grouping(0)'])), sorted(['001', '002']))
        self.assertListEqual(sorted(list(computed_df['decimal'])), sorted([1.1 + 3.1, 2.1 + 4.1 + 5.1]))

    def test_date_year_sampling(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .sample(sampler='YEAR')
                       .group_by('date')
                       .agg(self.kawa.col('decimal').sum())
                       .no_limit()
                       .compute())

        # then
        self.assertListEqual(list(computed_df['grouping(0)']), ['2023'])
        self.assertListEqual(list(computed_df['decimal']), [1.1 + 3.1 + 2.1 + 4.1 + 5.1])

    def test_date_month_sampling(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .sample(sampler='MONTH')
                       .group_by('date')
                       .agg(self.kawa.col('decimal').sum())
                       .no_limit()
                       .compute())

        # then
        self.assertListEqual(list(computed_df['grouping(0)']), ['01'])
        self.assertListEqual(list(computed_df['decimal']), [1.1 + 3.1 + 2.1 + 4.1 + 5.1])

    def test_date_week_sampling(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .sample(sampler='WEEK')
                       .group_by('date')
                       .agg(self.kawa.col('decimal').sum())
                       .no_limit()
                       .compute())

        # then
        self.assertListEqual(list(computed_df['grouping(0)']), ['01', '52'])
        self.assertListEqual(list(computed_df['decimal']), [+ 2.1 + 4.1 + 5.1, 1.1 + 3.1])

    def test_date_time_year_sampling(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .sample(sampler='YEAR')
                       .group_by('date_time')
                       .agg(self.kawa.col('decimal').sum())
                       .no_limit()
                       .compute())

        # then
        self.assertListEqual(list(computed_df['grouping(0)']), ['2023'])
        self.assertListEqual(list(computed_df['decimal']), [1.1 + 3.1 + 2.1 + 4.1 + 5.1])

    def test_date_time_hour_sampling(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name, force_tz='UTC')
                       .sample(sampler='HOUR')
                       .group_by('date_time')
                       .agg(self.kawa.col('decimal').sum())
                       .no_limit()
                       .compute())

        # then
        self.assertListEqual(list(computed_df['grouping(0)']), [utc(2023, 1, 1, 23, 0, 0)])
        self.assertListEqual(list(computed_df['decimal']), [1.1 + 3.1 + 2.1 + 4.1 + 5.1])

    def test_date_time_fifteen_minutes_sampling(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name, force_tz='UTC')
                       .sample(sampler='FIFTEEN_MINUTES')
                       .group_by('date_time')
                       .agg(self.kawa.col('decimal').sum())
                       .no_limit()
                       .compute())

        # then
        self.assertListEqual(list(computed_df['grouping(0)']), [utc(2023, 1, 1, 23, 15, 0)])
        self.assertListEqual(list(computed_df['decimal']), [1.1 + 3.1 + 2.1 + 4.1 + 5.1])

    def test_date_time_minute_sampling(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name, force_tz='UTC')
                       .sample(sampler='MINUTE')
                       .group_by('date_time')
                       .agg(self.kawa.col('decimal').sum())
                       .no_limit()
                       .compute())

        # then
        self.assertListEqual(list(computed_df['grouping(0)']), [utc(2023, 1, 1, 23, 23, 0)])
        self.assertListEqual(list(computed_df['decimal']), [1.1 + 3.1 + 2.1 + 4.1 + 5.1])

    def test_date_time_thirty_seconds_sampling(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name, force_tz='UTC')
                       .sample(sampler='THIRTY_SECONDS')
                       .group_by('date_time')
                       .agg(self.kawa.col('decimal').sum())
                       .no_limit()
                       .compute())

        # then
        self.assertListEqual(list(computed_df['grouping(0)']), [utc(2023, 1, 1, 23, 23, 0)])
        self.assertListEqual(list(computed_df['decimal']), [1.1 + 3.1 + 2.1 + 4.1 + 5.1])

    @staticmethod
    def df_for_tests():
        data = {
            'date': [
                date(2023, 1, 1),
                date(2023, 1, 2),
                date(2023, 1, 1),
                date(2023, 1, 2),
                date(2023, 1, 2)
            ],
            'date_time': [
                utc(2023, 1, 1, 23, 23, 2),
                utc(2023, 1, 1, 23, 23, 4),
                utc(2023, 1, 1, 23, 23, 2),
                utc(2023, 1, 1, 23, 23, 2),
                utc(2023, 1, 1, 23, 23, 2),
            ],
            'text': ['value11', 'value12', 'value21', 'value22', 'value23'],
            'integer': [1, 2, 3, 4, 5],
            'decimal': [1.1, 2.1, 3.1, 4.1, 5.1],
            'boolean': [True, False, True, True, False],
        }

        data_for_df = []
        for i in range(5):
            data_for_df.append({
                'date': data['date'][i],
                'date_time': data['date_time'][i],
                'boolean': data['boolean'][i],
                'text': data['text'][i],
                'integer': data['integer'][i],
                'decimal': data['decimal'][i],
            })

        return data, pd.DataFrame(data_for_df)
