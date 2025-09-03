from abc import ABC, abstractmethod
from uuid import uuid4
import json
from .application_building_utils import to_tuple, info


class Widget(ABC):

    def __init__(self, kawa, dashboard_id_supplier):
        self._k = kawa
        self._dashboard_id_supplier = dashboard_id_supplier
        self._widget_id = None
        self._x = None
        self._y = None
        self._width = None
        self._height = None

    def set_position(self, x, y, width):
        self._x = x
        self._y = y
        self._width = width
        self._height = self.compute_height(width)

    @abstractmethod
    def compute_height(self, width):
        ...

    def set_widget_id(self, widget_id):
        self._widget_id = widget_id

    def widget_id(self):
        return self._widget_id

    def position(self):
        return {
            "widgetId": str(self._widget_id),
            "positioning": {
                "width": self._width,
                "height": self._height,
                "x": self._x,
                "y": self._y,
                "slide": "dashboard"
            }
        }


class TextWidget(Widget):

    def __init__(self, kawa, dashboard_id_supplier, content):
        super().__init__(kawa=kawa, dashboard_id_supplier=dashboard_id_supplier)
        self._content = content

    @property
    def title(self):
        return self._content

    def compute_height(self, width):
        return 7

    def sync(self):
        info("💬 Creating text widget")
        dashboard_id = self._dashboard_id_supplier()
        widget_id = 'text_' + str(uuid4())
        self._k.commands.run_command('addDashboardWidgets', {
            "dashboardId": str(dashboard_id),
            "widgets": [
                {
                    "definition": {
                        "type": "RICH_TEXT_EDITOR",
                        "content": ""
                    },
                    "widgetId": widget_id,
                    "displayInformation": {
                        "displayName": "",
                        "description": ""
                    },
                    "displayParameters": {}
                }
            ]
        })
        self._k.commands.run_command('replaceWidgetDefinition', {
            "dashboardId": str(dashboard_id),
            "widgetId": widget_id,
            "widgetDefinition": {
                "type": "RICH_TEXT_EDITOR",
                "content": self._content
            }
        })
        self.set_widget_id(widget_id)


class DataWidget(Widget, ABC):

    def __init__(self,
                 kawa,
                 application_id_supplier,
                 dashboard_id_supplier,
                 sheet_id_supplier,
                 layout_type,
                 title):
        super().__init__(kawa=kawa, dashboard_id_supplier=dashboard_id_supplier)
        self._title = title
        self._application_id_supplier = application_id_supplier
        self._sheet_id_supplier = sheet_id_supplier
        self._layout_id = None
        self._layout_type = layout_type
        self._cached_sheet = None

    def sync(self):
        self._register()
        self.sync_layout()

    @abstractmethod
    def sync_layout(self):
        ...

    def compute_height(self, width):
        # TODO: Adjust this
        return 10

    @property
    def title(self):
        return self._title

    @property
    def layout_id(self):
        return self._layout_id

    @property
    def sheet_id(self):
        return self._sheet_id_supplier()

    @property
    def application_id(self):
        return self._application_id_supplier()

    @property
    def sheet(self):
        if not self._cached_sheet:
            self._cached_sheet = self._k.entities.sheets().get_entity_by_id(self.sheet_id)
        return self._cached_sheet

    def column(self, column_name):
        sheet = self.sheet
        all_columns = sheet.get('indicatorColumns', []) + sheet.get('computedColumns', [])
        for column in all_columns:
            display_name = column['displayInformation']['displayName']
            if display_name == column_name:
                return column
        raise Exception(f'The column {column_name} was not found in the sheet')

    def _register(self):
        layout_type = self._layout_type
        dashboard_id = self._dashboard_id_supplier()
        widget_id = f'{self._layout_type}-{uuid4()}'

        if not self.sheet_id:
            raise Exception('There is no sheet for this layout')

        initial_layout_id = self._k.commands.run_command('createLayout', {
            "layoutType": layout_type,
            "sheetId": self.sheet_id,
            "status": "ACTIVE",
            "createLayoutWithoutFields": (layout_type == 'CHART'),
            "standalone": False,
        })['id']
        widgets = self._k.commands.run_command('addDashboardWidgets', {
            "dashboardId": str(dashboard_id),
            "widgets": [
                {
                    "definition": {
                        "type": "SHEET",
                        "layoutId": str(initial_layout_id),
                        "sheetId": self.sheet_id,
                        "layoutType": layout_type
                    },
                    "widgetId": widget_id,
                    "displayInformation": {
                        "displayName": "",
                        "description": ""
                    },
                    "displayParameters": {}
                }
            ]
        })['dashboard']['widgets']

        widget = [w for w in widgets if w['widgetId'] == widget_id][0]
        self._layout_id = widget['definition']['layoutId']

        self._k.commands.run_command('renameEntity', {
            "id": str(self._layout_id),
            "displayInformation": {
                "displayName": self._title,
                "description": ""
            },
            "entityType": "layout"
        })

        info(f'📊 A new {layout_type} widget was created: {self._title}')
        self.set_widget_id(widget_id)
        return self._layout_id


