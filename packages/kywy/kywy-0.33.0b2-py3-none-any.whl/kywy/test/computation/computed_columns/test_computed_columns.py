import tempfile
import uuid
from datetime import date, datetime

import pandas as pd
import pytz

from ...kawa_base_e2e_test import KawaBaseTest
from ....client.computation_nodes import add, val, col
from ....client.layout_builder import KawaGridBuilder


def utc(year, month, day, hour, minute, second):
    return datetime(year, month, day, hour, minute, second, tzinfo=pytz.UTC)


class TestComputedColumns(KawaBaseTest):

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

    def test_select_computed_column(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .select(add(val(5), col('integer')).alias('5 plus integer column'))
                       .compute())

        # then
        self.assertListEqual(list(computed_df['5 plus integer column']), [i + 5 for i in self.data['integer']])

    def test_select_computed_column_with_sheet_name_absent(self):
        # setup
        sheet = self.kawa.entities.sheets().get_entity(self.sheet_name)
        view_id = KawaGridBuilder(self.kawa, sheet.get('id'), 'Grid').initialize().finalize()

        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=None)
                       .view_id(view_id=view_id)
                       .select(col('integer'))
                       .compute())

        # then
        self.assertListEqual(list(computed_df['integer']), self.data['integer'])

    def test_select_formula_without_aliases(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .select(add(val(5), col('integer')))
                       .compute())

        # then
        self.assertListEqual(list(computed_df['col0']), [i + 5 for i in self.data['integer']])

    def test_select_formula_and_columns(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .select(add(val(1), val(2)).alias('1 plus 2'), 'text')
                       .compute())

        # then
        self.assertListEqual(list(computed_df.columns), ['1 plus 2', 'text'])

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
