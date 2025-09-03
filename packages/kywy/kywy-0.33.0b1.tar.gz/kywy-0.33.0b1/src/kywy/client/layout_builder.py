class KawaLayoutBuilder:

    def __init__(self, kawa_client, sheet_id, view_name, view_type):
        self._k = kawa_client
        self._cmd = self._k.commands
        self._sheet_id = str(sheet_id)
        sheet = self._k.entities.sheets().get_entity(self._sheet_id)
        self._created_layout_id = None
        self._primary_ds_id = sheet['primaryDataSourceId']
        self._filters = []
        self._view_name = view_name
        self._view_type = view_type
        self._top = {
            "sortDirection": "ASCENDING",
            "ofDepth": -1,
            "columnId": "NO_TOP",
            "count": -1,
            "perDepth": -1,
            "applicable": True,
            "aggregationMethod": "NOOP"
        }

    def set_top_dimension(self, dimension, measure, aggregation='SUM', how_many=5):
        self._top = {
            "aggregationMethod": aggregation,
            "columnId": self._column_id(measure),
            "count": how_many,
            "sortDirection": "DESCENDING",
            "groupByColumnId": self._column_id(dimension)
        }
        return self

    def add_text_filter(self, filter_column, allowed_values):
        self._filters.append({
            "allowedValues": allowed_values,
            "mode": "ValuesList",
            "applyTo": self._column_id(filter_column),
            "enabled": True,
            "identifierType": "COLUMN_ID",
            "filterType": "TEXT_FILTER",
            "initial": False,
            "depth": 0,
            "applicable": True,
            "aggregationMethod": "FIRST"
        })
        return self

    def add_rolling_range_filter(self, filter_column, range_from=-1, range_to=0, unit='DAY'):
        self._filters.append({
            "selectionSize": max(range_from, range_to),
            "selectionOffset": min(range_from, range_to),
            "temporalUnit": unit,
            "dateSelectionMethod": "ROLLING_SPAN",
            "mode": "RANGE",
            "applyTo": self._column_id(filter_column),
            "enabled": True,
            "identifierType": "COLUMN_ID",
            "filterType": "DATE_FILTER",
            "initial": False,
            "depth": 0,
            "applicable": True,
            "aggregationMethod": "MAX"
        })
        return self

    def add_numeric_range_filter(self, filter_column, range_from=None, range_to=None):
        rules = []
        if range_from is None and range_to is None:
            return
        if range_from is not None:
            rules.append({"checkAgainst": range_from, "checkMethod": "GREATER_THAN_OR_EQUALS"})
        if range_to is not None:
            rules.append({"checkAgainst": range_to, "checkMethod": "LESSER_THAN_OR_EQUALS"})

        self._filters.append({
            "operatorBetweenRules": "AND",
            "mode": "ValuesRange",
            "rules": rules,
            "applyTo": self._column_id(filter_column),
            "enabled": True,
            "identifierType": "COLUMN_ID",
            "filterType": "NUMBER_FILTER",
            "initial": False,
            "depth": 0,
            "applicable": True,
            "aggregationMethod": "SUM"
        })
        return self

    def initialize(self, standalone=True):
        print("Creating {} {}".format(self._view_type, self._view_name))
        self._created_layout_id = self._run(
            command_name='CreateLayout',
            command_parameters={
                'layoutType': self._view_type,
                'sheetId': self._sheet_id,
                'status': 'ACTIVE',
                'createLayoutWithoutFields': self._view_type == 'CHART',
                'standalone': standalone
            }
        ).get('id')
        self._run(
            command_name='RenameEntity',
            command_parameters={
                'id': self._created_layout_id,
                'displayInformation': {
                    'displayName': self._view_name,
                    'description': ''
                },
                "entityType": "layout"
            }
        )
        return self

    def _run(self, command_name, command_parameters):
        return self._cmd.run_command(
            command_name=command_name,
            command_parameters=command_parameters
        )

    def _column_id(self, column_name):
        return "{}⟶{}".format(self._primary_ds_id, column_name)

    def _apply_all_filter(self):
        self._run(
            command_name='ReplaceFiltering',
            command_parameters={
                "layoutId": self._created_layout_id,
                "filtering": {
                    "top": self._top,
                    "accessFilters": [],
                    "columnFilters": self._filters,
                    "attributeFilters": [],
                    "fieldFilters": []
                }
            }
        )


