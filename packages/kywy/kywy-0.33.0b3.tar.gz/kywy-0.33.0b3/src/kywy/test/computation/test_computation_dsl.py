import tempfile
import uuid
from datetime import date, datetime

import pandas as pd
import pandas.testing as pd_testing
import pytz

from ..kawa_base_e2e_test import KawaBaseTest
from ...client.kawa_client import KawaClient


def utc(year, month, day, hour, minute, second):
    return datetime(year, month, day, hour, minute, second, tzinfo=pytz.UTC)


class TestComputationDsl(KawaBaseTest):

    @classmethod
    def setUpClass(cls):
        unique_id = 'resource_{}'.format(uuid.uuid4())
        print(tempfile.gettempdir())
        KawaBaseTest.setUpClass()
        cls.data, cls.df = cls.df_for_tests()
        cls.sheet_name = unique_id
        loader = cls.kawa.new_data_loader(df=cls.df.copy(deep=True), datasource_name=unique_id)
        loader.create_datasource()
        loader.load_data(reset_before_insert=True, create_sheet=True)

    def test_select_all_fields(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .select('date', 'date_time', 'boolean', 'text', 'integer', 'decimal')
                       .compute())

        # then
        self.assertListEqual(list(computed_df['text']), self.data['text'][0:5])
        self.assertListEqual(list(computed_df['boolean']), self.data['boolean'][0:5])
        self.assertListEqual(list(computed_df['integer']), self.data['integer'][0:5])
        self.assertListEqual(list(computed_df['decimal']), self.data['decimal'][0:5])
        self.assertListEqual(list(computed_df['date']), self.data['date'][0:5])
        self.assertListEqual(list(computed_df['date_time']), self.data['date_time'][0:5])

    def test_select_all_fields_preserves_the_order(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .select('text', 'date', 'boolean', 'integer', 'date_time', 'decimal')
                       .compute())

        # then
        self.assertListEqual(list(computed_df.columns), ['text', 'date', 'boolean', 'integer', 'date_time', 'decimal'])

    def test_select_multiple_fields_with_regexp(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .select(KawaClient.cols(r'.*date.*'))
                       .compute())

        # then
        self.assertListEqual(list(computed_df['date']), self.data['date'][0:5])
        self.assertListEqual(list(computed_df['date_time']), self.data['date_time'][0:5])

    def test_select_indicator_fields_only(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name, force_tz='UTC')
                       .select(KawaClient.indicator_cols())
                       .compute())

        pd_testing.assert_frame_equal(computed_df.drop('record_id', axis=1).sort_index(axis=1),
                                      self.df.sort_index(axis=1),
                                      check_dtype=False)
        # then
        self.assertListEqual(list(computed_df['date']), self.data['date'][0:5])
        self.assertListEqual(list(computed_df['date_time']), self.data['date_time'][0:5])

    def test_select_all_fields_with_gt_integer_filter(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .filter(KawaClient.col('integer').gt(2))
                       .select('date', 'date_time', 'boolean', 'text', 'integer', 'decimal')
                       .compute())

        # then
        self.assertListEqual(list(computed_df['text']), self.data['text'][2:5])
        self.assertListEqual(list(computed_df['integer']), self.data['integer'][2:5])
        self.assertListEqual(list(computed_df['decimal']), self.data['decimal'][2:5])
        self.assertListEqual(list(computed_df['date']), self.data['date'][2:5])
        self.assertListEqual(list(computed_df['date_time']), self.data['date_time'][2:5])

    def test_select_all_fields_with_lt_integer_filter(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .filter(KawaClient.col('integer').lt(2))
                       .select('date', 'date_time', 'boolean', 'text', 'integer', 'decimal')
                       .compute())

        # then
        self.assertListEqual(list(computed_df['text']), self.data['text'][0:1])
        self.assertListEqual(list(computed_df['integer']), self.data['integer'][0:1])
        self.assertListEqual(list(computed_df['decimal']), self.data['decimal'][0:1])
        self.assertListEqual(list(computed_df['date']), self.data['date'][0:1])
        self.assertListEqual(list(computed_df['date_time']), self.data['date_time'][0:1])

    def test_select_all_fields_with_gte_integer_filter(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .filter(KawaClient.col('integer').gte(2))
                       .select('date', 'date_time', 'boolean', 'text', 'integer', 'decimal')
                       .compute())

        # then
        self.assertListEqual(list(computed_df['text']), self.data['text'][1:5])
        self.assertListEqual(list(computed_df['integer']), self.data['integer'][1:5])
        self.assertListEqual(list(computed_df['decimal']), self.data['decimal'][1:5])
        self.assertListEqual(list(computed_df['date']), self.data['date'][1:5])
        self.assertListEqual(list(computed_df['date_time']), self.data['date_time'][1:5])

    def test_select_all_fields_with_lte_integer_filter(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .filter(KawaClient.col('integer').lte(2))
                       .select('date', 'date_time', 'boolean', 'text', 'integer', 'decimal')
                       .compute())

        # then
        self.assertListEqual(list(computed_df['text']), self.data['text'][0:2])
        self.assertListEqual(list(computed_df['integer']), self.data['integer'][0:2])
        self.assertListEqual(list(computed_df['decimal']), self.data['decimal'][0:2])
        self.assertListEqual(list(computed_df['date']), self.data['date'][0:2])
        self.assertListEqual(list(computed_df['date_time']), self.data['date_time'][0:2])

    def test_select_all_fields_with_eq_integer_filter(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .filter(KawaClient.col('integer').eq(2))
                       .select('date', 'date_time', 'boolean', 'text', 'integer', 'decimal')
                       .compute())

        # then
        self.assertListEqual(list(computed_df['text']), self.data['text'][1:2])
        self.assertListEqual(list(computed_df['integer']), self.data['integer'][1:2])
        self.assertListEqual(list(computed_df['decimal']), self.data['decimal'][1:2])
        self.assertListEqual(list(computed_df['date']), self.data['date'][1:2])
        self.assertListEqual(list(computed_df['date_time']), self.data['date_time'][1:2])

    def test_select_all_fields_with_ne_integer_filter(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .filter(KawaClient.col('integer').ne(5))
                       .select('date', 'date_time', 'boolean', 'text', 'integer', 'decimal')
                       .compute())

        # then
        self.assertListEqual(list(computed_df['text']), self.data['text'][0:4])
        self.assertListEqual(list(computed_df['integer']), self.data['integer'][0:4])
        self.assertListEqual(list(computed_df['decimal']), self.data['decimal'][0:4])
        self.assertListEqual(list(computed_df['date']), self.data['date'][0:4])
        self.assertListEqual(list(computed_df['date_time']), self.data['date_time'][0:4])

    def test_select_all_fields_with_starts_with_filter(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .filter(KawaClient.col('text').starts_with('value1'))
                       .select('date', 'date_time', 'boolean', 'text', 'integer', 'decimal')
                       .compute())

        # then
        self.assertListEqual(list(computed_df['text']), self.data['text'][0:2])
        self.assertListEqual(list(computed_df['integer']), self.data['integer'][0:2])
        self.assertListEqual(list(computed_df['decimal']), self.data['decimal'][0:2])
        self.assertListEqual(list(computed_df['date']), self.data['date'][0:2])
        self.assertListEqual(list(computed_df['date_time']), self.data['date_time'][0:2])

    def test_select_all_fields_with_ends_with_filter(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .filter(KawaClient.col('text').ends_with('3'))
                       .select('date', 'date_time', 'boolean', 'text', 'integer', 'decimal')
                       .compute())

        # then
        self.assertListEqual(list(computed_df['text']), self.data['text'][4:5])
        self.assertListEqual(list(computed_df['integer']), self.data['integer'][4:5])
        self.assertListEqual(list(computed_df['decimal']), self.data['decimal'][4:5])
        self.assertListEqual(list(computed_df['date']), self.data['date'][4:5])
        self.assertListEqual(list(computed_df['date_time']), self.data['date_time'][4:5])

    def test_select_all_fields_with_contains_filter(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .filter(KawaClient.col('text').contains('e1'))
                       .select('date', 'date_time', 'boolean', 'text', 'integer', 'decimal')
                       .compute())

        # then
        self.assertListEqual(list(computed_df['text']), self.data['text'][0:2])
        self.assertListEqual(list(computed_df['integer']), self.data['integer'][0:2])
        self.assertListEqual(list(computed_df['decimal']), self.data['decimal'][0:2])
        self.assertListEqual(list(computed_df['date']), self.data['date'][0:2])
        self.assertListEqual(list(computed_df['date_time']), self.data['date_time'][0:2])

    def test_select_all_fields_with_does_no_contain_filter(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .filter(KawaClient.col('text').does_not_contain('e1'))
                       .select('date', 'date_time', 'boolean', 'text', 'integer', 'decimal')
                       .compute())

        # then
        self.assertListEqual(list(computed_df['text']), self.data['text'][2:5])
        self.assertListEqual(list(computed_df['integer']), self.data['integer'][2:5])
        self.assertListEqual(list(computed_df['decimal']), self.data['decimal'][2:5])
        self.assertListEqual(list(computed_df['date']), self.data['date'][2:5])
        self.assertListEqual(list(computed_df['date_time']), self.data['date_time'][2:5])

    def test_select_all_fields_with_range_filter_on_date(self):
        # when
        d = date(2023, 1, 1)
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .filter(KawaClient.col('date').date_range(from_inclusive=d, to_inclusive=d))
                       .select('date', 'date_time', 'boolean', 'text', 'integer', 'decimal')
                       .compute())

        # then
        self.assertListEqual(list(computed_df['integer']), [self.data['integer'][0], self.data['integer'][2]])
        self.assertListEqual(list(computed_df['date']), [self.data['date'][0], self.data['date'][2]])

    def test_select_all_fields_with_range_filter_on_datetime(self):
        # when
        from_dt = utc(2023, 1, 1, 23, 23, 2)
        to_dt = utc(2023, 1, 1, 23, 23, 2)
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .filter(KawaClient.col('date_time').datetime_range(from_inclusive=from_dt, to_inclusive=to_dt))
                       .select('date', 'date_time', 'boolean', 'text', 'integer', 'decimal')
                       .compute())

        # then
        self.assertListEqual(list(computed_df['integer']), [
            self.data['integer'][0],
            self.data['integer'][2],
            self.data['integer'][3],
            self.data['integer'][4]])

    def test_select_all_fields_with_in_list_filter(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .filter(KawaClient.col('text').in_list(['value11', 'value21']))
                       .select('date', 'date_time', 'boolean', 'text', 'integer', 'decimal')
                       .compute())

        # then
        self.assertListEqual(list(computed_df['integer']), [self.data['integer'][0], self.data['integer'][2]])

    def test_select_all_fields_with_open_range_filter_on_datetime(self):
        # when
        from_dt = utc(2023, 1, 1, 23, 23, 3)
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .filter(KawaClient.col('date_time').datetime_range(from_inclusive=from_dt))
                       .select('date', 'date_time', 'boolean', 'text', 'integer', 'decimal')
                       .compute())

        # then
        self.assertListEqual(list(computed_df['integer']), [self.data['integer'][1]])

    def test_aggregation_without_filters(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .group_by('date')
                       .select(KawaClient.col('integer').avg(),
                               KawaClient.col('date').first(),
                               KawaClient.col('decimal').sum())
                       .compute()).sort_values(by=['date'])

        # then
        self.assertListEqual(list(computed_df.columns), ['grouping(0)', 'integer', 'date', 'decimal'])

        self.assertListEqual(list(computed_df['grouping(0)']), [
            date(2023, 1, 1),
            date(2023, 1, 2)
        ])
        self.assertListEqual(list(computed_df['date']), [
            date(2023, 1, 1),
            date(2023, 1, 2)
        ])

        self.assertListEqual(list(computed_df['integer']), [2.0, 11.0 / 3])
        self.assertListEqual(list(computed_df['decimal']), [1.1 + 3.1, 2.1 + 4.1 + 5.1])

    def test_aggregation_without_filters_and_without_limit(self):
        # when
        computed_df = ((self.kawa
                        .sheet(sheet_name=self.sheet_name)
                        .group_by('date')
                        .agg(KawaClient.col('integer').avg(),
                             KawaClient.col('date').first(),
                             KawaClient.col('decimal').sum())
                        .no_limit()
                        .compute())
                       .sort_values(by=['date']))

        # then
        self.assertListEqual(list(computed_df.columns), ['grouping(0)', 'integer', 'date', 'decimal'])
        self.assertListEqual(list(computed_df['grouping(0)']), [date(2023, 1, 1), date(2023, 1, 2)])
        self.assertListEqual(list(computed_df['date']), [date(2023, 1, 1), date(2023, 1, 2)])
        self.assertListEqual(list(computed_df['integer']), [2.0, 11.0 / 3])
        self.assertListEqual(list(computed_df['decimal']), [1.1 + 3.1, 2.1 + 4.1 + 5.1])

    def test_with_in_list_filter(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .filter(KawaClient.col('text').in_list(['value11', 'value21']))
                       .select('text')
                       .compute())

        # then
        self.assertListEqual(list(computed_df['text']), ['value11', 'value21'])

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
