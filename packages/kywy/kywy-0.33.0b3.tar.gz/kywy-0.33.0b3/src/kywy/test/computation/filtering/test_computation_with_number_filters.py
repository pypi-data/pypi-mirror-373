from ...kawa_base_e2e_test import KawaBaseTest
import pandas as pd
import uuid
import tempfile
from ....client.kawa_client import KawaClient as K


class TestComputationWithNumericFilters(KawaBaseTest):

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
                       .select('integer')
                       .compute())

        # then
        self.assertListEqual(list(computed_df['integer']), [1, 2, 3, 4, 5])

    def test_gt_filter(self):
        self._apply_and_check_filter(K.col('integer').gt(4), [5])
        self._apply_and_check_filter(K.col('integer').gt(4.1), [5])
        self._apply_and_check_filter(K.col('integer').gt(1), [2, 3, 4, 5])
        self._apply_and_check_filter(K.col('integer').gt(-11), [1, 2, 3, 4, 5])
        self._apply_and_check_filter(K.col('integer').gt(11), [])

    def test_gte_filter(self):
        self._apply_and_check_filter(K.col('integer').gte(4), [4, 5])
        self._apply_and_check_filter(K.col('integer').gte(4.1), [5])
        self._apply_and_check_filter(K.col('integer').gte(2), [2, 3, 4, 5])
        self._apply_and_check_filter(K.col('integer').gte(-2), [1, 2, 3, 4, 5])
        self._apply_and_check_filter(K.col('integer').gte(29), [])

    def test_lt_filter(self):
        self._apply_and_check_filter(K.col('integer').lt(4), [1, 2, 3])
        self._apply_and_check_filter(K.col('integer').lt(3.9), [1, 2, 3])
        self._apply_and_check_filter(K.col('integer').lt(2), [1])
        self._apply_and_check_filter(K.col('integer').lt(-11), [])
        self._apply_and_check_filter(K.col('integer').lt(11), [1, 2, 3, 4, 5])

    def test_lte_filter(self):
        self._apply_and_check_filter(K.col('integer').lte(4), [1, 2, 3, 4])
        self._apply_and_check_filter(K.col('integer').lte(3.9), [1, 2, 3])
        self._apply_and_check_filter(K.col('integer').lte(2), [1, 2])
        self._apply_and_check_filter(K.col('integer').lte(-11), [])
        self._apply_and_check_filter(K.col('integer').lte(11), [1, 2, 3, 4, 5])

    def test_eq_filter(self):
        self._apply_and_check_filter(K.col('integer').eq(4), [4])
        self._apply_and_check_filter(K.col('integer').eq(3.9), [])
        self._apply_and_check_filter(K.col('integer').eq(2), [2])
        self._apply_and_check_filter(K.col('integer').eq(-11), [])
        self._apply_and_check_filter(K.col('integer').eq(11), [])

    def test_ne_filter(self):
        self._apply_and_check_filter(K.col('integer').ne(4), [1, 2, 3, 5])
        self._apply_and_check_filter(K.col('integer').ne(3.9), [1, 2, 3, 4, 5])
        self._apply_and_check_filter(K.col('integer').ne(2), [1, 3, 4, 5])
        self._apply_and_check_filter(K.col('integer').ne(-11), [1, 2, 3, 4, 5])
        self._apply_and_check_filter(K.col('integer').ne(11), [1, 2, 3, 4, 5])

    def _apply_and_check_filter(self, f, expected):
        df = (self.kawa
              .sheet(sheet_name=self.sheet_name)
              .filter(f)
              .select('integer')
              .compute())
        self.assertListEqual(list(df['integer']), expected)

    @staticmethod
    def _df_for_tests():
        data = {
            'text': ['c1', 'c1', 'c1', 'c2', 'c2'],
            'integer': [1, 2, 3, 4, 5],
        }
        return pd.DataFrame(data)