class KawaGridBuilder(KawaLayoutBuilder):

    def __init__(self, kawa_client, sheet_id, grid_name):
        super().__init__(kawa_client=kawa_client, sheet_id=sheet_id, view_name=grid_name, view_type='GRID')
        self._k = kawa_client
        self._cmd = self._k.commands
        self._sheet_id = str(sheet_id)
        sheet = self._k.entities.sheets().get_entity(self._sheet_id)
        self._primary_ds_id = sheet['primaryDataSourceId']
        self._grid_name = grid_name
        self._created_layout_id = None
        self._filters = []

    def set_grouping(self, columns):
        grouping_items = [{"fieldId": self._column_id(c)} for c in columns]
        self._run(
            command_name='ReplaceGrouping',
            command_parameters={
                "layoutId": self._created_layout_id,
                "rowGrouping": {
                    "groupingItems": grouping_items
                }
            }
        )
        return self

    def set_sorting(self, column, direction='DESCENDING'):
        self._run(command_name='ReplaceSorting',
                  command_parameters={
                      "layoutId": self._created_layout_id,
                      "sorting": {
                          "fieldSortingList": [
                              {
                                  "fieldId": self._column_id(column),
                                  "sortDirection": direction
                              }
                          ]
                      }
                  })
        return self

    def hide_fields(self, columns):
        self._run(command_name='ReplaceHiddenFields',
                  command_parameters={
                      "layoutId": self._created_layout_id,
                      "hiddenFieldIds": [self._column_id(c) for c in columns]
                  })
        return self

    def set_aggregation(self, column, aggregation_method):
        self._run(command_name='ReplaceFieldAggregation',
                  command_parameters={
                      "layoutId": self._created_layout_id,
                      "fieldId": self._column_id(column),
                      "aggregationMethod": aggregation_method
                  })
        return self

    def finalize(self):
        self._apply_all_filter()
        return self._created_layout_id


