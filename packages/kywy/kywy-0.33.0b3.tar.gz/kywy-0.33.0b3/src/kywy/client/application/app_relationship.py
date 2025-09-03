from .application_building_utils import ACCEPTABLE_AGGREGATIONS, get_column
from .app_synchronizer import Synchronizer


class Relationship:

    def __init__(self, kawa, reporter, name, model, dataset, link):
        self._k = kawa
        self._reporter = reporter
        self._name = name
        self._dataset = dataset
        self._model = model
        self._link = link
        self._cached_sheet = None
        self._columns = []

    @property
    def source_sheet(self):
        return self._model.sheet

    @property
    def target_sheet(self):
        return self._dataset.sheet

    @property
    def name(self):
        return self._name

    def add_column(self, name, aggregation, new_column_name):
        uc_aggregation = aggregation.upper()
        if uc_aggregation not in ACCEPTABLE_AGGREGATIONS:
            raise Exception('The aggregation is not known, please use one of: ' + ','.join(ACCEPTABLE_AGGREGATIONS))

        self._columns.append({
            'name': name,
            'aggregation': uc_aggregation,
            'new_column_name': new_column_name,
        })

    def sync(self):
        if not self._columns:
            return

        datasource_id = self._dataset.datasource_id
        if not datasource_id:
            raise Exception('The underlying dataset has not been synced')

        if not self._link:
            raise Exception('There is no definition for the link in this relationship')

        for column in self._columns:
            Relationship._Synchronizer(
                kawa=self._k,
                relationship=self,
                column=column
            ).sync()

        self._reporter.report(
            object_type='Relationship',
            name=self._name,
        )

    def build_join_definition(self):
        joins = []
        for source, target in self._link.items():
            source_column = get_column(self.source_sheet, source)
            target_column = get_column(self.target_sheet, target)
            joins.append({
                "targetColumnId": target_column['columnId'],
                "sourceColumnId": source_column['columnId'],
            })
        return joins

    class _Synchronizer(Synchronizer):
        def __init__(self, kawa, relationship, column):
            super().__init__(
                kawa=kawa,
                icon='🔗',
                entity_description=f'Relationship "{relationship.name}"',
            )
            self._relationship = relationship
            self._column = column

        def _load_state(self):
            existing_columns = {
                c['displayInformation']['displayName']: c
                for c in self._relationship.source_sheet['computedColumns']
                if c['columnNature'] == 'LINKED' and c['columnStatus'] == 'ACTIVE'
            }
            return existing_columns.get(self._column['new_column_name'])

        def _raise_if_state_invalid(self):
            ...

        def _should_create(self):
            return self._state is None

        def _create_new_entity(self):
            source_sheet = self._relationship.source_sheet
            target_sheet = self._relationship.target_sheet
            target_column = get_column(target_sheet, self._column['name'])
            joins = self._relationship.build_join_definition()

            self._k.commands.run_command(
                command_name='addLookupField',
                command_parameters={
                    "layoutId": str(source_sheet['defaultLayoutId']),  # This is the source layout
                    "linkedSheetId": str(target_sheet['id']),  # This is the target sheet
                    "columnDefinitions": [
                        {
                            "columnId": target_column['columnId'],
                            "aggregation": self._column['aggregation'],
                            "lookupColumnName": self._column['new_column_name'],
                        }
                    ],
                    "joins": joins
                }
            )

        def _update_entity(self):
            existing_lookup_column = self._state
            existing_joins = existing_lookup_column['joins']
            new_joins = self._relationship.build_join_definition()

            existing_joins_for_comparison = sorted([(j['sourceColumnId'], j['targetColumnId']) for j in existing_joins])
            new_joins_for_comparison = sorted([(j['sourceColumnId'], j['targetColumnId']) for j in new_joins])
            if existing_joins_for_comparison != new_joins_for_comparison:
                # TODO We need to update the join for this column
                ...

            # TODO: Update aggregation -> Need to upgrade definition view

            # TODO: Update the target column (We need BE support for this)

            ...

        def _build_new_state(self):
            pass
