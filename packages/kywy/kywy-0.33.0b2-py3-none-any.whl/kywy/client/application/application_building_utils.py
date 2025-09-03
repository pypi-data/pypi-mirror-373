SHEET_CACHE = {}
ACCEPTABLE_AGGREGATIONS = ['FIRST', 'SUM', 'AVERAGE', 'COUNT', 'MEDIAN', 'COUNT_UNIQUE', 'MIN', 'MAX']
IMPORTS = [
    'from kywy.client.kawa_decorators import kawa_tool',
    'from datetime import datetime, date, timedelta',
    'import pandas as pd',
    'import numpy as np',
    'from faker import Faker',
    'import random'
]
LOGS_COLLECTOR = []


def init_logs():
    LOGS_COLLECTOR.clear()


def feedback(application_url, report_file):
    at_least_one_error = bool([m for m in LOGS_COLLECTOR if not m['ok']])
    if at_least_one_error:
        error_messages = '\n'.join([m['message'] for m in LOGS_COLLECTOR if not m['ok']])
        print('❌ There were errors')
        print('#' * 30)
        print('🚨 Please fix these:')
        print('# ERROR SECTION')
        print(error_messages)
        print('# ERROR SECTION')
        print('#' * 30)
        init_logs()
        return error_messages
    else:
        info('---' * 30)
        info(f'🎉 Publication Complete: [{application_url}]')
        info(f'📁 Report file here: [{report_file}]')
        info('---' * 30)
        init_logs()


def info(message: str):
    # TODO: Connect to logger
    LOGS_COLLECTOR.append({'ok': True, 'message': message})
    print(message)


def error(message: str):
    # TODO: Connect to logger
    LOGS_COLLECTOR.append({'ok': False, 'message': message})
    print('🚨' + message)


def start_sync(object_description: str):
    message = f'Now syncing: {object_description}'
    LOGS_COLLECTOR.append({'ok': True, 'message': message})
    print(message)


def to_tuple(i):
    if isinstance(i, str):
        return (i,)
    elif isinstance(i, tuple):
        return i
    elif isinstance(i, list):
        return tuple(i)
    else:
        raise Exception('The variable must be a string, a tuple or a list')


def load_sheet(kawa, sheet_id):
    if not sheet_id:
        raise Exception('Please specify a sheet id to load')

    cached_sheet = SHEET_CACHE.get(sheet_id)

    if not cached_sheet:
        SHEET_CACHE[sheet_id] = kawa.entities.sheets().get_entity_by_id(sheet_id)

    return SHEET_CACHE.get(sheet_id)


def load_dashboard(kawa, dashboard_id):
    return kawa.entities.dashboards().get_entity_by_id(dashboard_id)


def get_column(sheet, column_name):
    sheet_id = sheet['id']
    all_columns = sheet.get('indicatorColumns', []) + sheet.get('computedColumns', [])
    for one_column in all_columns:
        display_name = one_column['displayInformation']['displayName']
        if display_name == column_name:
            return one_column

    raise Exception(f'Column {column_name} not found in sheet {sheet_id}')


PALETTES = {
    'classic1': ['#8DD3C7', '#FFFFB3', '#BEBADA', '#FB8072', '#80B1D3', '#FDB462', '#B3DE69', '#FCCDE5', '#D9D9D9',
                 '#BC80BD'],
    'classic2': ['#26a1d5', '#ec1254', '#f27c14', '#f5e31d', '#1ee8b6', '#570bb7', '#d042f8', '#2edbef', '#3aefb6',
                 '#f10983'],
    'fire': ["#ff0000", "#ff3000", "#ff6000", "#ff9000", "#ffc000", "#043F98", "#1165C1", "#9CDEEB", "#B7E8EB",
             "#66BEF9"],
    'ice': ["#A8D8E9", "#F0F4F8", "#B2EBF2", "#E0F7FA", "#AEEEEE", "#FFFFFF", "#74C3E8", "#8EDBFF", "#B0E0E6",
            "#007B7F"],
    'constrast': ["#A4D8E1", "#003B5C", "#C2E0E5", "#E7F1F8", "#A9D6E5", "#007B8A", "#B0E1E7", "#F0FFFF", "#C8D6D4",
                  "#2A272E"],
    'autumn': ["#57291F", "#C0413B", "#D77B5F", "#FF9200", "#FFCD73", "#80003A", "#506432", "#FFC500", "#B30019",
               "#EC410B"],
    'tableau': ["#5778A4", "#E49444", "#D1615D", "#85B6B2", "#6A9F58", "#E7CA60", "#A87C9F", "#F1A2A9", "#967662",
                "#B8B0AC"],
    'excel': ["#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF", "#800000",
              "#008000"]
}
