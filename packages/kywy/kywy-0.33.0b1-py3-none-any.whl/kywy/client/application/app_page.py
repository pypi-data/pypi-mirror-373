from .app_widget import SimpleChart, Table, ScatterChart, TextWidget, IndicatorChart
from uuid import uuid4
from .app_synchronizer import Synchronizer

from .application_building_utils import load_dashboard, info, error

NUM_COLUMNS = 32


class ApplicationPage:

    def __init__(self, kawa, reporter, application, data_model, name: str):
        self._name = name
        self._data_model = data_model
        self._application = application
        self._sections = []
        self._dashboard_id = None
        self._k = kawa
        self._reporter = reporter

    @property
    def name(self):
        return self._name

    @property
    def tag(self):
        return f'{self._application.tag}|{self._name}'

    @property
    def dashboard_id(self):
        return self._dashboard_id

    @property
    def widgets(self):
        widget_collector = []
        for section in self._sections:
            for column in section.columns:
                widget_collector += column.widgets()
        return widget_collector

    def create_section(self, title, num_columns=1):

        if num_columns == 0:
            raise Exception(f'Please define at least one column for section {title}')
        if num_columns > 8:
            raise Exception(f'Please define at most eight columns for section {title}')

        new_section = ApplicationPageSection(
            kawa=self._k,
            reporter=self._reporter,
            page=self,
            title=title,
            data_model=self._data_model,
            num_columns=num_columns,
        )
        self._sections.append(new_section)
        columns = new_section.columns
        return columns[0] if num_columns == 1 else columns

    def sync(self, application_id):

        if not self._sections:
            raise Exception('You have to define at least one section by calling the create_section() function')

        self._dashboard_id = ApplicationPage._Synchronizer(
            kawa=self._k,
            page=self,
            application_id=application_id,
        ).sync()

        for section in self._sections:
            section.sync()

        self.set_layout()

        self._reporter.report(
            object_type='Dashboard',
            name=self._name,
        )

    def set_layout(self):
        current_position = 0

        # Propagate layout down to the widgets
        for section in self._sections:
            section.set_position(current_position)
            current_position = section.set_layout()

        dashboard_layout = [w.position() for w in self.widgets]
        self._k.commands.run_command('ReplaceDashboardLayout', {
            "dashboardId": str(self._dashboard_id),
            "dashboardLayout": dashboard_layout,
        })

    class _Synchronizer(Synchronizer):
        def __init__(self, kawa, page, application_id):
            super().__init__(
                kawa=kawa,
                icon='🎨',
                entity_description=f'Page "{page.name}"',
                entity_tag=page.tag,
            )
            self._page = page
            self._application_id = application_id
            self._new_dashboard_id = None

        def _load_state(self):
            return self._k.entities.dashboards().find_entity_by_tag(tag=self._tag)

        def _raise_if_state_invalid(self):
            ...

        def _should_create(self):
            return not self._state

        def _create_new_entity(self):
            component_id = str(uuid4())
            updated_application = self._k.commands.run_command(
                command_name='addNewDashboardToApplication',
                command_parameters={
                    "applicationId": str(self._application_id),
                    "componentId": component_id,
                    "layoutType": "ONE_PAGE",
                    "tag": self._tag,
                }
            )['application']

            components = updated_application.get('components', [])
            created_component = [c for c in components if c['componentId'] == component_id]
            if not created_component:
                raise Exception(f'The page {self._name} could not be created in the application')

            self._new_dashboard_id = created_component[0]['componentConfiguration']['entityId']
            self._k.commands.run_command(
                command_name='renameEntity',
                command_parameters={
                    "displayInformation": {
                        "displayName": self._page.name,
                        "description": ""
                    },
                    "entityType": "dashboard",
                    "id": str(self._new_dashboard_id)
                }
            )

        def _update_entity(self):
            dashboard_id = self._state['id']
            widgets = self._state['widgets']
            if widgets:
                widget_ids = [w['widgetId'] for w in widgets]
                self._k.commands.run_command(
                    command_name='deleteWidget',
                    command_parameters={
                        "dashboardId": str(dashboard_id),
                        "widgetIds": widget_ids,
                    }
                )

        def _build_new_state(self):
            return self._state['id'] if self._state else self._new_dashboard_id


class ApplicationPageSection:

    def __init__(self, kawa, reporter, page, data_model, title, num_columns):
        self._k = kawa
        self._reporter = reporter
        self._title = title
        self._page = page
        self._data_model = data_model
        self._columns = [
            ApplicationPageColumn(
                kawa=kawa,
                reporter=self._reporter,
                section=self,
                data_model=data_model,
                width=NUM_COLUMNS // num_columns,
                position=i * NUM_COLUMNS // num_columns
            ) for i in range(num_columns)
        ]

        # Position is the y coordinate of the top of the section
        self._position = None

    def set_position(self, y):
        self._position = y

    @property
    def position(self):
        return self._position

    @property
    def dashboard_id(self):
        return self._page.dashboard_id

    @property
    def columns(self):
        return self._columns

    def sync(self):
        info(f'🖼️ Sync a new section {self._title} with {len(self._columns)} columns')
        for column in self._columns:
            column.sync()

    def set_layout(self):
        max_y = 0
        for column in self._columns:
            y = column.set_layout()
            if y > max_y:
                max_y = y

        # Will be used to position the next section
        return max_y


