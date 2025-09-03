import pandas as pd
from datetime import date, datetime
import uuid

from ..kawa_base_e2e_test import KawaBaseTest
from ...client.kawa_client import KawaClient as kawa
import zoneinfo


class TestPartitionManagement(KawaBaseTest):

    def test_that_data_is_deleted_based_on_a_date_time(self):
        # setup
        eastern_tz = zoneinfo.ZoneInfo('US/Eastern')
        unique_id = 'resource_{}'.format(uuid.uuid4())
        dtf1 = pd.DataFrame([
            {
                'trade_date': datetime(2024, 1, 1, 10, 0, 0, tzinfo=eastern_tz),
                'ticker': 'AAPL',
                'price': 112.3
            },
            {
                'trade_date': datetime(2024, 1, 1, 11, 0, 0, tzinfo=eastern_tz),
                'ticker': 'AAPL',
                'price': 113.3
            },
            {
                'trade_date': datetime(2024, 1, 1, 12, 0, 0, tzinfo=eastern_tz),
                'ticker': 'AAPL',
                'price': 114.3
            },
            {
                'trade_date': datetime(2024, 1, 1, 13, 0, 0, tzinfo=eastern_tz),
                'ticker': 'AAPL',
                'price': 115.3
            },
            {
                'trade_date': datetime(2024, 1, 1, 10, 0, 0, tzinfo=eastern_tz),
                'ticker': 'TSLA',
                'price': 12.3
            },
            {
                'trade_date': datetime(2024, 1, 1, 11, 0, 0, tzinfo=eastern_tz),
                'ticker': 'TSLA',
                'price': 13.3
            },
            {
                'trade_date': datetime(2024, 1, 1, 12, 0, 0, tzinfo=eastern_tz),
                'ticker': 'TSLA',
                'price': 42.3
            },
            {
                'trade_date': datetime(2024, 1, 1, 13, 0, 0, tzinfo=eastern_tz),
                'ticker': 'TSLA',
                'price': 32.3
            },
        ])

        loader = self.kawa.new_data_loader(df=dtf1, datasource_name=unique_id)
        loader.create_datasource()
        datasource = loader.load_data(reset_before_insert=True, create_sheet=True)

        # given
        delete_from = datetime(2024, 1, 1, 12, 0, 0, tzinfo=eastern_tz)
        where_clauses = [
            # Will delete everything that is after or on delete_from
            kawa.where('trade_date').datetime_range(from_inclusive=delete_from)
        ]

        # when
        self.commands.delete_data(datasource=datasource, delete_where=where_clauses)
        computed_df_after_data_delete = (self.kawa.sheet(sheet_name=unique_id)
                                         .select('trade_date', 'ticker', 'price')
                                         .compute())

        # then
        self.assertListEqual(list(computed_df_after_data_delete['trade_date']), [
            datetime(2024, 1, 1, 10, 0, 0, tzinfo=eastern_tz),
            datetime(2024, 1, 1, 11, 0, 0, tzinfo=eastern_tz),
            datetime(2024, 1, 1, 10, 0, 0, tzinfo=eastern_tz),
            datetime(2024, 1, 1, 11, 0, 0, tzinfo=eastern_tz)
        ])
        self.assertListEqual(list(computed_df_after_data_delete['ticker']), ['AAPL', 'AAPL', 'TSLA', 'TSLA'])
        self.assertListEqual(list(computed_df_after_data_delete['price']), [112.3, 113.3, 12.3, 13.3])

    def test_that_data_is_deleted_based_on_a_date_time_with_different_time_zone(self):
        # setup
        eastern_tz = zoneinfo.ZoneInfo('US/Eastern')
        pacific_tz = zoneinfo.ZoneInfo('US/Pacific')

        unique_id = 'resource_{}'.format(uuid.uuid4())
        dtf1 = pd.DataFrame([
            {
                'trade_date': datetime(2024, 1, 1, 10, 0, 0, tzinfo=eastern_tz),
                'ticker': 'AAPL',
                'price': 112.3
            },
            {
                'trade_date': datetime(2024, 1, 1, 11, 0, 0, tzinfo=eastern_tz),
                'ticker': 'AAPL',
                'price': 113.3
            },
            {
                'trade_date': datetime(2024, 1, 1, 12, 0, 0, tzinfo=eastern_tz),
                'ticker': 'AAPL',
                'price': 114.3
            },
            {
                'trade_date': datetime(2024, 1, 1, 13, 0, 0, tzinfo=eastern_tz),
                'ticker': 'AAPL',
                'price': 115.3
            },
            {
                'trade_date': datetime(2024, 1, 1, 10, 0, 0, tzinfo=eastern_tz),
                'ticker': 'TSLA',
                'price': 12.3
            },
            {
                'trade_date': datetime(2024, 1, 1, 11, 0, 0, tzinfo=eastern_tz),
                'ticker': 'TSLA',
                'price': 13.3
            },
            {
                'trade_date': datetime(2024, 1, 1, 12, 0, 0, tzinfo=eastern_tz),
                'ticker': 'TSLA',
                'price': 42.3
            },
            {
                'trade_date': datetime(2024, 1, 1, 13, 0, 0, tzinfo=eastern_tz),
                'ticker': 'TSLA',
                'price': 32.3
            },
        ])

        loader = self.kawa.new_data_loader(df=dtf1, datasource_name=unique_id)
        loader.create_datasource()
        datasource = loader.load_data(reset_before_insert=True, create_sheet=True)

        # given
        # 10:00 Pacific is 13:00 Eastern
        delete_from = datetime(2024, 1, 1, 10, 0, 0, tzinfo=pacific_tz)
        where_clauses = [
            # Will delete everything that is after or on delete_from
            kawa.where('trade_date').datetime_range(from_inclusive=delete_from)
        ]

        # when
        self.commands.delete_data(datasource=datasource, delete_where=where_clauses)
        computed_df_after_data_delete = (self.kawa.sheet(sheet_name=unique_id)
                                         .select('trade_date', 'ticker', 'price')
                                         .compute())

        # then
        self.assertListEqual(list(computed_df_after_data_delete['trade_date']), [
            datetime(2024, 1, 1, 10, 0, 0, tzinfo=eastern_tz),
            datetime(2024, 1, 1, 11, 0, 0, tzinfo=eastern_tz),
            datetime(2024, 1, 1, 12, 0, 0, tzinfo=eastern_tz),
            datetime(2024, 1, 1, 10, 0, 0, tzinfo=eastern_tz),
            datetime(2024, 1, 1, 11, 0, 0, tzinfo=eastern_tz),
            datetime(2024, 1, 1, 12, 0, 0, tzinfo=eastern_tz)
        ])
        self.assertListEqual(list(computed_df_after_data_delete['ticker']),
                             ['AAPL', 'AAPL', 'AAPL', 'TSLA', 'TSLA', 'TSLA'])
        self.assertListEqual(list(computed_df_after_data_delete['price']), [112.3, 113.3, 114.3, 12.3, 13.3, 42.3])

    def test_that_data_is_deleted_based_on_a_number_filter(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        dtf1 = pd.DataFrame([
            {'date': date(2024, 1, 1), 'int': 1, 'other': 100},
            {'date': date(2024, 1, 1), 'int': 2, 'other': 10},
            {'date': date(2024, 1, 1), 'int': 3, 'other': 10},
            {'date': date(2024, 1, 2), 'int': 4, 'other': 10},
            {'date': date(2024, 1, 2), 'int': 5, 'other': 10},
            {'date': date(2024, 1, 3), 'int': 6, 'other': 10},
            {'date': date(2024, 1, 3), 'int': 7, 'other': 10},
        ])

        loader = self.kawa.new_data_loader(df=dtf1, datasource_name=unique_id)
        loader.create_datasource()
        datasource = loader.load_data(reset_before_insert=True, create_sheet=True)
        self.kawa.entities.get_datasource_schema(datasource_id=datasource.get('id')).get('schema')

        # given
        computed_df_before_delete = self.kawa.sheet(sheet_name=unique_id).select('date', 'int', 'other').compute()
        where_clauses = [
            kawa.where('int').lte(4),
            kawa.where('other').ne(10).exclude(),
        ]

        # when
        self.commands.delete_data(datasource=datasource, delete_where=where_clauses)
        computed_df_after_data_delete = self.kawa.sheet(sheet_name=unique_id).select('date', 'int', 'other').compute()

        # then: computation before drop is correct
        self.assertListEqual(list(computed_df_before_delete['int']), list(range(1, 8)))
        self.assertListEqual(list(computed_df_before_delete['other']), [100, 10, 10, 10, 10, 10, 10])
        self.assertListEqual(list(computed_df_before_delete['date']), [
            date(2024, 1, 1),
            date(2024, 1, 1),
            date(2024, 1, 1),
            date(2024, 1, 2),
            date(2024, 1, 2),
            date(2024, 1, 3),
            date(2024, 1, 3)
        ])

        # and: computation after drop is correct
        self.assertListEqual(list(computed_df_after_data_delete['int']), [1, 5, 6, 7])
        self.assertListEqual(list(computed_df_after_data_delete['other']), [100, 10, 10, 10])
        self.assertListEqual(list(computed_df_after_data_delete['date']), [
            date(2024, 1, 1),
            date(2024, 1, 2),
            date(2024, 1, 3),
            date(2024, 1, 3)
        ])

    def test_that_data_is_deleted_based_on_a_text_filter(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        dtf1 = pd.DataFrame([
            {'ticker': 'AAPL'},
            {'ticker': 'TSLA'},
            {'ticker': 'MSFT'},
            {'ticker': 'AMZN'},
        ])

        loader = self.kawa.new_data_loader(df=dtf1, datasource_name=unique_id)
        loader.create_datasource()
        datasource = loader.load_data(reset_before_insert=True, create_sheet=True)

        # when
        where_clauses = [kawa.where('ticker').in_list(['TSLA', 'MSFT'])]
        self.commands.delete_data(datasource=datasource, delete_where=where_clauses)
        computed_df_after_data_delete = self.kawa.sheet(sheet_name=unique_id).select('ticker').compute()

        # then: computation after drop is correct
        self.assertListEqual(list(computed_df_after_data_delete['ticker']), ['AAPL', 'AMZN'])

    def test_that_data_is_deleted_based_on_a_combination_of_text_filters(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        dtf1 = pd.DataFrame([
            {'ticker': 'AAPL'},
            {'ticker': 'TSLA'},
            {'ticker': 'MSFT'},
            {'ticker': 'AMZN'},
        ])

        loader = self.kawa.new_data_loader(df=dtf1, datasource_name=unique_id)
        loader.create_datasource()
        datasource = loader.load_data(reset_before_insert=True, create_sheet=True)

        # when
        where_clauses = [
            kawa.where('ticker').contains('M'),
            kawa.where('ticker').contains('N')
        ]
        self.commands.delete_data(datasource=datasource, delete_where=where_clauses)
        computed_df_after_data_delete = self.kawa.sheet(sheet_name=unique_id).select('ticker').compute()

        # then: computation after drop is correct
        self.assertListEqual(list(computed_df_after_data_delete['ticker']), ['AAPL', 'TSLA', 'MSFT'])

    def test_that_data_is_deleted_based_on_a_date_filter(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        dtf1 = pd.DataFrame([
            {'date': date(2024, 1, 1)},
            {'date': date(2024, 1, 2)},
            {'date': date(2024, 1, 3)},
            {'date': date(2024, 1, 4)},
        ])

        loader = self.kawa.new_data_loader(df=dtf1, datasource_name=unique_id)
        loader.create_datasource()
        datasource = loader.load_data(reset_before_insert=True, create_sheet=True)

        # when
        where_clauses = [
            kawa.where('date').date_range(
                from_inclusive=date(2024, 1, 2),
                to_inclusive=date(2024, 1, 3))
        ]
        self.commands.delete_data(datasource=datasource, delete_where=where_clauses)
        computed_df_after_data_delete = self.kawa.sheet(sheet_name=unique_id).select('date').compute()

        # then: computation after drop is correct
        self.assertListEqual(list(computed_df_after_data_delete['date']), [
            date(2024, 1, 1),
            date(2024, 1, 4)
        ])

    def test_that_data_is_deleted_based_on_a_combination_of_date_time_and_text_filters(self):
        # setup
        unique_id = 'resource_{}'.format(uuid.uuid4())
        dtf1 = pd.DataFrame([
            {'k': 1, 'ticker': 'AAPL', 'trade_date': datetime(2024, 1, 1, 13, 0, 0)},
            {'k': 2, 'ticker': 'AAPL', 'trade_date': datetime(2024, 1, 1, 13, 1, 0)},
            {'k': 3, 'ticker': 'AAPL', 'trade_date': datetime(2024, 1, 1, 13, 2, 0)},
            {'k': 4, 'ticker': 'AAPL', 'trade_date': datetime(2024, 1, 1, 13, 3, 0)},
            {'k': 5, 'ticker': 'MSFT', 'trade_date': datetime(2024, 1, 1, 13, 0, 0)},
            {'k': 6, 'ticker': 'MSFT', 'trade_date': datetime(2024, 1, 1, 13, 1, 0)},
            {'k': 7, 'ticker': 'MSFT', 'trade_date': datetime(2024, 1, 1, 13, 2, 0)},
            {'k': 8, 'ticker': 'MSFT', 'trade_date': datetime(2024, 1, 1, 13, 3, 0)},
        ])

        loader = self.kawa.new_data_loader(df=dtf1, datasource_name=unique_id)
        loader.create_datasource()
        datasource = loader.load_data(reset_before_insert=True, create_sheet=True)

        # when
        utc = zoneinfo.ZoneInfo('UTC')
        from_date = datetime(2024, 1, 1, 13, 1, 0, tzinfo=utc)
        where_clauses = [
            kawa.where('ticker').in_list(['MSFT']),
            kawa.where('trade_date').datetime_range(from_inclusive=from_date)
        ]
        self.commands.delete_data(datasource=datasource, delete_where=where_clauses)
        computed_df_after_data_delete = self.kawa.sheet(sheet_name=unique_id).select('k').compute()

        # then: computation after drop is correct
        self.assertListEqual(list(computed_df_after_data_delete['k']), [1, 2, 3, 4, 5])
