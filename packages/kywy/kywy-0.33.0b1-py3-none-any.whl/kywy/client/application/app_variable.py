from numbers import Number
from datetime import date, datetime
from .app_synchronizer import Synchronizer


class Variable:

    def __init__(self, kawa, reporter, sheet_id_supplier, name, kawa_type, initial_value):
        self._k = kawa
        self._reporter = reporter
        self._name = name
        self._type = kawa_type.lower()
        self._initial_value = initial_value
        self._sheet_id_supplier = sheet_id_supplier

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def sheet_id_supplier(self):
        return self._sheet_id_supplier

    def sync(self):
        Variable._Synchronizer(
            kawa=self._k,
            variable=self,
        ).sync()

        self._reporter.report(
            object_type='Variable',
            name=self._name,
        )

    def formatted_initial_value(self):
        init = self._initial_value
        if self._type == 'text':
            return str(init) if init else ''
        elif self._type == 'decimal' or self._type == 'integer':
            return init if isinstance(init, Number) else 0
        elif self._type == 'date':
            return (init - date(1790, 1, 1)).days if isinstance(init, date) else None
        elif self._type == 'date_time':
            return int(init.timestamp() * 1000) if isinstance(init, datetime) else None
        elif self._type == 'boolean':
            return bool(init)
        else:
            raise Exception(f'Unsupported type for control {self._name}: {self._type}')

    def retrieve_sheet_id(self):
        return self._sheet_id_supplier()

    def control_type(self):
        if self._type == 'text':
            return 'TEXT_INPUT'
        elif self._type == 'decimal' or self._type == 'integer':
            return 'NUMBER_INPUT'
        elif self._type == 'boolean':
            return 'TOGGLE'
        elif self._type == 'date':
            return 'DATE_INPUT'
        elif self._type == 'date_time':
            return 'DATETIME_INPUT'
        else:
            raise Exception(f'Unsupported type for control {self._name}: {self._type}')

    class _Synchronizer(Synchronizer):

        def __init__(self, kawa, variable):
            super().__init__(
                kawa=kawa,
                icon='#️⃣',
                entity_description=f'Variable "{variable.name}"',
            )
            self._variable = variable

        def _load_state(self):
            sheet_id = self._variable.sheet_id_supplier()
            control_panel = self._k.entities.control_panels().get_entity_by_id(sheet_id)
            existing_parameters = control_panel['parameters']
            existing_controls = {c['displayInformation']['displayName']: c
                                 for c in control_panel['controls']} if control_panel else {}

            return {
                'controls': existing_controls,
                'parameters': existing_parameters,
            }

        def _raise_if_state_invalid(self):
            existing_controls = self._state['controls']
            existing_parameters = self._state['parameters']

            if existing_parameters and existing_controls and self._variable.name in existing_controls:
                existing_control = existing_controls[self._variable.name]
                existing_parameter = [p for p in existing_parameters if p['id'] == existing_control['parameterId']]
                existing_parameter_type = existing_parameter[0]['type']
                if existing_parameter_type != self._variable.type:
                    raise Exception(
                        'The "{}" variable already exists with type: {}. It cannot be changed to {}'.format(
                            self._variable.name,
                            existing_parameter_type,
                            self._variable.type
                        )
                    )

        def _should_create(self):
            return self._variable.name not in self._state['controls']

        def _create_new_entity(self):
            self._k.commands.run_command('createParameterControlWithLinkedParameter', {
                "sheetId": self._variable.retrieve_sheet_id(),
                "parameterConfiguration": {
                    "type": self._variable.type,
                    "initialValue": self._variable.formatted_initial_value(),
                },
                "controlConfiguration": {
                    "displayInformation": {
                        "displayName": self._variable.name,
                        "description": ""
                    },
                    "controlParameters": {
                        "control": self._variable.control_type(),
                        "size": "md"
                    }
                }
            })

        def _update_entity(self):
            ...

        def _build_new_state(self):
            pass