class ScatterChart(DataWidget):

    def __init__(self,
                 kawa,
                 application_id_supplier,
                 dashboard_id_supplier,
                 sheet_id_supplier,
                 title,
                 x,
                 aggregation_x,
                 y,
                 aggregation_y,
                 granularity,
                 color=None,
                 aggregation_color=None):
        super().__init__(
            kawa=kawa,
            application_id_supplier=application_id_supplier,
            dashboard_id_supplier=dashboard_id_supplier,
            sheet_id_supplier=sheet_id_supplier,
            title=title,
            layout_type='CHART',
        )

        self._x = x
        self._aggregation_x = aggregation_x

        self._y = y
        self._aggregation_y = aggregation_y or 'SUM'

        self._granularity = granularity or 'SUM'

        self._color = color
        self._aggregation_color = aggregation_color or 'SUM'

        self._chart_type = 'scatter'

    def sync_layout(self):
        layout_id = self.layout_id

        x_column = self.column(self._x)
        y_column = self.column(self._y)
        granularity_column = self.column(self._granularity)
        color_column = self.column(self._color) if self._color else None

        # Takes care of granularity (The grouping)
        self._k.commands.run_command('addChartGrouping', {
            "layoutId": str(layout_id),
            "columnId": granularity_column['columnId'],
            "insertPosition": 1,
            "displayInformation": {
                "displayName": self._granularity,
                "description": ""
            }
        })

        # X and Y
        self._k.commands.run_command('addChartSeries', {
            "layoutId": str(layout_id),
            "columnId": x_column['columnId'],
            "displayInformation": {
                "displayName": self._x,
                "description": "",
            },
            "seriesType": self._chart_type,
            "aggregationMethod": self._aggregation_x,
        })
        modified_layout = self._k.commands.run_command('addChartSeries', {
            "layoutId": str(layout_id),
            "columnId": y_column['columnId'],
            "displayInformation": {
                "displayName": self._y,
                "description": "",
            },
            "seriesType": self._chart_type,
            "aggregationMethod": self._aggregation_y,
        })

        # Color if defined
        if color_column:
            modified_layout = self._k.commands.run_command('addChartSeries', {
                "layoutId": str(layout_id),
                "columnId": color_column['columnId'],
                "displayInformation": {
                    "displayName": self._color,
                    "description": "",
                },
                "seriesType": self._chart_type,
                "aggregationMethod": self._aggregation_color,
            })

        series_field_ids = modified_layout['fieldIdsForSeries']
        self._k.commands.run_command('replaceChartDisplayConfiguration', {
            "layoutId": str(layout_id),
            "chartDisplayConfiguration": {
                **series_and_axis(
                    chart_type=self._chart_type,
                    series_field_ids=series_field_ids,
                ),
                **chart_settings(
                    chart_type=self._chart_type,
                    scatter_color_mode=bool(self._color)
                ),
            }
        })


