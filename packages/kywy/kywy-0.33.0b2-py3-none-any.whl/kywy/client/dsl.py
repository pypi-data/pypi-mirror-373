import typing
import pyarrow
from datetime import date, datetime
import datetime as dt
from tzlocal import get_localzone
import type_enforced
from typing import Union, Dict

from ..client.computation_nodes import TreeNode


@type_enforced.Enforcer(enabled=True)
class KawaColumn:

    def __init__(self,
                 column_name: typing.Optional[str],
                 column_regexp: typing.Optional[str] = None,
                 column_alias: typing.Optional[str] = None,
                 indicator_columns_only: bool = False,
                 xml_syntactic_tree: typing.Optional[str] = None,
                 default_sheet_columns_only: bool = False):
        self._aggregation_method = None
        self._column_name = column_name
        self._column_alias = column_alias
        self._column_regexp = column_regexp
        self._indicator_columns_only = indicator_columns_only
        self._xml_syntactic_tree = xml_syntactic_tree
        self._default_sheet_columns_only = default_sheet_columns_only

    def to_dict(self):
        return {
            'columnName': self.column_name(),
            'columnAlias': self.column_alias(),
            'aggregationMethod': self.aggregation_method(),
            'columnRegexp': self.column_regexp(),
            'indicatorColumnsOnly': self.indicator_columns_only(),
            'sheetDefaultColumnsOnly': self.default_sheet_columns_only(),
            'xmlSyntacticTree': self.xml_syntactic_tree(),
        }

    def xml_syntactic_tree(self):
        return self._xml_syntactic_tree

    def indicator_columns_only(self):
        return self._indicator_columns_only

    def default_sheet_columns_only(self):
        return self._default_sheet_columns_only

    def column_regexp(self):
        return self._column_regexp

    def column_name(self):
        return self._column_name

    def aggregation_method(self):
        return self._aggregation_method

    def column_alias(self):
        return self._column_alias

    def aggregate(self, aggregation_method: str):
        self._aggregation_method = aggregation_method.upper()
        return self

    def filter(self):
        return KawaFilter(column=self)

    def alias(self, alias: str):
        self._column_alias = alias.strip()
        return self

    def filter_with_list_of_values(self, values: list[str]):
        return self.filter().in_list(values)

    # Filters
    def yoy_ytd(self):
        return self.filter().yoy_ytd()

    def date_range(self,
                   from_inclusive: typing.Optional[date] = None,
                   to_inclusive: typing.Optional[date] = None):
        return self.filter().date_range(from_inclusive, to_inclusive)

    def datetime_range(self,
                       from_inclusive: typing.Optional[datetime] = None,
                       to_inclusive: typing.Optional[datetime] = None):
        return self.filter().datetime_range(from_inclusive, to_inclusive)

    def time_range(self,
                   from_inclusive: typing.Optional[dt.time] = None,
                   from_exclusive: typing.Optional[dt.time] = None,
                   to_inclusive: typing.Optional[dt.time] = None,
                   to_exclusive: typing.Optional[dt.time] = None):
        return self.filter().time_range(
            from_inclusive=from_inclusive,
            from_exclusive=from_exclusive,
            to_inclusive=to_inclusive,
            to_exclusive=to_exclusive
        )

    def empty(self):
        return self.filter().empty()

    def not_empty(self):
        return self.filter().not_empty()

    def in_list(self, *args):
        # Note: This argument introspection is done to maintain backward compatibility
        # With pre 0.18beta7 versions
        # (commit 7b1ccb11)
        # Two ways to call this:
        # - With a tuple: K.col('text').in_list('this', 'is', 'foo')
        # - With a list:  K.col('text').in_list(['this', 'is', 'foo'])
        list_of_values = []
        if args is None:
            return self.filter().in_list([])
        for arg in args:
            if isinstance(arg, list):
                list_of_values.extend([str(v) for v in arg])
            else:
                list_of_values.append(str(arg))

        return self.filter().in_list(list_of_values)

    def starts_with(self, value: str):
        return self.filter().starts_with(value)

    def ends_with(self, value: str):
        return self.filter().ends_with(value)

    def contains(self, value: str):
        return self.filter().contains(value)

    def does_not_contain(self, value: str):
        return self.filter().does_not_contain(value)

    def does_not_start_with(self, value: str):
        return self.filter().does_not_start_with(value)

    def does_not_end_with(self, value: str):
        return self.filter().does_not_end_with(value)

    def gt(self, value: Union[float, int]):
        return self.filter().gt(value)

    def lt(self, value: Union[float, int]):
        return self.filter().lt(value)

    def gte(self, value: Union[float, int]):
        return self.filter().gte(value)

    def lte(self, value: Union[float, int]):
        return self.filter().lte(value)

    def eq(self, value: Union[float, int, str, bool]):
        return self.filter().eq(value)

    def ne(self, value: Union[float, int, str]):
        return self.filter().ne(value)

    # Aggregations
    def first(self):
        return self.aggregate('first')

    def identical(self):
        return self.aggregate('identical')

    def identical_ignore_empty(self):
        return self.aggregate('identical_ignore_empty')

    def count(self):
        return self.aggregate('count')

    def count_unique(self):
        return self.aggregate('count_unique')

    def percent_filled(self):
        return self.aggregate('percent_filled')

    def percent_empty(self):
        return self.aggregate('percent_empty')

    def count_empty(self):
        return self.aggregate('count_empty')

    def sum(self):
        return self.aggregate('sum')

    def avg(self):
        return self.aggregate('avg')

    def median(self):
        return self.aggregate('median')

    def min(self):
        return self.aggregate('min')

    def max(self):
        return self.aggregate('max')

    def min_abs(self):
        return self.aggregate('min_abs')

    def max_abs(self):
        return self.aggregate('max_abs')

    def var_sample(self):
        return self.aggregate('var_sample')

    def var_pop(self):
        return self.aggregate('var_pop')

    def std_dev_sample(self):
        return self.aggregate('std_dev_sample')

    def std_dev_pop(self):
        return self.aggregate('std_dev_pop')

    def lowest_decile(self):
        return self.aggregate('lowest_decile')

    def lowest_quartile(self):
        return self.aggregate('lowest_quartile')

    def highest_decile(self):
        return self.aggregate('highest_decile')

    def highest_quartile(self):
        return self.aggregate('highest_quartile')


