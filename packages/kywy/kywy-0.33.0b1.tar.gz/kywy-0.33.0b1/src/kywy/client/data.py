import os.path
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import uuid
import glob
import shutil
import numpy as np
import time


class KawaData:

    def __init__(self, kawa_client):
        self._k = kawa_client

    def wrap_sql_query(self, sheet_name_or_id, sql):
        sheet = self._k.entities.sheets().get_entity(sheet_name_or_id)
        if not sheet:
            raise Exception('Sheet with name/id {} was not found in the current workspace'.format(sheet_name_or_id))

        url = '{}/computation/sql-query-for-gen-ai'.format(self._k.kawa_api_url)
        response = self._k.post(url=url, data={
            'sheetName': sheet.get('displayInformation').get('displayName'),
            'sql': sql
        })
        return response.get('sql')

    def create_datasource_and_load(self,
                                   datasource_name,
                                   df,
                                   column_to_attribute=None,
                                   primary_key_columns=None,
                                   ignore_new_columns=False,
                                   default_columns=None,
                                   create_sheet=False,
                                   reset_data=True,
                                   delete_datasource_and_recreate=False,
                                   type_overrides=None,
                                   shared=False,
                                   list_of_parquet_files=None,
                                   **xargs):

        return self.__create_datasource_and_load(datasource_name=datasource_name,
                                                 df=df,
                                                 column_to_attribute=column_to_attribute,
                                                 primary_key_columns=primary_key_columns,
                                                 ignore_new_columns=ignore_new_columns,
                                                 default_columns=default_columns,
                                                 create_sheet=create_sheet,
                                                 reset_data=reset_data,
                                                 delete_datasource_and_recreate=delete_datasource_and_recreate,
                                                 type_overrides=type_overrides,
                                                 shared=shared,
                                                 list_of_parquet_files=list_of_parquet_files,
                                                 private_join_datasource=False)

    def create_private_join_datasource_and_load(self,
                                                datasource_name,
                                                df,
                                                column_to_attribute=None,
                                                default_columns=None,
                                                type_overrides=None,
                                                show_progress=True,
                                                list_of_parquet_files=None):

        self.__create_datasource_and_load(datasource_name=datasource_name,
                                          df=df,
                                          column_to_attribute=column_to_attribute,
                                          primary_key_columns=None,
                                          ignore_new_columns=False,
                                          default_columns=default_columns,
                                          create_sheet=False,
                                          reset_data=True,
                                          delete_datasource_and_recreate=False,
                                          type_overrides=type_overrides,
                                          shared=False,
                                          show_progress=show_progress,
                                          list_of_parquet_files=list_of_parquet_files,
                                          private_join_datasource=True)

    def __create_datasource_and_load(self,
                                     datasource_name,
                                     df,
                                     column_to_attribute=None,
                                     primary_key_columns=None,
                                     ignore_new_columns=False,
                                     default_columns=None,
                                     create_sheet=False,
                                     reset_data=True,
                                     delete_datasource_and_recreate=False,
                                     type_overrides=None,
                                     shared=False,
                                     show_progress=True,
                                     list_of_parquet_files=None,
                                     private_join_datasource=False):

        datasource_id = self._k.entities.datasources().get_entity_id(entity_name=datasource_name)

        if not primary_key_columns:
            primary_key_columns = []
        if not column_to_attribute:
            column_to_attribute = {}

        if datasource_id and delete_datasource_and_recreate:
            self._k.commands.delete_datasource(datasource=datasource_id)

        datasource = self.__create_datasource(df=df,
                                              shared=shared,
                                              default_columns=default_columns,
                                              datasource_name=datasource_name,
                                              column_to_attribute=column_to_attribute,
                                              primary_key_columns=primary_key_columns,
                                              type_overrides=type_overrides,
                                              private_join_datasource=private_join_datasource)

        if not ignore_new_columns:
            self.__add_missing_indicators_to_datasource(df=df,
                                                        datasource=datasource,
                                                        type_overrides=type_overrides)

        self.__load_data(df=df,
                         datasource=datasource,
                         reset_data=reset_data,
                         show_progress=show_progress,
                         list_of_parquet_files=list_of_parquet_files)

        if create_sheet:
            self._k.commands.create_sheet(datasource=datasource,
                                          sheet_name=datasource_name)

        return datasource

    def __load_data(self, datasource, df, show_progress=True, reset_data=True, list_of_parquet_files=None):
        print(
            'WARNING: This method to load data is deprecated. '
            'Please refer to https://docs.kawa.ai/python-api-for-data-analytics#36e18270b6c9465b95252248ff3802b5')
        datasource_id = datasource if isinstance(datasource, str) else datasource.get('id')
        indicators = datasource.get('indicators')
        session_id = str(uuid.uuid4())

        print('Starting an ingestion session with id={}'.format(session_id))

        # URLs for ingestion session
        query_params = 'datasource={}&format=parquet&reset={}&session={}'.format(datasource_id, reset_data, session_id)
        prepare_url = '{}/ingestion/prepare?{}'.format(self._k.kawa_api_url, query_params)
        ingest_url = '{}/ingestion/upload?{}'.format(self._k.kawa_api_url, query_params)
        finalize_url = '{}/ingestion/finalize?{}'.format(self._k.kawa_api_url, query_params)
        finalize_for_failure_url = '{}/ingestion/stop-with-failure?{}'.format(self._k.kawa_api_url, query_params)

        # Check that all date and date time indicators are numbers in the data frame
        temporal_indicators = [i for i in indicators if
                               i.get('type') == 'date' or i.get('type') == 'date_time']
        for temporal_indicator in temporal_indicators:
            df_type_name = df[temporal_indicator.get('indicatorId')].dtype
            if 'datetime' in str(df_type_name):
                raise Exception(
                    "When using accelerated loading, "
                    "date and date_time columns should be converted to numbers. Date columns should be expressed "
                    "as number of days since epoch and Date time columns as number of milliseconds since epoch.")

        # Call prepare data that will check if we can start loading and give us the offset for automatic index
        prepare_data = self._k.post(url=prepare_url, data={})

        if not prepare_data.get('canRunLoading'):
            raise Exception(
                'We cannot start ingestion due to: ' + prepare_data.get('raisonItCannotStart', 'No reason given'))

        parquet_directory = '{}/{}'.format(self._k.tmp_files_directory, str(uuid.uuid4()))
        os.makedirs(parquet_directory, exist_ok=True)

        try:
            auto_increment_indicator = [i for i in indicators if
                                        i.get('storageConfig', {}).get('automaticUniqueValue', False)]

            if len(auto_increment_indicator) == 1:
                if 'offsetToApplyToAutoIncrementIndex' not in prepare_data:
                    self._k.post(url=finalize_for_failure_url, data={})
                    raise Exception('The offset for to the auto_increment_index was not present in the answer from '
                                    'backend. Cannot continue')

                auto_increment_indicator_id = auto_increment_indicator[0].get('indicatorId')
                df[auto_increment_indicator_id] = df.index + prepare_data.get('offsetToApplyToAutoIncrementIndex') + 1

            if list_of_parquet_files:
                futures = []
                with ThreadPoolExecutor(10) as executor:
                    for file_name in list_of_parquet_files:
                        futures.append(executor.submit(self._k.post_binary_file, file_name, ingest_url))
                wait(futures, return_when=ALL_COMPLETED)

            else:
                partition_cols = []

                if show_progress:
                    print('> Exporting the dataframe a parquet file')
                df.to_parquet(partition_cols=partition_cols, path=parquet_directory + '/', compression='gzip')
                start = time.time()
                file_name = glob.glob('{}/**/*.parquet'.format(parquet_directory), recursive=True)[0]
                self._k.post_binary_file(filename=file_name, url=ingest_url)
                end = time.time()
                if show_progress:
                    print('> {} rows were imported in {}ms'.format(df.shape[0], end - start))

        except Exception as e:
            self._k.post(url=finalize_for_failure_url, data={})
            raise e

        finally:
            if os.path.isdir(parquet_directory):
                shutil.rmtree(parquet_directory)

            if list_of_parquet_files:
                for filename in list_of_parquet_files:
                    try:
                        os.remove(filename)
                    except OSError:
                        pass

            self._k.post(url=finalize_url, data={})
            if show_progress:
                print('> Import was successfully finalized')

    def __add_missing_indicators_to_datasource(self, datasource, df, type_overrides=None):

        if not type_overrides:
            type_overrides = {}

        existing_indicator_id = [i.get('indicatorId') for i in datasource.get('indicators', [])]

        new_indicators = []
        for column_name in df.columns:
            new_indicator = self.__get_indicator_from_column(type_override=type_overrides.get(column_name),
                                                             df_column=df[column_name])

            new_indicator_id = new_indicator.get('indicatorId')
            if not (new_indicator_id in existing_indicator_id):
                new_indicators.append(new_indicator)

        if new_indicators:
            print('Adding the following indicators: {}'.format([i.get('indicatorId') for i in new_indicators]))
            self._k.commands.add_indicators_to_datasource(datasource=datasource,
                                                          new_indicators=new_indicators)

    def __create_datasource(self, datasource_name, df, column_to_attribute, primary_key_columns,
                            shared=False, default_columns=None, type_overrides=None, private_join_datasource=False):

        if not type_overrides:
            type_overrides = {}

        # Create all the needed attributes first
        # (This operation is idempotent)
        for key, value in column_to_attribute.items():
            self._k.commands.create_attribute(value)

        indicators = []
        for column_name in df.columns:
            is_attribute = column_name in column_to_attribute
            is_default = not default_columns or column_name in default_columns

            indicator = self.__get_indicator_from_column(df_column=df[column_name],
                                                         type_override=type_overrides.get(column_name),
                                                         attribute_name=column_to_attribute.get(column_name),
                                                         is_default=is_default or is_attribute,
                                                         is_primary_key=column_name in primary_key_columns)
            indicators.append(indicator)

        # A private join datasource must have the same primary keys as the main datasource
        if private_join_datasource:
            main_datasource = self._k.entities.datasources().get_entity(entity_name=datasource_name)
            for main_ds_indicator in main_datasource['indicators']:
                if 'key' in main_ds_indicator:
                    key = main_ds_indicator['key']
                    if 'keyType' in key:
                        keyType = key['keyType']
                        if keyType == 'PRIMARY_SHARDING_KEY' or keyType == 'PRIMARY_KEY':
                            indicators.append(main_ds_indicator)

        # Add the auto increment key if there is no specified key
        key_indicators = [i for i in indicators if 'key' in i]
        if not key_indicators and not private_join_datasource:
            indicators.append({
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

        datasource = {
            'shared': shared,
            'displayInformation': {
                'displayName': datasource_name
            },
            'storageConfiguration': {
                'loadingAdapterName': 'CLICKHOUSE'
            },
            'indicators': indicators,
            'dataCategoryId': '1'
        }

        if private_join_datasource:
            return self._k.commands.create_private_join_datasource(datasource)
        else:
            return self._k.commands.create_datasource(datasource)

    def __get_indicator_from_column(self, df_column, is_default=True, type_override=None, attribute_name=None,
                                    is_primary_key=False):

        attribute_id = (self._k
                        .entities
                        .attributes()
                        .get_entity_id(attribute_name))

        column_name = df_column.name
        df_type_name = df_column.dtype.base
        kawa_type = self.__resolve_type(df_type_name.name)

        # We have to detect arrays as well as their types
        # This is a poor method but let's leave it there for now
        first_defined_element = None
        for element in df_column.to_list():
            if element is not None:
                first_defined_element = element
                break

        if isinstance(first_defined_element, list):
            list_from_df = first_defined_element
            if len(list_from_df) == 0:
                kawa_type = 'list(integer,text)'
            else:
                first = list_from_df[0]
                if isinstance(first, (int, float, complex)) and not isinstance(first, bool):
                    kawa_type = 'list(integer,decimal)'
                else:
                    kawa_type = 'list(integer,text)'

        # Apply override if available
        if type_override:
            kawa_type = type_override

        indicator = {
            'displayInformation': {
                'displayName': column_name
            },
            'includedInDefaultLayout': is_default,
            'indicatorId': column_name,
            'storageConfig': {
                'indexed': bool(is_primary_key or attribute_id)
            },
            'type': kawa_type
        }

        if attribute_id is not None:
            indicator['attributeId'] = attribute_id

        if is_primary_key:
            indicator['key'] = {
                'keyType': 'PRIMARY_SHARDING_KEY'
            }

        return indicator

    @staticmethod
    def __resolve_type(np_type_name):
        if np_type_name in KAWA_TYPES_DICT:
            return KAWA_TYPES_DICT.get(np_type_name)

        if 'datetime' in np_type_name:
            return K_DATE

        return K_TEXT


K_CATEGORY = 'category'
K_DATE = 'date'
K_BOOLEAN = 'boolean'
K_TEXT = 'text'
K_DECIMAL = 'decimal'
K_INTEGER = 'integer'

KAWA_TYPES_DICT = {np.dtype(str).name: K_TEXT,
                   np.dtype(object).name: K_TEXT,
                   K_CATEGORY: K_TEXT,
                   np.dtype(bool).name: K_BOOLEAN,
                   np.dtype(np.datetime64).name: K_DATE,
                   np.dtype(np.int8).name: K_INTEGER,
                   np.dtype(np.int16).name: K_INTEGER,
                   np.dtype(np.int32).name: K_INTEGER,
                   np.dtype(np.int64).name: K_INTEGER,
                   np.dtype(np.timedelta64).name: K_INTEGER,
                   np.dtype(np.uint8).name: K_INTEGER,
                   np.dtype(np.uint16).name: K_INTEGER,
                   np.dtype(np.uint32).name: K_INTEGER,
                   np.dtype(np.uint64).name: K_INTEGER,
                   np.dtype(np.float16).name: K_DECIMAL,
                   np.dtype(np.float32).name: K_DECIMAL,
                   np.dtype(np.float64).name: K_DECIMAL,
                   np.dtype(np.complex64).name: K_DECIMAL,
                   np.dtype(np.complex128).name: K_DECIMAL
                   }
