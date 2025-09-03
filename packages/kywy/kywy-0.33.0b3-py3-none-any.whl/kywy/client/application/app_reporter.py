import json
import tempfile
from datetime import datetime

"""
The reporter is a shared DICT across all generated objects with an export method
"""


class Reporter():

    def __init__(self, name):
        now = datetime.now()
        self._report = {
            'name': name,
            'start': now.strftime("%Y-%m-%d %H:%M:%S"),
            'report': {}
        }

    def report(self, object_type, name):
        if object_type not in self._report['report']:
            self._report['report'][object_type] = []

        self._report['report'][object_type].append({
            'name': name,
            'description': 'TODO',
        })

    def export(self):
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_file:
            json.dump(self._report, tmp_file, indent=4)
            tmp_file.flush()
            return tmp_file.name
