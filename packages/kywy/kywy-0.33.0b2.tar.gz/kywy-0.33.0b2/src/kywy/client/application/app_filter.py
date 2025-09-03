from .app_synchronizer import Synchronizer
from .application_building_utils import load_sheet, get_column


class TextFilter:

    def __init__(self, kawa, reporter, name):
        self._k = kawa
        self._reporter = reporter
        self._name = name
        self._columns = []

    @property
    def name(self):
        return self._name

    @property
    def columns(self):
        return self._columns

    def append_column(self, sheet_id_supplier, column_name):
        self._columns.append({
            'sheet_id_supplier': sheet_id_supplier,
            'name': column_name
        })

    def sync(self, extended_application):
        TextFilter._Synchronizer(
            kawa=self._k,
            text_filter=self,
            application_id=extended_application['application']['id'],
            control_panel=extended_application['extendedControlPanel'],
        ).sync()

    class _Synchronizer(Synchronizer):
        def __init__(self, kawa, text_filter, application_id, control_panel):
            super().__init__(
                kawa=kawa,
                icon='🚦',
                entity_description=f'Filter "{text_filter.name}"',
            )
            self._filter = text_filter
            self._control_panel = control_panel
            self._application_id = application_id

        def _load_state(self):
            filter_controls = {
                c['displayInformation']['displayName']: c
                for c in self._control_panel['controls']
                if c['controlType'] == 'FILTER_CONTROL'
            }
            return filter_controls.get(self._filter.name)

        def _raise_if_state_invalid(self):
            ...

        def _should_create(self):
            return not self._state

        def _create_new_entity(self):
            apply_to = self._build_apply_to()
            self._k.commands.run_command('createFilterControlWithLinkedFilter', {
                "applicationId": str(self._application_id),
                "filterConfiguration": {
                    "filterType": "TEXT_FILTER",
                    "applyTo": apply_to,
                    "filterOutNullValues": True
                },
                "controlConfiguration": {
                    "displayInformation": {
                        "displayName": self._filter.name,
                        "description": ""
                    },
                    "controlParameters": {
                        "mode": "ValuesList",
                        "multiSelection": True,
                        "size": "md"
                    }
                }
            })

        def _update_entity(self):
            ...

        def _build_new_state(self):
            ...

        def _build_apply_to(self):
            apply_to = []
            for column in self._filter.columns:
                sheet_id_supplier = column['sheet_id_supplier']
                column_name = column['name']

                sheet_id = sheet_id_supplier()
                sheet = load_sheet(self._k, sheet_id)
                column = get_column(sheet, column_name)

                apply_to.append({
                    'columnId': column['columnId'],
                    'sheetId': str(sheet_id),
                })
            return apply_to
