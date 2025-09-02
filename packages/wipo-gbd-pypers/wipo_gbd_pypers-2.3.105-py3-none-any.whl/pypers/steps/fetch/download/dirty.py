import json
import os
import re
from datetime import datetime
import json
from pypers.utils import utils
from pypers.core.step import FunctionStep
from pypers.steps.base import merge_spec_dict
from pypers.core.interfaces import db
from pypers.core.interfaces.db.cache import clear_cache


class Dirty(FunctionStep):
    base_spec = {
        "args": {
            "inputs": [],
            "params": [
                {
                    "name": "limit",
                    "type": "int",
                    "descr": "the upper limit of the archives to fetch. "
                             "default 0 (all)",
                    "value": 100
                },
                {
                    "name": "collPrefix",
                    "type": "str",
                    "descr": "regular expression to filter files",
                    "value": ".*"
                },
                {
                    "name": "cmd_retry_limit",
                    "type": "int",
                    "descr": "the limit to retry a command until the pipeline "
                             "step fails",
                    "value": 5
                },
                {
                    "name": "http_get_retries",
                    "type": "int",
                    "descr": "the limit to retry an http get until the "
                             "step fails",
                    "value": 7
                },
                {
                    "name": "http_get_delay",
                    "type": "int",
                    "descr": "initial delay between retries in seconds",
                    "value": 4
                },
                {
                    "name": "http_get_backoff",
                    "type": "int",
                    "descr": "backoff multiplier "
                             "e.g. value of 2 will double the delay each retry",
                    "value": 2
                }
            ],
            "outputs": [
                {
                    "name": "output_files",
                    "type": "file",
                    "descr": "the download files from the feed"
                }
            ]
        }
    }

    spec = {
        "version": "2.0",
        "descr": [
            "Fetch archives from either a local dir"
        ],
    }


    def __init__(self, *args, **kwargs):
        merge_spec_dict(self.spec, self.base_spec)
        super(Dirty, self).__init__(*args, **kwargs)
        self.logger = self.log


    def process(self):
        clear_cache(self.meta['pipeline'].get('output_dir', None))
        records = db.get_db_dirty().get_uids(self.collPrefix, self.limit)
        dest_file = os.path.join(self.output_dir, '%s.json' % datetime.now().strftime('%Y-%m-%d'))
        with open(dest_file, 'w') as f:
            json.dump(records,f)
        self.output_files.append(dest_file)



