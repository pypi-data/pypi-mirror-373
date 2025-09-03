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
                       .select('text')
                       .compute())

        # then
        self.assertListEqual(list(computed_df['text']), ['this', 'is', 'some', 'test', 'data', ''])

    def test_contains_filter(self):
        self._check_filter(K.col('text').contains('i'), ['this', 'is'])
        self._check_filter(K.col('text').contains('data'), ['data'])
        self._check_filter(K.col('text').contains('foo'), [])
        self._check_filter(K.col('text').contains(''), ['this', 'is', 'some', 'test', 'data', ''])

    def test_does_not_contain_filter(self):
        self._check_filter(K.col('text').does_not_contain('i'), ['some', 'test', 'data', ''])
        self._check_filter(K.col('text').does_not_contain('data'), ['this', 'is', 'some', 'test', ''])
        self._check_filter(K.col('text').does_not_contain('foo'), ['this', 'is', 'some', 'test', 'data', ''])
        self._check_filter(K.col('text').does_not_contain(''), [])

    def test_starts_with(self):
        self._check_filter(K.col('text').starts_with('is'), ['is'])
        self._check_filter(K.col('text').starts_with('data'), ['data'])
        self._check_filter(K.col('text').starts_with('foo'), [])
        self._check_filter(K.col('text').starts_with(''), ['this', 'is', 'some', 'test', 'data', ''])

    def test_does_not_start_with(self):
        self._check_filter(K.col('text').does_not_start_with('is'), ['this', 'some', 'test', 'data', ''])
        self._check_filter(K.col('text').does_not_start_with('data'), ['this', 'is', 'some', 'test', ''])
        self._check_filter(K.col('text').does_not_start_with('foo'),
                           ['this', 'is', 'some', 'test', 'data', ''])
        self._check_filter(K.col('text').does_not_start_with(''), [])

    def test_ends_with(self):
        self._check_filter(K.col('text').ends_with('s'), ['this', 'is'])
        self._check_filter(K.col('text').ends_with('is'), ['this', 'is'])
        self._check_filter(K.col('text').ends_with('his'), ['this'])
        self._check_filter(K.col('text').ends_with('data'), ['data'])
        self._check_filter(K.col('text').ends_with('foo'), [])
        self._check_filter(K.col('text').ends_with(''), ['this', 'is', 'some', 'test', 'data', ''])

    def test_does_not_end_with(self):
        self._check_filter(K.col('text').does_not_end_with('s'), ['some', 'test', 'data', ''])
        self._check_filter(K.col('text').does_not_end_with('is'), ['some', 'test', 'data', ''])
        self._check_filter(K.col('text').does_not_end_with('his'), ['is', 'some', 'test', 'data', ''])
        self._check_filter(K.col('text').does_not_end_with('data'), ['this', 'is', 'some', 'test', ''])
        self._check_filter(K.col('text').does_not_end_with('foo'), ['this', 'is', 'some', 'test', 'data', ''])
        self._check_filter(K.col('text').does_not_end_with(''), [])

    def test_empty(self):
        self._check_filter(K.col('text').empty(), [''])

    def test_not_empty(self):
        self._check_filter(K.col('text').not_empty(), ['this', 'is', 'some', 'test', 'data'])

    def test_in_list(self):
        self._check_filter(K.col('text').in_list(['this', 'is', 'foo']), ['this', 'is'])
        self._check_filter(K.col('text').in_list(['this', 'is', '']), ['this', 'is', ''])
        self._check_filter(K.col('text').in_list(['foo']), [])
        self._check_filter(K.col('text').in_list(['']), [''])

    def test_in_list_with_tuple(self):
        self._check_filter(K.col('text').in_list('this', 'is', 'foo'), ['this', 'is'])
        self._check_filter(K.col('text').in_list('this', 'is', ''), ['this', 'is', ''])
        self._check_filter(K.col('text').in_list('foo'), [])
        self._check_filter(K.col('text').in_list(''), [''])

    def test_not_in_list(self):
        self._check_filter(K.col('text').in_list(['this', 'is']).exclude(), ['some', 'test', 'data', ''])
        self._check_filter(K.col('text').in_list(['foo']).exclude(), ['this', 'is', 'some', 'test', 'data', ''])

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
            'text': ['this', 'is', 'some', 'test', 'data', '']
        }
        return pd.DataFrame(data)
