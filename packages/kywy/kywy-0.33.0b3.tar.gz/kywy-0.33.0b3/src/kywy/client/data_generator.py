import datetime

from .kawa_client import KawaClient

from .generator import Generators as g
import pandas as pd
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq


class DataGenerator:

    def __init__(self,
                 kawa_client: KawaClient,
                 sheet_and_datasource_name,
                 number_of_rows=10,
                 number_of_dimensions=5,
                 number_of_measures=5):
        """
        Initializes the data generator

        :param kawa_client: the kawa client
        :param sheet_and_datasource_name: the name of the datasource and sheet to create
        :param number_of_rows: how many rows to feed
        :param number_of_dimensions: how many extra dimensions
        :param number_of_measures: how many extra measure columns
        """
        self._k = kawa_client
        self._sheet_and_datasource_name = sheet_and_datasource_name
        self._number_of_rows = number_of_rows
        self._number_of_dimensions = number_of_dimensions
        self._number_of_measures = number_of_measures

    def generate_data(self):
        df = self._generate_df()
        data_loader = self._k.new_data_loader(df, self._sheet_and_datasource_name)
        data_loader.create_datasource(primary_keys=['f_id'])

        nb_files = max(1, int(self._number_of_rows / (100 * 1000)))
        tmp_dir = self._k.tmp_files_directory
        print("Will generate {} parquet files".format(nb_files))
        try:
            all_files = []
            for i in range(nb_files):
                filename = '{}/kawa.{}.parquet'.format(tmp_dir, i + 1)
                print('Exporting file ' + filename)
                df['f_id'] = df.index + i * self._number_of_rows
                df['f_pseudo_id_2'] = df['f_id'].map(lambda x: 'pseudo-k2-' + str(int(x / 2)))
                df['f_pseudo_id_3'] = df['f_id'].map(lambda x: 'pseudo-k3-' + str(int(x / 3)))
                df['f_pseudo_id_4'] = df['f_id'].map(lambda x: 'pseudo-k4-' + str(int(x / 4)))
                df['f_pseudo_id_5'] = df['f_id'].map(lambda x: 'pseudo-k5-' + str(int(x / 5)))
                df['f_pseudo_id_6'] = df['f_id'].map(lambda x: 'pseudo-k10-' + str(int(x / 10)))
                df['f_id'] = df['f_id'].apply(str)
                pq.write_table(pa.Table.from_pandas(df=df), filename)
                all_files.append(filename)

            nb_threads = min(20, len(all_files))
            data_loader.load_data(create_sheet=True,
                                  reset_before_insert=True,
                                  nb_threads=nb_threads,
                                  parquet_file_list=all_files)
        finally:
            for p in Path(tmp_dir).glob("kawa.*.parquet"):
                p.unlink()

    def _generate_df(self):
        data = []
        print("Generating the data")

        # The df contains at most 100,000 rows
        nb_rows_in_df = min(self._number_of_rows, 100 * 1000)

        for i in range(nb_rows_in_df):
            row = self._one_row_of_data(i)
            data.append(row)

        df = pd.DataFrame.from_records(data)

        return df

    def _one_row_of_data(self, row_id):
        number_of_dimension_columns = self._number_of_dimensions
        number_of_measure_columns = self._number_of_measures
        random_date = datetime.date(2024, 1, g.generate_random_int(1, 10))

        base = {
            # id and pseudo ids will be overridden further on
            'f_id': str(row_id),
            'f_pseudo_id_2': 'a2',
            'f_pseudo_id_3': 'a3',
            'f_pseudo_id_4': 'a4',
            'f_pseudo_id_5': 'a5',
            'f_pseudo_id_6': 'a6',

            'f_date': random_date,
            'f_text': 'text-{}'.format(g.generate_random_int(1, 10000)),
            'f_dimension_10': 'dim-{}'.format(g.generate_random_int(1, 10)),
            'f_dimension_100': 'dim-{}'.format(g.generate_random_int(1, 100)),
            'f_dimension_1000': 'dim-{}'.format(g.generate_random_int(1, 1000)),

            'system': 'text-{}'.format(g.generate_random_int(1, 5)),
            'isin': 'isin-{}'.format(row_id),
            'trading_region': 'region{}'.format(g.generate_random_int(1, 3)),
            'strategy': 'strat{}'.format(g.generate_random_int(1, 200)),
            'book': 'book{}'.format(g.generate_random_int(1, 1000)),
            'portfolio': 'ptf{}'.format(g.generate_random_int(1, 3000)),


        }

        base['netting-key-7'] = '{}+{}+{}+{}+{}+{}+{}'.format(
            base['f_date'],
            base['system'],
            base['isin'],
            base['trading_region'],
            base['strategy'],
            base['book'],
            base['portfolio'],
        )

        base['netting-key-6'] = '{}+{}+{}+{}+{}+{}'.format(
            base['f_date'],
            base['system'],
            base['isin'],
            base['trading_region'],
            base['strategy'],
            base['book']
        )

        base['netting-key-5'] = '{}+{}+{}+{}+{}'.format(
            base['f_date'],
            base['system'],
            base['isin'],
            base['trading_region'],
            base['strategy']
        )

        base['netting-key-4'] = '{}+{}+{}+{}'.format(
            base['f_date'],
            base['system'],
            base['isin'],
            base['trading_region']
        )

        for i in range(number_of_dimension_columns):
            base['dim_{}'.format(i)] = 'a-{}'.format(g.generate_random_int(1, 1000))

        for i in range(number_of_measure_columns):
            base['meas_{}'.format(i)] = g.generate_random_int(1, 1000)

        return base