class SimpleChart(DataWidget):

    def __init__(self,
                 kawa,
                 application_id_supplier,
                 dashboard_id_supplier,
                 sheet_id_supplier,
                 title,
                 x,
                 y,
                 chart_type,
                 aggregation,
                 legend='BOTTOM',
                 show_values=False,
                 show_totals=False,
                 show_labels=False,
                 time_sampling=None,
                 color=None,
                 stack=True,
                 area=False,
                 align_zero=True,
                 fill_in_temporal_gaps=False,
                 color_offset=0,
                 doughnut=False,
                 ):

        super().__init__(
            kawa=kawa,
            application_id_supplier=application_id_supplier,
            dashboard_id_supplier=dashboard_id_supplier,
            sheet_id_supplier=sheet_id_supplier,
            title=title,
            layout_type='CHART',
        )

        aggr_as_tuple = to_tuple(aggregation)
        y_as_tuple = to_tuple(y)

        if len(aggr_as_tuple) != len(y_as_tuple):
            raise Exception('Both y and aggregation must have the same length')

        if len(y_as_tuple) == 0:
            raise Exception('At least one Y axis is necessary')

        self._x = x
        self._y = y_as_tuple
        self._aggregation = aggr_as_tuple
        self._color = color
        self._stack = stack
        self._chart_type = chart_type
        self._time_sampling = time_sampling
        self._legend = legend
        self._show_values = show_values
        self._show_totals = show_totals
        self._area = area
        self._align_zero = align_zero
        self._show_labels = show_labels
        self._fill_in_temporal_gaps = fill_in_temporal_gaps
        self._color_offset = color_offset
        self._doughnut = doughnut

    def sync_layout(self):

        layout_id = self.layout_id

        if not self._color:
            stacking = 0
        else:
            stacking = 2

        x_column = self.column(self._x)
        c_column = self.column(self._color) if self._color else None

        # Takes care of groups: X and color if present
        layout_with_one_grouping = self._k.commands.run_command('addChartGrouping', {
            "layoutId": str(layout_id),
            "columnId": x_column['columnId'],
            "insertPosition": 1,
            "displayInformation": {
                "displayName": self._x,
                "description": ""
            }
        })

        # Time segmentation
        if self._time_sampling:
            sampling_type = 'DATE_TIME_SAMPLER' if x_column['type'] == 'date_time' else 'DATE_SAMPLER'
            sampling_type_key = 'dateTimeSamplerType' if x_column['type'] == 'date_time' else 'dateSamplerType'
            field_id = layout_with_one_grouping['fields'][0]['fieldId']
            payload = {
                "layoutId": str(layout_id),
                "fieldId": field_id,
                "sampler": {
                    "samplerType": sampling_type,
                    sampling_type_key: self._time_sampling,
                }
            }
            self._k.commands.run_command('updateChartGrouping', payload)

        if c_column:
            self._k.commands.run_command('addChartGrouping', {
                "layoutId": str(layout_id),
                "columnId": c_column['columnId'],
                "insertPosition": 2,
                "displayInformation": {
                    "displayName": self._color,
                    "description": ""
                }
            })

        # Takes care of all y_axis:
        modified_layout = None
        for y, aggr in zip(self._y, self._aggregation):
            y_column = self.column(y)
            modified_layout = self._k.commands.run_command('addChartSeries', {
                "layoutId": str(layout_id),
                "columnId": y_column['columnId'],
                "displayInformation": {
                    "displayName": y,
                    "description": "",
                },
                "seriesType": self._chart_type,
                "aggregationMethod": aggr,
            })

        series_field_ids = modified_layout['fieldIdsForSeries']

        if self._chart_type == 'boxplot':
            self._k.commands.run_command('replaceChartSeriesType', {
                "layoutId": str(layout_id),
                "seriesTypes": {
                    series_field_ids[0]: "boxplot"
                }
            })

        self._k.commands.run_command('replaceChartDisplayConfiguration', {
            "layoutId": str(layout_id),
            "chartDisplayConfiguration": {
                **series_and_axis(
                    chart_type=self._chart_type,
                    series_field_ids=series_field_ids,
                    show_label=self._show_values,
                    show_label_names=self._show_labels,
                    line_area=self._area,
                    color_offset=self._color_offset,
                ),
                **chart_settings(
                    legend_position=self._legend,
                    chart_type=self._chart_type,
                    stacking=stacking,
                    totals=self._show_totals,
                    fill_in_temporal_gaps=self._fill_in_temporal_gaps,
                    align_zero=self._align_zero,
                    doughnut=self._doughnut,
                ),
            }
        })


