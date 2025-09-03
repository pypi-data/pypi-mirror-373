import glob
import os.path
import re
import shutil
import time
import traceback
import uuid
from datetime import date
import pyarrow as pa
import pyarrow.types as types
import pyarrow.compute as pc
import pyarrow.ipc as ipc
import pandas as pd
import concurrent.futures
import io
import numpy
import socket
import platform
from slugify import slugify
import numpy as np


class KawaDataLoader:

    def __init__(self,
                 kawa_client,
                 df,
                 datasource_name=None,
                 datasource_is_shared=False,
                 datasource_id=None,
                 copy_df=True,
                 arrow_table=None,
                 arrow_schema=None,
                 strict_mode=False
                 ):
        if datasource_id is None and datasource_name is None:
            raise Exception('To build a KawaDataLoader you need either a datasource_name or a datasource_id')

        self._k = kawa_client
        self._shared = datasource_is_shared
        self._name = '' if datasource_name is None else datasource_name.strip()
        self._datasource_id = datasource_id
        self._strict_mode = strict_mode

        # Check arrow schema consistency
        if arrow_schema is not None and arrow_table is not None:
            if not arrow_schema.equals(arrow_table.schema):
                raise Exception('The schema of the arrow_table does not match the arrow_schema')

        # Mode 1: The pandas dataframe is defined
        if df is not None:
            if strict_mode:
                raise Exception('Strict mode is only supported with Arrow tables, not with pandas')
            self._use_arrow = False
            self._df = df.copy() if copy_df else df

        # Mode 2: The arrow table is there (We will prioritize the use of the provided schema)
        elif arrow_table is not None:
            self._use_arrow = True
            self._arrow_schema = arrow_schema if arrow_schema else arrow_table.schema
            self._arrow_table = arrow_table

        # Mode 3: Only an arrow schema is here. We can do everything except load data
        elif arrow_schema is not None:
            self._use_arrow = True
            self._arrow_schema = arrow_schema
            self._arrow_table = None

        else:
            raise Exception('To build a KawaDataLoader you need either a pandas dataframe, '
                            'an arrow table or an arrow schema')

    def create_datasource(self, primary_keys=None):
        """
        If the datasource with name == datasource_name does not exist in the current
        workspace, create it.
        This command is idempotent.
        Once the datasource exists, it will have no effect at all.

        The indicators of the datasource will be deduced from the columns of the dataframe.

        :param: primary_keys:
        Defines the list of columns that will be considered as primary key.
        If left empty, KAWA will generate a record_id which will act as an auto increment primary key.

        IMPORTANT: Those primary keys will be imported in the same order as they appear in the dataframe.

        :return: The created or existing datasource
        """
        if self._datasource_id:
            raise Exception('Cannot create data source when data source id has been provided')
        existing_datasource = self._k.entities.datasources().get_entity(entity_id_or_name=self._name)
        if existing_datasource:
            # Idempotent
            return existing_datasource
        else:
            ds = self._define_data_source_from_df(primary_keys=primary_keys)
            return self._k.commands.create_datasource(datasource=ds)

    def add_new_indicators_to_datasource(self):
        """
        Adds to the existing datasource (identified by its name) all the columns of the dataframe that
        were not already there.
        This command will only add new indicators to the datasource and will have no other effect.

        :raises: Exception is raised if the datasource does not exist in the current workspace
        :return: The updated datasource
        """
        existing_datasource = self._get_data_source_or_raise()

        existing_indicator_id = []
        existing_primary_keys = []

        for indicator in existing_datasource.get('indicators', []):
            indicator_id = indicator.get('indicatorId')
            existing_indicator_id.append(indicator_id)
            key = indicator.get('key', {})
            key_type = key.get('keyType', '')
            if 'PRIMARY' in key_type:
                existing_primary_keys.append(indicator_id)

        # No new primary key here because we only look for new indicators
        # And BE does not support adding PK via the add_indicators_to_datasource command.
        new_datasource_from_df = self._define_data_source_from_df(existing_primary_keys)

        new_indicators = []
        for new_indicator in new_datasource_from_df.get('indicators', []):
            new_indicator_id = new_indicator.get('indicatorId')
            if new_indicator_id not in existing_indicator_id:
                new_indicators.append(new_indicator)

        if new_indicators:
            print('Adding the following indicators: {}'.format([i.get('indicatorId') for i in new_indicators]))
            return self._k.commands.add_indicators_to_datasource(
                datasource=existing_datasource,
                new_indicators=new_indicators)
        else:
            print('No new indicator to add')
            return existing_datasource

    def load_data(self,
                  reset_before_insert=False,
                  create_sheet=False,
                  optimize_after_insert=False,
                  nb_threads=1,
                  parquet_file_list=None,
                  job_id=None):

        if self._strict_mode:
            self._enforce_strict_schema_validation()

        datasource = self._load_data(optimize_after_insert=optimize_after_insert,
                                     reset_data=reset_before_insert,
                                     nb_threads=nb_threads,
                                     parquet_file_list=parquet_file_list,
                                     session_id_input=job_id)
        if create_sheet:
            self._k.commands.create_sheet(datasource=datasource,
                                          sheet_name=self._name)

        return datasource

    def _enforce_strict_schema_validation(self):
        datasource = self._get_data_source_or_raise()
        indicators_in_datasource = [(i['indicatorId'], i['type']) for i in datasource['indicators'] if
                                    i['indicatorId'] != 'record_id']

        arrow_schema = self._arrow_schema
        indicators = [self._define_indicator(c, False) for c in arrow_schema.names]
        indicators_in_arrow_table = [(i['indicatorId'], i['type']) for i in indicators]

        # Look for missing indicators in the data source
        for indicator in indicators_in_datasource:
            if indicator not in indicators_in_arrow_table:
                indicator_name = indicator[0]
                indicator_type = indicator[1]
                raise Exception(
                    f'Arrow table is invalid. Indicator {indicator_name} with type {indicator_type} is missing')

        # Look for missing indicators in the arrow table
        for indicator in indicators_in_arrow_table:
            if indicator not in indicators_in_datasource:
                indicator_name = indicator[0]
                indicator_type = indicator[1]
                msg = (f'Arrow table is invalid. Indicator {indicator_name} with type {indicator_type} '
                       f'is missing in datasource')
                raise Exception(msg)

    def _introspect_df(self):
        column_kawa_types = {}
        column_names = self._arrow_schema.names if self._use_arrow else self._df.columns
        for column_name in column_names:
            kawa_type = self._extract_kawa_type(column_name)
            column_kawa_types[column_name] = kawa_type

        return column_kawa_types

    def _define_data_source_from_df(self, primary_keys=None):

        defined_pks = primary_keys if primary_keys else []

        if self._use_arrow:
            indicators = [self._define_indicator(c, c in defined_pks) for c in self._arrow_schema.names]
        else:
            indicators = [self._define_indicator(c, c in defined_pks) for c in self._df.columns]

        # Add the auto increment key if there is no specified key
        key_indicators = [i for i in indicators if 'key' in i]
        if not key_indicators:
            indicators.insert(0, {
                'displayInformation': {
                    'displayName': 'record_id'
                },
                'includedInDefaultLayout': False,
                'indicatorId': 'record_id',
                'storageConfig': {
                    'indexed': True,
                    'automaticUniqueValue': True
                },
                'type': 'integer',
                'key': {
                    'keyType': 'PRIMARY_SHARDING_KEY'
                }
            })

        return {
            'shared': self._shared,
            'displayInformation': {
                'displayName': self._name
            },
            'storageConfiguration': {
                'loadingAdapterName': 'CLICKHOUSE'
            },
            'indicators': indicators,
        }

    def _define_indicator(self, column_name, is_primary_key=False):
        indicator = {
            'displayInformation': {
                'displayName': column_name
            },
            'includedInDefaultLayout': True,
            'indicatorId': column_name,
            'storageConfig': {
                'indexed': is_primary_key
            },
            'type': self._extract_kawa_type(column_name)
        }
        if is_primary_key:
            indicator['key'] = {'keyType': 'PRIMARY_SHARDING_KEY'}

        return indicator

    def _extract_kawa_type(self, column_name):
        if self._use_arrow:
            kawa_type = self._extract_kawa_type_from_arrow_schema(column_name)
        else:
            kawa_type = self._extract_kawa_type_from_pandas_df(column_name)
        return kawa_type

    def _extract_kawa_type_from_arrow_schema(self, column_name):
        col_type = self._arrow_schema.field(column_name).type

        # Unsupported types
        if types.is_date64(col_type):
            raise Exception(f'Type date64 is not supported for column {column_name}. Please use date32 instead')
        if types.is_float16(col_type):
            raise Exception(f'Type float16 is not supported for column {column_name}. Please use float32 instead')

        # Supported types
        if types.is_integer(col_type):
            return 'integer'
        elif types.is_floating(col_type) or types.is_decimal(col_type):
            return 'decimal'
        elif types.is_string(col_type):
            return 'text'
        elif types.is_date(col_type):
            return 'date'
        elif types.is_boolean(col_type):
            return 'boolean'
        elif types.is_timestamp(col_type):
            return 'date_time'
        else:
            # Throws if type is not covered.
            raise Exception(f'Arrow type {col_type} is not supported for column {column_name}')

    def _extract_kawa_type_from_pandas_df(self, column_name):
        """
        This method is not ideal and should be avoided.
        For example, strings have an 'object' type in pandas and values need to be introspected to find the real type
        If an arrow schema is passed to the loader, the KAWA schema will be deduced from it instead.

        :param column_name: The column to extract the kawa type from
        :return: Kawa Type
        """
        column = self._df[column_name]
        column_type_name = str(column.dtype)

        if re.match(r'^datetime64', column_type_name):
            return 'date_time'

        if column_type_name == 'object':
            return self._introspect_values(column_name)

        if column_type_name == 'string':
            return 'text'

        if column_type_name == 'bool':
            return 'boolean'

        if re.match(r'^u?int[0-9]*$', column_type_name):
            return 'integer'

        if re.match(r'^float[0-9]*$', column_type_name):
            return 'decimal'

        raise Exception('Column {} with type {} is not supported'.format(column_name, column_type_name))

    def _introspect_values(self, column_name):
        for val in self._df[column_name]:
            if type(val) is str:
                return 'text'
            if type(val) is date:
                return 'date'
            if type(val) is bool:
                return 'boolean'
            if type(val) is list and val:
                for list_item in val:
                    if type(list_item) is str:
                        return 'list(integer,text)'
                    if type(list_item) is int:
                        return 'list(integer,integer)'
                    if type(list_item) is float:
                        return 'list(integer,decimal)'

        return 'any'

    def _get_data_source_or_raise(self):
        if self._datasource_id:
            datasource = self._k.entities.datasources().get_entity_by_id(self._datasource_id)
            if not datasource:
                raise Exception(
                    'No datasource with id: {} was found in the current workspace'.format(self._datasource_id))
        else:
            datasource = self._k.entities.datasources().get_entity(entity_id_or_name=self._name)
            if not datasource:
                raise Exception('No datasource with name: {} was found in the current workspace'.format(self._name))
        return datasource

    def _load_data(self,
                   show_progress=True,
                   reset_data=True,
                   optimize_after_insert=False,
                   nb_threads=1,
                   parquet_file_list=None,
                   session_id_input=None):

        if self._use_arrow and not self._arrow_table:
            raise Exception('Cannot start ingestion when no data was passed to the loader')

        datasource = self._get_data_source_or_raise()
        datasource_id = datasource.get('id')

        nb_rows_to_be_inserted = (self._arrow_table if self._use_arrow else self._df).shape[0]
        indicators = datasource.get('indicators')
        session_id = session_id_input if session_id_input is not None else str(uuid.uuid4())
        print('Starting an ingestion session with id={}'.format(session_id))

        # URLs for ingestion session
        data_format = 'ArrowStream' if self._use_arrow else 'parquet'

        # Info about client
        try:
            system = slugify(platform.system() or 'NA')
        except Exception:
            system = 'NA'

        try:
            hostname = slugify(socket.gethostname() or 'NA')
        except Exception:
            hostname = 'NA'

        start_ms = int(time.time() * 1000)
        query_params_dict = {
            'datasource': datasource_id,
            'format': data_format,
            'reset': reset_data,
            'session': session_id,
            'optimize': optimize_after_insert,
            'system': system,
            'hostname': hostname,
            'start': start_ms,
            'nb_rows': nb_rows_to_be_inserted
        }
        query_params = '&'.join([f'{param}={value}' for param, value in query_params_dict.items()])

        prepare_url = '{}/ingestion/prepare?{}'.format(self._k.kawa_api_url, query_params)
        ingest_url = '{}/ingestion/upload?{}'.format(self._k.kawa_api_url, query_params)
        query_params_for_finalize = f'{query_params}&nb_rows={nb_rows_to_be_inserted}'
        finalize_url = '{}/ingestion/finalize?{}'.format(self._k.kawa_api_url, query_params_for_finalize)
        finalize_for_failure_url = '{}/ingestion/stop-with-failure?{}'.format(self._k.kawa_api_url, query_params)

        # Call prepare data that will check if we can start loading and give us the offset for automatic index
        prepare_data = self._k.post(url=prepare_url, data={})
        parquet_directory = '{}/{}'.format(self._k.tmp_files_directory, str(uuid.uuid4()))

        if not prepare_data.get('canRunLoading'):
            raise Exception(
                'We cannot start ingestion due to: ' + prepare_data.get('raisonItCannotStart', 'No reason given'))

        try:
            use_clickhouse_native_temporal_format = prepare_data.get('useClickhouseNativeTemporalFormat', False)

            # Adapt the format of date time for older versions of KAWA
            # Using the arrow loader is no longer compatible with this logic
            if self._use_arrow and not use_clickhouse_native_temporal_format:
                raise Exception('Only native format is supported with Arrow')
            elif not self._use_arrow:
                self._adapt_dataframe_to_correct_format(self._df, not use_clickhouse_native_temporal_format, indicators)

            auto_increment_indicator = [i for i in indicators if
                                        i.get('storageConfig', {}).get('automaticUniqueValue', False)]

            if len(auto_increment_indicator) == 1:
                if 'offsetToApplyToAutoIncrementIndex' not in prepare_data:
                    self._k.post(url=finalize_for_failure_url, data={})
                    raise Exception('The offset for to the auto_increment_index was not present in the answer from '
                                    'backend. Cannot continue')

                auto_increment_indicator_id = auto_increment_indicator[0].get('indicatorId')
                offset = prepare_data.get('offsetToApplyToAutoIncrementIndex')

                if self._use_arrow:
                    if auto_increment_indicator_id in self._arrow_table.schema.names:
                        self._arrow_table = self._arrow_table.remove_column(
                            self._arrow_table.schema.get_field_index(auto_increment_indicator_id))

                    index_vector = pa.array(range(offset + 1, offset + 1 + self._arrow_table.num_rows))
                    self._arrow_table = self._arrow_table.append_column(
                        auto_increment_indicator_id,
                        index_vector)
                else:
                    index_vector = numpy.arange(0, self._df.shape[0], 1)
                    self._df[auto_increment_indicator_id] = index_vector + offset + 1

            # Check that all the indicators are present in the data frame, otherwise create empty columns
            for indicator in indicators:
                indicator_id = indicator.get('indicatorId')
                if self._use_arrow and indicator_id not in self._arrow_table.schema.names:
                    default_value = self._empty_value_for_indicator(indicator)
                    new_column = pa.array([default_value] * self._arrow_table.num_rows)
                    self._arrow_table = self._arrow_table.append_column(indicator_id, new_column)

                elif not self._use_arrow and indicator_id not in self._df.columns:
                    default_value = self._empty_value_for_indicator(indicator)
                    self._df[indicator_id] = default_value

            if self._use_arrow:
                start = time.time()
                print('> Starting loading arrow stream')
                self._loading_thread_arrow(
                    ingestion_url=ingest_url,
                    arrow_table=self._arrow_table
                )
                num_rows = self._arrow_table.num_rows
                end = time.time()
                print('> {} rows were imported in {}s'.format(num_rows, end - start))
                return datasource

            # Add a partition column to split up the frames into multiple parquet files
            if not parquet_file_list:
                partition_cols = []
                nb_partitions = max(1, nb_threads)
                if nb_partitions > 1:
                    index_vector = numpy.arange(0, self._df.shape[0], 1)
                    self._df['__partition__'] = (index_vector + 1) % nb_partitions
                    partition_cols.append('__partition__')

                if show_progress:
                    print('> Exporting the dataframe into {} parquet file{}'.format(nb_partitions,
                                                                                    's' if nb_partitions > 1 else ''))
                os.makedirs(parquet_directory, exist_ok=True)
                self._df.to_parquet(partition_cols=partition_cols, path=parquet_directory + '/', compression='gzip')

            start = time.time()

            if parquet_file_list:
                parquet_files = parquet_file_list
            else:
                parquet_files = glob.glob(
                    pathname='{}/**/*.parquet'.format(parquet_directory),
                    recursive=True,
                )

            if show_progress:
                print('> Starting {} loading threads'.format(nb_threads))

            with concurrent.futures.ThreadPoolExecutor(max_workers=nb_threads) as executor:
                futures = [
                    executor.submit(self._loading_thread, ingest_url, parquet_file)
                    for parquet_file
                    in parquet_files
                ]
                concurrent.futures.wait(futures)

            end = time.time()
            if show_progress:
                print('> {} rows were imported in {}ms'.format(self._df.shape[0], end - start))

        except Exception as e:
            self._k.post(url=finalize_for_failure_url, data={})
            raise e

        finally:
            if os.path.isdir(parquet_directory):
                shutil.rmtree(parquet_directory)

            self._k.post(url=finalize_url, data={})
            if show_progress:
                print('> Import was successfully finalized')

        return datasource

    @staticmethod
    def _adapt_dataframe_to_correct_format(df,
                                           use_numbers_for_temporal_columns,
                                           indicators):
        KawaDataLoader._process_temporal_columns(indicators, df, use_numbers_for_temporal_columns)
        KawaDataLoader._process_string_columns(indicators, df)
        KawaDataLoader._process_decimal_columns(indicators, df)
        KawaDataLoader._process_integer_columns(indicators, df)

    def _adapt_arrow_to_correct_format(self,
                                       df,
                                       use_numbers_for_temporal_columns,
                                       indicators):
        if use_numbers_for_temporal_columns:
            temporal_indicators = [i for i in indicators if i.get('type') == 'date_time' or i.get('type') == 'date']
            for temporal_indicator in temporal_indicators:
                column_name = temporal_indicator.get('indicatorId')
                if column_name in df.columns:
                    column_type_name = str(df[column_name].dtype)
                    if re.match(r'^datetime64', column_type_name):
                        try:
                            column_in_unix_millis = convert_arrow_time_stamp_column_to_unix_millis(self._arrow_table,
                                                                                                   column_name)
                            self._arrow_table = self._arrow_table.set_column(
                                self._arrow_table.schema.get_field_index(column_name),
                                column_name,
                                column_in_unix_millis
                            )
                        except ValueError:
                            # todo:
                            #  fix 'ValueError: The truth value of a DatetimeIndex is ambiguous.
                            #  Use a.empty, a.bool(), a.item(), a.any() or a.all()'
                            traceback.print_exc()
                    elif temporal_indicator.get('type') == 'date':
                        date_column = self._arrow_table[column_name]
                        nb_days = pc.if_else(pc.is_null(date_column),
                                             pa.scalar(0, pa.date32()),
                                             date_column)
                        self._arrow_table = self._arrow_table.set_column(
                            self._arrow_table.schema.get_field_index(column_name),
                            column_name,
                            nb_days
                        )

    def _loading_thread(self, ingestion_url, parquet_file):
        self._k.post_binary_file(filename=parquet_file, url=ingestion_url)

    def _loading_thread_arrow(self, ingestion_url, arrow_table: pa.Table):

        def stream_batches():
            output_stream = io.BytesIO()
            schema = arrow_table.schema
            writer = ipc.RecordBatchStreamWriter(output_stream, schema)
            chunk_size = 10000
            for start in range(0, len(arrow_table), chunk_size):
                chunk = arrow_table.slice(start, chunk_size)
                writer.write_table(chunk)
                output_stream.seek(0)
                yield output_stream.getvalue()
                output_stream.truncate(0)
                output_stream.seek(0)

            writer.close()

        self._k.post_stream(
            stream=stream_batches(),
            url=ingestion_url
        )

    @staticmethod
    def _process_string_columns(indicators, df):
        # Replace None/NaN with empty strings in text columns
        text_column_names = []
        text_indicators = [i for i in indicators if i.get('type') == 'text']
        for text_indicator in text_indicators:
            column_name = text_indicator.get('indicatorId')
            if column_name in df.columns:
                text_column_names.append(column_name)

        df.fillna(value={v: '' for v in text_column_names}, inplace=True)

    @staticmethod
    def _process_decimal_columns(indicators, df):
        decimal_column_names = []
        decimal_indicators = [i for i in indicators if i.get('type') == 'decimal']
        for decimal_indicator in decimal_indicators:
            column_name = decimal_indicator.get('indicatorId')
            if column_name in df.columns:
                decimal_column_names.append(column_name)

        df[decimal_column_names] = df[decimal_column_names].astype(float)

    @staticmethod
    def _process_integer_columns(indicators, df):
        integer_column_names = []
        integer_indicators = [i for i in indicators if i.get('type') == 'integer']
        for integer_indicator in integer_indicators:
            column_name = integer_indicator.get('indicatorId')
            if column_name in df.columns:
                integer_column_names.append(column_name)

        df[integer_column_names] = df[integer_column_names].replace([np.inf, -np.inf], pd.NA)
        df[integer_column_names] = df[integer_column_names].astype('Int64')

    @staticmethod
    def _process_temporal_columns(indicators, df, use_numbers_for_temporal_columns):
        if use_numbers_for_temporal_columns:
            temporal_indicators = [i for i in indicators if i.get('type') == 'date_time' or i.get('type') == 'date']
            for temporal_indicator in temporal_indicators:
                column_name = temporal_indicator.get('indicatorId')
                if column_name in df.columns:
                    column_type_name = str(df[column_name].dtype)
                    if re.match(r'^datetime64', column_type_name):
                        try:
                            df[column_name] = df[column_name].map(
                                lambda x: int(x.timestamp() * 1000) if x and pd.notna(x) else 0)
                        except ValueError:
                            traceback.print_exc()
                    elif temporal_indicator.get('type') == 'date':
                        epoch = date(1970, 1, 1)
                        df[column_name] = df[column_name].map(lambda x: x if x and pd.notna(x) else epoch)
        else:
            date_indicators = [i for i in indicators if i.get('type') == 'date']
            for date_indicator in date_indicators:
                column_name = date_indicator.get('indicatorId')
                if column_name in df.columns:
                    df[column_name] = pd.to_datetime(df[column_name], errors='coerce').dt.date

    @staticmethod
    def _empty_value_for_indicator(indicator):
        indicator_type = indicator.get('type')
        if indicator_type == 'text':
            return ''
        if indicator_type == 'date':
            return date(1970, 1, 1)
        if indicator_type == 'date_time':
            return 0
        if indicator_type.startswith('list('):
            raise 'Does not support omitting lists'
        return None


def convert_arrow_time_stamp_column_to_unix_millis(table: pa.Table, column_name: str):
    timestamp_column = table[column_name]
    timestamp_unit = timestamp_column.type.unit

    timestamp_column_as_number = pc.if_else(pc.is_null(timestamp_column),
                                            pa.scalar(0, pa.int64()),
                                            pc.cast(timestamp_column, pa.int64()))

    if timestamp_unit == 's':
        return pc.multiply(timestamp_column_as_number, 1000)

    divider_for_millis = 1
    if timestamp_unit == 'ms':
        divider_for_millis = 1
    elif timestamp_unit == 'us':
        divider_for_millis = 1000
    elif timestamp_unit == 'ns':
        divider_for_millis = 1_000_000

    return pc.divide(timestamp_column_as_number, divider_for_millis)
