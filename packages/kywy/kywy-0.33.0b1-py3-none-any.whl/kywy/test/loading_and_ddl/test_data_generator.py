from ...client.data_generator import DataGenerator
from datetime import date
import uuid
import numpy

from ..kawa_base_e2e_test import KawaBaseTest


class TestDataGenerator(KawaBaseTest):

    def test_that_data_is_properly_generated(self):
        # setup
        sheet_name = 'generated_' + str(uuid.uuid4())
        generator = DataGenerator(
            kawa_client=self.kawa,
            sheet_and_datasource_name=sheet_name,
            number_of_rows=10,
            number_of_measures=1,
            number_of_dimensions=1
        )

        # when
        generator.generate_data()

        # then
        computed_df = (self.kawa
                       .sheet(sheet_name=sheet_name)
                       .select(self.kawa.cols())
                       .compute())

        self.assertEqual(computed_df.shape[0], 10)
        self.assertGreaterEqual(computed_df.shape[1], 13)

        self.assertListEqual(list(computed_df['f_id']), ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])

        self.assertTrue(type(computed_df['f_id'][0]) is str)
        self.assertTrue(type(computed_df['dim_0'][0]) is str)
        self.assertTrue(type(computed_df['f_dimension_10'][0]) is str)
        self.assertTrue(type(computed_df['f_dimension_100'][0]) is str)
        self.assertTrue(type(computed_df['f_dimension_1000'][0]) is str)
        self.assertTrue(type(computed_df['f_pseudo_id_2'][0]) is str)
        self.assertTrue(type(computed_df['f_pseudo_id_3'][0]) is str)
        self.assertTrue(type(computed_df['f_pseudo_id_4'][0]) is str)
        self.assertTrue(type(computed_df['f_pseudo_id_5'][0]) is str)
        self.assertTrue(type(computed_df['f_pseudo_id_6'][0]) is str)
        self.assertTrue(type(computed_df['f_text'][0]) is str)
        self.assertTrue(type(computed_df['f_date'][0]) is date)
        self.assertTrue(type(computed_df['meas_0'][0]) is numpy.int64)
