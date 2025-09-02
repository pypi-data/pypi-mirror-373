import boto3
from pypers.core.interfaces.config.pypers_schema_db import PYPERS_RUN_CONFIG, \
    PYPERS_LOGS, PYPERS_CONFIG, PYPES_ERRORS, PYPERS_SEEN_STEPS, \
    PYPERS_DONE_ARCHIVE, PYPERS_PRE_PROD, PYPERS_TRIGGER, PYPERS_INDEXING_CONFIG, \
    PYPERS_RUN_CONFIG_STEPS, PYPERS_PRE_PROD_HISTORY, PYPERS_ENTITY, PYPERS_OPERATIONS

class DynamoManager:

    TABLES = [PYPERS_RUN_CONFIG, PYPERS_CONFIG, PYPES_ERRORS, PYPERS_SEEN_STEPS, PYPERS_ENTITY, PYPERS_OPERATIONS,
              PYPERS_LOGS, PYPERS_DONE_ARCHIVE, PYPERS_PRE_PROD, PYPERS_TRIGGER, PYPERS_PRE_PROD_HISTORY,
              PYPERS_INDEXING_CONFIG, PYPERS_RUN_CONFIG_STEPS]
    @classmethod
    def update_capacity(cls, table, wrtie_cap, read_cap):
        client = boto3.client('dynamodb')
        args = {
            'TableName': table,
            'ProvisionedThroughput': {
                'ReadCapacityUnits': read_cap,
                'WriteCapacityUnits': wrtie_cap
            }
        }
        gcu_schema = []
        for t in DynamoManager.TABLES:
            if t['name'] == table:
                if len(t['indexes']) > 1:
                    for sec_index in t['indexes'][1:]:
                        tmp_key_schema = []
                        name = t['name']
                        for index in sec_index:
                            name = "%s_%s" % (name, index['name'])
                        gcu_schema.append(
                            {
                                'IndexName': name,
                                'ProvisionedThroughput': {
                                    'ReadCapacityUnits': read_cap,
                                    'WriteCapacityUnits': wrtie_cap
                                }
                            })
                break
        client.update_table(**args)
        for gcu in gcu_schema:
            client.update_table(**gcu)