@type_enforced.Enforcer(enabled=True)
class KawaFilter:

    def __init__(self,
                 column: typing.Optional[KawaColumn] = None,
                 indicator_id: typing.Optional[str] = None):
        self._column = column
        self._indicator_id = indicator_id
        if bool(column) == bool(indicator_id):
            raise AssertionError('One of column or indicator_id must be specified')

        self._exclude = False
        self._clauses = []

    def exclude(self):
        self._exclude = True
        return self

    def _add_clause(self, operator: str, value=None):
        self._clauses.append({
            'arguments': {'value': value} if value is not None else {},
            'operation': operator
        })
        return self

    def _add_clause_for_date_filter(self,
                                    from_days: typing.Optional[int],
                                    to_days: typing.Optional[int]):
        self._clauses.append({
            'arguments': {
                'dateFrom': from_days,
                'dateTo': to_days
            }
        })
        return self

    def _add_clause_for_date_time_filter(self,
                                         instant_milliseconds_from: typing.Optional[int],
                                         instant_milliseconds_to: typing.Optional[int]):
        self._clauses.append({
            'arguments': {
                'instantFrom': int(instant_milliseconds_from / 1000) if instant_milliseconds_from else None,
                'instantTo': int(instant_milliseconds_to / 1000) if instant_milliseconds_to else None,
                'instantMillisecondsFrom': instant_milliseconds_from,
                'instantMillisecondsTo': instant_milliseconds_to
            }
        })
        return self

    def _add_clause_for_time_filter(self,
                                    time_from_inclusive: typing.Optional[str],
                                    time_from_exclusive: typing.Optional[str],
                                    time_to_inclusive: typing.Optional[str],
                                    time_to_exclusive: typing.Optional[str]):
        self._clauses.append({
            'arguments': {
                'timeFromInclusive': time_from_inclusive,
                'timeFromExclusive': time_from_exclusive,
                'timeToInclusive': time_to_inclusive,
                'timeToExclusive': time_to_exclusive,
            }
        })
        return self

    def to_dict(self):
        d = {
            'exclude': self._exclude,
            'clauses': self._clauses,
        }

        if self._column:
            d['column'] = self._column.to_dict()
        if self._indicator_id:
            d['indicatorId'] = self._indicator_id

        return d

    # Empty / Not empty
    def not_empty(self):
        return self._add_clause('not_empty')

    def empty(self):
        return self._add_clause('empty')

    # Text clauses
    def in_list(self, values: list[str]):
        return self._add_clause('in_list', values)

    def contains(self, value: str):
        return self._add_clause('contains', value)

    def ends_with(self, value: str):
        return self._add_clause('ends_with', value)

    def starts_with(self, value: str):
        return self._add_clause('starts_with', value)

    def does_not_contain(self, value: str):
        return self._add_clause('does_not_contain', value)

    def does_not_end_with(self, value: str):
        return self._add_clause('does_not_end_with', value)

    def does_not_start_with(self, value: str):
        return self._add_clause('does_not_start_with', value)

    # Temporal filters
    def weekdays_only(self):
        if self._clauses and self._clauses[0]['arguments']:
            self._clauses[0]['arguments']['keepWeekDaysOnly'] = True
        return self

    def yoy_ytd(self):
        self._clauses.append({'arguments': {'specialMode': 'YOY_YTD'}})
        return self

    def date_range(self,
                   from_inclusive: typing.Optional[date] = None,
                   to_inclusive: typing.Optional[date] = None):
        from_days = (from_inclusive - date(1970, 1, 1)).days if from_inclusive else None
        to_days = (to_inclusive - date(1970, 1, 1)).days if to_inclusive else None
        return self._add_clause_for_date_filter(
            from_days=from_days,
            to_days=to_days)

    def datetime_range(self,
                       from_inclusive: typing.Optional[datetime] = None,
                       to_inclusive: typing.Optional[datetime] = None):
        from_milliseconds = int(from_inclusive.timestamp() * 1000) if from_inclusive else None
        to_milliseconds = int(to_inclusive.timestamp() * 1000) if to_inclusive else None
        return self._add_clause_for_date_time_filter(
            instant_milliseconds_from=from_milliseconds,
            instant_milliseconds_to=to_milliseconds)

    def time_range(self,
                   from_inclusive: typing.Optional[dt.time] = None,
                   from_exclusive: typing.Optional[dt.time] = None,
                   to_inclusive: typing.Optional[dt.time] = None,
                   to_exclusive: typing.Optional[dt.time] = None):

        if from_inclusive and from_exclusive:
            raise AssertionError('Both exclusive and inclusive from are defined')

        if to_inclusive and to_exclusive:
            raise AssertionError('Both exclusive and inclusive to are defined')

        return self._add_clause_for_time_filter(
            time_from_inclusive=str(from_inclusive) if from_inclusive else None,
            time_from_exclusive=str(from_exclusive) if from_exclusive else None,
            time_to_inclusive=str(to_inclusive) if to_inclusive else None,
            time_to_exclusive=str(to_exclusive) if to_exclusive else None,
        )

    # Numeric clauses
    def lt(self, value: Union[int, float]):
        return self._add_clause('lt', value)

    def lte(self, value: Union[int, float]):
        return self._add_clause('lte', value)

    def gt(self, value: Union[int, float]):
        return self._add_clause('gt', value)

    def gte(self, value: Union[int, float]):
        return self._add_clause('gte', value)

    def eq(self, value: Union[int, float, str, bool]):
        return self._add_clause('eq', value)

    def ne(self, value: Union[int, float, str]):
        return self._add_clause('ne', value)