class ApplicationPageColumn:

    def __init__(self, kawa, reporter, position, width, section, data_model):
        self._k = kawa
        self._reporter = reporter
        self._section = section
        self._data_model = data_model
        self._widgets = []

        # Position of the column on the x-axis and width of the column
        self._position = position
        self._width = width

        # This will be used to track the position of the current widget
        # And incremented each time we add a new one
        self._current_y = 0

    def widgets(self):
        return self._widgets

    def set_layout(self):
        self._current_y = self._section.position
        for widget in self._widgets:
            widget.set_position(
                x=self._position,
                y=self._current_y,
                width=self._width,
            )

            self._current_y += widget.compute_height(self._width)

        return self._current_y

    def indicator_chart(self, title, indicator, aggregation='SUM', source=None):
        widget = IndicatorChart(
            kawa=self._k,
            application_id_supplier=lambda: self._data_model.application_id,
            dashboard_id_supplier=lambda: self._section.dashboard_id,
            sheet_id_supplier=lambda: source.sheet_id if source else self._data_model.sheet_id,
            title=title,
            indicator=indicator,
            aggregation=aggregation,
        )
        self._widgets.append(widget)

    def text_widget(self, html):
        widget = TextWidget(
            kawa=self._k,
            dashboard_id_supplier=lambda: self._section.dashboard_id,
            content=html,
        )
        self._widgets.append(widget)

    def scatter_chart(self, title, x, y, granularity, aggregation_x='SUM', aggregation_y='SUM', aggregation_color='SUM',
                      color=None, source=None):
        # Load the sheet_id from the source: either a dataset or a model
        # It works because they both implement the sheet_id() method
        chart = ScatterChart(
            kawa=self._k,
            application_id_supplier=lambda: self._data_model.application_id,
            dashboard_id_supplier=lambda: self._section.dashboard_id,
            sheet_id_supplier=lambda: source.sheet_id if source else self._data_model.sheet_id,
            title=title,
            x=x,
            aggregation_x=aggregation_x,
            y=y,
            aggregation_y=aggregation_y,
            granularity=granularity,
            color=color,
            aggregation_color=aggregation_color,
        )
        self._widgets.append(chart)

    def bar_chart(self, title, x, y, aggregation='SUM', legend='BOTTOM', show_values=False, time_sampling=None,
                  color=None, source=None, show_totals=False, color_offset=0):
        self._simple_chart(
            title=title,
            x=x,
            y=y,
            aggregation=aggregation,
            chart_type='bar',
            color=color,
            source=source,
            time_sampling=time_sampling,
            legend=legend,
            show_values=show_values,
            show_totals=show_totals,
            color_offset=color_offset,
        )

    def line_chart(self, title, x, y, aggregation='SUM', legend='BOTTOM', show_values=False, time_sampling=None,
                   color=None, source=None, area=False, align_zero=True, fill_in_temporal_gaps=False, color_offset=0):
        self._simple_chart(
            title=title,
            x=x,
            y=y,
            aggregation=aggregation,
            chart_type='line',
            color=color,
            source=source,
            legend=legend,
            time_sampling=time_sampling,
            show_values=show_values,
            align_zero=align_zero,
            area=area,
            fill_in_temporal_gaps=fill_in_temporal_gaps,
            color_offset=color_offset,
        )

    def pie_chart(self, title, labels, values, aggregation='SUM', source=None, show_values=False, show_labels=False,
                  legend='NONE', time_sampling=None, doughnut=False):
        self._simple_chart(
            title=title,
            x=labels,
            y=values,
            aggregation=aggregation,
            chart_type='pie',
            legend=legend,
            source=source,
            show_values=show_values,
            show_labels=show_labels,
            time_sampling=time_sampling,
            doughnut=doughnut,
        )

    def boxplot(self, title, x, y, aggregation='SUM', source=None, show_values=False, time_sampling=None):
        self._simple_chart(
            title=title,
            x=x,
            y=y,
            aggregation=aggregation,
            chart_type='boxplot',
            legend='NONE',
            source=source,
            show_values=show_values,
            time_sampling=time_sampling
        )

    def table(self, title, source=None):
        table = Table(
            kawa=self._k,
            application_id_supplier=lambda: self._data_model.application_id,
            dashboard_id_supplier=lambda: self._section.dashboard_id,
            sheet_id_supplier=lambda: source.sheet_id if source else self._data_model.sheet_id,
            title=title,
        )
        self._widgets.append(table)

    def sync(self):
        for widget in self._widgets:
            try:
                widget.sync()
            except Exception as e:
                error(f'⚠️Error on sync for widget {widget.title}: {e}')
                raise e

    def _simple_chart(self, title, x, y, aggregation, chart_type, time_sampling=None, color=None, source=None,
                      legend='BOTTOM', show_values=False, show_totals=False, area=False, align_zero=True,
                      fill_in_temporal_gaps=False, show_labels=False, color_offset=0, doughnut=False, ):
        # Load the sheet_id from the source: either a dataset or a model
        # It works because they both implement the sheet_id() method
        chart = SimpleChart(
            kawa=self._k,
            application_id_supplier=lambda: self._data_model.application_id,
            dashboard_id_supplier=lambda: self._section.dashboard_id,
            sheet_id_supplier=lambda: source.sheet_id if source else self._data_model.sheet_id,
            title=title,
            chart_type=chart_type,
            x=x,
            y=y,
            color=color,
            aggregation=aggregation,
            time_sampling=time_sampling,
            legend=legend,
            show_values=show_values,
            show_totals=show_totals,
            show_labels=show_labels,
            area=area,
            align_zero=align_zero,
            fill_in_temporal_gaps=fill_in_temporal_gaps,
            color_offset=color_offset,
            doughnut=doughnut,
        )
        self._widgets.append(chart)