class KawaChartBuilder(KawaLayoutBuilder):

    def __init__(self, kawa_client, sheet_id, chart_name, chart_type):
        super().__init__(kawa_client=kawa_client, sheet_id=sheet_id, view_name=chart_name, view_type='CHART')
        self._chart_name = chart_name
        self._chart_type = chart_type
        self._series_id = None
        self._chart_type = chart_type

    def finalize(self,
                 legend_position='NONE',
                 bar_stacking_mode=0,
                 show_labels=True,
                 num_labels=100,
                 label_rotation=45,
                 line_area=False,
                 color=0):
        self._apply_all_filter()
        self._set_display_configuration(legend_position=legend_position,
                                        bar_stacking_mode=bar_stacking_mode,
                                        show_labels=show_labels,
                                        num_labels=num_labels,
                                        label_rotation=label_rotation,
                                        line_area=line_area,
                                        color=color)
        return self._created_layout_id

    def sort_series(self, direction='DESCENDING'):
        self._run(command_name='ReplaceSorting',
                  command_parameters={
                      "layoutId": self._created_layout_id,
                      "sorting": {
                          "fieldSortingList": [
                              {
                                  "fieldId": self._series_id,
                                  "sortDirection": direction
                              }
                          ]
                      }
                  })
        return self

    def add_comparison(self, comparison_type='PREVIOUS'):
        self._run(
            command_name='AddChartComparison',
            command_parameters={
                "layoutId": self._created_layout_id,
                "comparisons": [
                    {
                        "comparisonParameters": {
                            "fieldId": self._series_id
                        },
                        "comparisonType": comparison_type,
                        "enabled": True
                    }
                ]
            }
        )
        return self

    def add_grouping(self, column_id, name=None):
        self._run(
            command_name='AddChartGrouping',
            command_parameters={
                "layoutId": self._created_layout_id,
                "columnId": column_id,
                "insertFirst": False,
                "displayInformation": {
                    "displayName": name if name else column_id,
                    "description": ""
                }
            }
        )
        return self

    def set_sampling(self, column_id, name=None):
        self._run(
            command_name='UpdateChartGrouping',
            command_parameters={
                "layoutId": self._created_layout_id,
                "columnId": column_id,
                "insertFirst": False,
                "displayInformation": {
                    "displayName": name if name else column_id,
                    "description": ""
                }
            }
        )
        return self

    def add_series(self, column_id, name, aggregation='COUNT', unit=None):
        chart = self._run(
            command_name='AddChartSeries',
            command_parameters={
                "layoutId": self._created_layout_id,
                "columnId": column_id,
                "displayInformation": {
                    "displayName": "Measure",
                    "description": ""
                },
                "seriesType": self._chart_type
            }
        )
        series_id = chart.get('seriesIds')[0]['fieldId']
        self._run(
            command_name='RenameField',
            command_parameters={
                "layoutId": self._created_layout_id,
                "fieldId": series_id,
                "fieldName": name,
            }
        )
        self._run(
            command_name='ReplaceFieldAggregation',
            command_parameters={
                "layoutId": self._created_layout_id,
                "aggregationMethod": aggregation,
                "fieldId": series_id,
            }
        )
        if unit:
            self._run(
                command_name='ReplaceFieldFormatters',
                command_parameters={
                    "layoutId": self._created_layout_id,
                    "formatters": {
                        "decimal": {
                            "precision": {
                                "params": {
                                    "fractionDigits": 2,
                                    "numberLocale": "local"
                                }
                            },
                            "unit": {
                                "params": {
                                    "unit": "auto"
                                }
                            },
                            "postfix": {
                                "params": {
                                    "postfix": unit
                                }
                            },
                            "negative": {
                                "params": {
                                    "negativeType": "minus"
                                }
                            }
                        },
                        "integer": {
                            "precision": {
                                "params": {
                                    "fractionDigits": 0,
                                    "numberLocale": "local"
                                }
                            },
                            "unit": {
                                "params": {
                                    "unit": "auto"
                                }
                            },
                            "postfix": {
                                "params": {
                                    "postfix": unit
                                }
                            },
                            "negative": {
                                "params": {
                                    "negativeType": "minus"
                                }
                            }
                        }
                    },
                    "fieldId": self._series_id,
                }
            )
        return self

    def _set_display_configuration(self,
                                   legend_position='NONE',
                                   bar_stacking_mode=0,
                                   show_labels=True,
                                   num_labels=100,
                                   label_rotation=45,
                                   line_area=False,
                                   color=0):
        self._run(
            command_name='ReplaceChartSeriesType',
            command_parameters={
                "layoutId": self._created_layout_id,
                "seriesTypes": {
                    self._series_id: self._chart_type,
                }
            }
        )
        self._run(
            command_name='ReplaceChartDisplayConfiguration',
            command_parameters={
                "layoutId": self._created_layout_id,
                "chartDisplayConfiguration": {
                    "chartType": self._chart_type,
                    "series": [
                        {
                            "id": "s_59ab",
                            "isVisible": True,
                            "type": self._chart_type,
                            "colorIndexInPalette": color,
                            "fieldId": self._series_id,
                            "label": show_labels
                        }
                    ],
                    "map": {
                        "seriesToYAxis": {
                            "s_59ab": "a_b237"
                        },
                        "yAxisToContainer": {
                            "a_4483": "g_cef6",
                            "a_ce86": "g_cef6",
                            "a_b237": "g_cef6",
                            "a_3912": "g_cef6"
                        }
                    },
                    "yAxis": [
                        {
                            "type": "value",
                            "id": "a_b237"
                        },
                        {
                            "type": "value",
                            "id": "a_3912"
                        },
                        {
                            "type": "value",
                            "id": "a_4483"
                        },
                        {
                            "type": "value",
                            "id": "a_ce86"
                        }
                    ],
                    "comparisonsConfig": {},
                    "containers": [
                        {
                            "id": "g_cef6"
                        },
                        {
                            "id": "g_db28"
                        },
                        {
                            "id": "g_2472"
                        },
                        {
                            "id": "g_99eb"
                        }
                    ],
                    "gridLines": True,
                    "multigrid": False,
                    "lineAreaStyle": line_area,
                    "labelItemsNumber": num_labels,
                    "labelItemRotation": label_rotation,
                    "stacking": bar_stacking_mode,
                    "showDataZoom": True,
                    "smoothLine": False,
                    "showYAxisLabel": True,
                    "showPoints": True,
                    "legend": [
                        {
                            "positionMode": legend_position
                        },
                        {
                            "positionMode": "NONE"
                        }
                    ],
                    "formatters": {},
                    "lineWidth": 1,
                    "isMultiSeriesMode": True
                }}
        )