@type_enforced.Enforcer(enabled=True)
class KawaLazyQuery:

    def __init__(self,
                 kawa_client,
                 sheet_name: typing.Optional[str] = None,
                 sheet_id: typing.Optional[str] = None,
                 datasource_id: typing.Optional[str] = None,
                 force_tz: typing.Optional[str] = None,
                 no_output: bool = False):
        self._k = kawa_client
        self._sheet_name = sheet_name
        self._sheet_id = sheet_id
        self._datasource_id = datasource_id
        self._group_by = None
        self._sample = None
        self._order_by = None
        self._as_user_id = None
        self._column_aggregations = []
        self._columns = []
        self._tz = force_tz if force_tz else str(get_localzone())
        self._filters = []
        self._limit = 100
        self._view_id = None
        self._no_output = no_output
        self._dashboard_id = None
        self._application_id = None
        self._kawa_tool = None

    def kawa_tool(self, kawa_tool, mapping: Dict[str, str], **kwargs):
        self._kawa_tool = {
            'tool': kawa_tool,
            'mapping': mapping,
            'args': kwargs,
        }
        return self

    def widget(self,
               dashboard_name: str,
               widget_name: str):
        dashboards = self._k.entities.dashboards()
        dashboard = dashboards.get_entity(dashboard_name)
        if dashboard is None:
            raise Exception('Dashboard with name {} not found in workspace'.format(dashboard_name))

        widgets = dashboard.get('widgets', [])
        for candidate_widget in widgets:
            candidate_widget_name = candidate_widget.get('displayInformation').get('displayName')
            if candidate_widget_name == widget_name:
                widget_definition = candidate_widget.get('definition')
                layout_id = widget_definition.get('layoutId')
                return self.view_id(layout_id)

        raise Exception('No widget with name {} was found in dashboard {}'.format(widget_name, dashboard_name))

    def view_id(self, view_id: str):
        self._view_id = str(view_id)
        return self

    def as_user_id(self, as_user_id: str):
        self._as_user_id = str(as_user_id)
        return self

    def filter(self, column_filter: KawaFilter):
        self._filters.append(column_filter.to_dict())
        return self

    def group_by(self, *column_names):
        if not self._group_by:
            self._group_by = []

        self._group_by += list(column_names)
        return self

    def order_by(self, column_name: str, ascending: bool = True):
        self._order_by = {
            'columnName': column_name,
            'ascending': ascending
        }
        return self

    def select(self, *columns_or_column_names):
        columns = []
        for column_or_column_name in columns_or_column_names:
            if isinstance(column_or_column_name, KawaColumn):
                columns.append(column_or_column_name.to_dict())
            elif isinstance(column_or_column_name, TreeNode):
                columns.append(column_or_column_name)
            else:
                column = KawaColumn(column_name=str(column_or_column_name))
                columns.append(column.to_dict())

        self._columns = columns
        return self

    def limit(self, limit: int):
        self._limit = limit
        return self

    def no_limit(self):
        self._limit = -1
        return self

    def agg(self, *column_aggregations):
        self._column_aggregations = [c.to_dict() for c in column_aggregations]
        return self

    def dashboard_id(self, dashboard_id: typing.Optional[str]):
        self._dashboard_id = dashboard_id
        return self

    def application_id(self, application_id: typing.Optional[str]):
        self._application_id = application_id
        return self

    def sample(self,
               sampler: str,
               how_many_buckets: int = 10,
               bucket_size: int = 10,
               buckets: typing.Optional[list[int]] = None,
               column_name: typing.Optional[str] = None):
        self._sample = {
            'columnName': column_name,
            'sampler': sampler,
            'howManyBuckets': how_many_buckets,
            'bucketSize': bucket_size,
            'buckets': buckets
        }
        return self

    def as_chart(self, chart_name='Generated chart', standalone=False):
        dsl_as_dict = self._transform_to_dict()
        view = self._k.commands.run_command(
            command_name='CreateLayoutFromDsl',
            command_parameters={
                'dsl': dsl_as_dict,
                'chartName': chart_name,
                'standalone': standalone,
            }
        )

        return view

    def compute(self,
                skip_cache: bool = False,
                use_group_names: bool = False):

        if self._sheet_name:
            # Inline XML only support sheet name
            sheet = self._load_sheet()
            self._columns = self._convert_tree_nodes_to_computed_columns(self._columns, sheet)

        return self.collect(
            use_group_names=use_group_names,
            skip_cache=skip_cache,
        )

    def collect(self,
                skip_cache: bool = False,
                use_group_names: bool = False):

        url = '{}/computation/compute-from-dsl'.format(self._k.kawa_api_url)

        data = self._transform_to_dict(skip_cache)
        response = self._k.post(url=url, data=data, stream=True)

        if self._no_output:
            return

        with pyarrow.ipc.open_stream(response.content) as reader:
            df = reader.read_pandas()

        if use_group_names and self._group_by:
            for group_id, group_name in enumerate(self._group_by):
                prev_name = f'grouping({group_id})'
                new_name = f'group({group_id}) {group_name}'
                df.rename(columns={prev_name: new_name}, inplace=True)

        if self._kawa_tool:
            return self._k.run_tool(
                tool=self._kawa_tool['tool'],
                df=df,
                mapping=self._kawa_tool['mapping'],
                **self._kawa_tool['args']
            )
        else:
            return df

    def profile(self, column_name: typing.Optional[str] = None):
        sheet = self._load_sheet()
        all_columns = sheet.get('indicatorColumns', []) + sheet.get('computedColumns', [])
        data = {
            'sheetId': sheet.get('id'),
        }

        if column_name:
            for c in all_columns:
                if c['displayInformation']['displayName'] == column_name:
                    data['columnId'] = c['columnId']

        sheet_profile = self._k.post(
            url=f'{self._k.kawa_api_url}/computation/compute-sheet-stats',
            data=data,
        )

        profile_with_column_names = {}
        for column_id, column_profile in sheet_profile.items():
            matching_column_names = [
                c['displayInformation']['displayName']
                for c in all_columns
                if c['columnId'] == column_id]

            if matching_column_names:
                profile_with_column_names[matching_column_names[0]] = column_profile

        return profile_with_column_names

    def schema(self):
        sheet = self._load_sheet()
        indicator_columns = sheet.get('indicatorColumns', [])
        computed_columns = sheet.get('computedColumns', [])

        return [{c['displayInformation']['displayName']: c['type']} for c in
                [*indicator_columns, *computed_columns]]

    def _transform_to_dict(self, skip_cache=False, ):

        body = {
            'sheetName': self._sheet_name,
            'sheetId': self._sheet_id,
            'datasourceId': self._datasource_id,
            'timeZone': self._tz,
            'limit': self._limit,
            'skipCache': skip_cache,
            'noOutput': self._no_output
        }

        if self._group_by is not None:
            body['groupBy'] = self._group_by

        if self._sample is not None:
            body['sample'] = self._sample

        if self._column_aggregations:
            body['aggregation'] = {'columns': self._column_aggregations}

        if self._columns:
            body['select'] = {'columns': self._columns}

        if self._filters:
            body['filters'] = self._filters

        if self._order_by:
            body['orderBy'] = self._order_by

        if self._view_id:
            body['viewId'] = self._view_id

        if self._as_user_id:
            body['asUserId'] = self._as_user_id

        if self._dashboard_id:
            body['dashboardId'] = self._dashboard_id

        if self._application_id:
            body['applicationId'] = self._application_id

        return body

    def _load_sheet(self):
        if not self._sheet_name:
            sheet = self._load_sheet_by_view_id()
        else:
            sheet = self._k.entities.sheets().get_entity(self._sheet_name)
        if not sheet:
            raise Exception('Sheet with name {} was not found in the current workspace'.format(self._sheet_name))
        return sheet

    def _load_sheet_by_view_id(self):
        layout = self._k.entities.layouts().get_entity_by_id(self._view_id)
        sheet = self._k.entities.sheets().get_entity_by_id(layout.get('sheetId'))
        return sheet

    @staticmethod
    def _convert_tree_nodes_to_computed_columns(columns: list, sheet):
        result = []
        for i, column in enumerate(columns):
            if isinstance(column, TreeNode):
                column_name = column.name if column.name is not None else f"col{i}"
                xml_syntactic_tree = column.to_xml(sheet, parameters=[])
                kawa_column = KawaColumn(column_name=column_name, xml_syntactic_tree=xml_syntactic_tree)
                result.append(kawa_column.to_dict())
            else:
                result.append(column)
        return result