class IndicatorChart(DataWidget):

    def __init__(self,
                 kawa,
                 application_id_supplier,
                 dashboard_id_supplier,
                 sheet_id_supplier,
                 title,
                 indicator,
                 aggregation):
        super().__init__(
            kawa=kawa,
            application_id_supplier=application_id_supplier,
            dashboard_id_supplier=dashboard_id_supplier,
            sheet_id_supplier=sheet_id_supplier,
            title=title,
            layout_type='CHART',
        )

        self._indicator = indicator
        self._aggregation = aggregation
        self._chart_type = 'indicator'

    def sync_layout(self):
        layout_id = self.layout_id

        indicator_column = self.column(self._indicator)
        modified_layout = self._k.commands.run_command('addChartSeries', {
            "layoutId": str(layout_id),
            "columnId": indicator_column['columnId'],
            "displayInformation": {
                "displayName": self._title,
                "description": "",
            },
            "seriesType": self._chart_type,
            "aggregationMethod": self._aggregation,
        })

        series_field_ids = modified_layout['fieldIdsForSeries']
        self._k.commands.run_command('replaceChartDisplayConfiguration', {
            "layoutId": str(layout_id),
            "chartDisplayConfiguration": {
                **series_and_axis(
                    chart_type=self._chart_type,
                    series_field_ids=series_field_ids,
                ),
                **chart_settings(
                    chart_type=self._chart_type
                ),
            }
        })

    def compute_height(self, width):
        return width // 2


class Table(DataWidget):

    def __init__(self,
                 kawa,
                 application_id_supplier,
                 dashboard_id_supplier,
                 sheet_id_supplier,
                 title):
        super().__init__(
            kawa=kawa,
            application_id_supplier=application_id_supplier,
            dashboard_id_supplier=dashboard_id_supplier,
            sheet_id_supplier=sheet_id_supplier,
            title=title,
            layout_type='GRID',
        )

    def sync_layout(self):
        ...


def chart_settings(chart_type,
                   label_items_number=50,
                   label_item_rotation=25,
                   scatter_symbol_size=10,
                   stacking=0,
                   scatter_color_mode=False,
                   legend_position='AUTO',
                   totals=False,
                   align_zero=True,
                   fill_in_temporal_gaps=False,
                   doughnut=False,
                   ):
    return {
        "scatterSymbolSize": scatter_symbol_size,
        "fillInTemporalGaps": fill_in_temporal_gaps,
        "chartType": chart_type,
        "columnValuesCustomColorsList": [],
        "comparisonColors": [],
        "comparisonsConfig": {},
        "multigrid": False,
        "doughnut": doughnut,
        "alignZero": align_zero,
        "labelItemsNumber": label_items_number,
        "labelItemRotation": label_item_rotation,
        "stacking": stacking,
        "showDataZoom": True,
        "useScale": scatter_color_mode,
        "smoothLine": False,
        "showYAxisLabel": False,
        "showPoints": True,
        "totals": totals,
        "scatterVisualMap": False,
        "scatterColorMode": scatter_color_mode,
        "scatterSeriesColor": {"colorIndexInPalette": 0},
        "legend": [{"positionMode": legend_position, "currentSize": "S"}, {"positionMode": "NONE"}],
        "formatters": {},
        "lineWidth": 1,
        "isMultiSeriesMode": True
    }


def series_and_axis(chart_type,
                    series_field_ids,
                    show_label=False,
                    show_label_names=False,
                    line_area=False,
                    color_offset=0):
    y_axis = [{"type": "value", "id": f"axis{i}"} for i in range(1, 5)]
    series_to_axis_map = {}
    series = []
    counter = 0

    for series_field_id in series_field_ids:
        counter += 1
        series_id = f'series{counter}'
        axis_id = f'axis{counter}'
        series.append({
            "id": series_id,
            "isVisible": True,
            "label": show_label,
            "labelNames": show_label_names,
            "type": chart_type,
            "lineAreaStyle": line_area,
            "colorIndexInPalette": (color_offset + counter) % 7,
            "fieldId": str(series_field_id),
            "showPoints": True,
        })
        series_to_axis_map[series_id] = axis_id

    return {
        "containers": [{"id": "c1"}],
        "yAxis": y_axis,
        "map": {
            "seriesToYAxis": series_to_axis_map,
            "yAxisToContainer": {"axis1": "c1", "axis2": "c1", "axis3": "c1", "axis4": "c1"}
        },
        "series": series,
    }
