from ...kawa_base_e2e_test import KawaBaseTest
import pandas as pd
import uuid
import tempfile
from ....client.kawa_client import KawaClient as K


class TestComputationWithTextFilters(KawaBaseTest):

    @classmethod
    def setUpClass(cls):
        unique_id = 'resource_{}'.format(uuid.uuid4())
        print(tempfile.gettempdir())
        KawaBaseTest.setUpClass()
        cls.df = cls._df_for_tests()
        cls.sheet_name = unique_id
        loader = cls.kawa.new_data_loader(df=cls.df.copy(deep=True), datasource_name=unique_id)
        loader.create_datasource()
        loader.load_data(reset_before_insert=True, create_sheet=True)

    def test_without_filters(self):
        # when
        computed_df = (self.kawa
                       .sheet(sheet_name=self.sheet_name)
                       .select('text', 'float')
                       .compute())

        # then
        self.assertListEqual(list(computed_df['text']), ['this', 'is', 'some', 'test', 'data', ''])
        self.assertListEqual(list(computed_df['float'])[:-1], [1.1, 2.2, 3.3, 4.4, 5.5])
        self.assertTrue(pd.isna(list(computed_df['float'])[-1]))

    def test_or_composition(self):
        self._check_filter(K.col('text').contains('i').contains('a'), ['this', 'is', 'data'])
        self._check_filter(K.col('float').gt(4.4).lt(2.05), ['this', 'data'])

    def test_or_and_exclude_composition(self):
        self._check_filter(K.col('text').contains('i').contains('a').exclude(), ['some', 'test', ''])

    def test_and_composition(self):
        # when
        df = (self.kawa
              .sheet(sheet_name=self.sheet_name)
              .filter(K.col('text').contains('i'))
              .filter(K.col('text').contains('h'))
              .select('text')
              .compute())

        # then
        self.assertListEqual(list(df['text']), ['this'])

    def _check_filter(self, f, expected):
        df = (self.kawa
              .sheet(sheet_name=self.sheet_name)
              .filter(f)
              .select('text')
              .compute())
        self.assertListEqual(list(df['text']), expected)

    @staticmethod
    def _df_for_tests():
        data = {
            'float': [1.1, 2.2, 3.3, 4.4, 5.5, None],
            'text': ['this', 'is', 'some', 'test', 'data', '']
        }
        return pd.DataFrame(data)
