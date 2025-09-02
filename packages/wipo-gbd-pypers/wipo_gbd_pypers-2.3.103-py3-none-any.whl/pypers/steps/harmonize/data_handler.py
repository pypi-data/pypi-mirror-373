import os
import json
import traceback

if os.environ.get('GITHUB_TOKEN'):
    from pypers.test import MockXMLParser as Parser
    from pypers.test import MockRuleEngine as RuleEngine
    from pypers.test import ErrorSeverityMock as ErrorSeverity

else:
    from gbdtransformation.parser import Parser
    from gbdvalidation.engine import RuleEngine
    from gbdvalidation.rules import ErrorSeverity

from pypers.utils.utils import rename_file
from . import BaseHandler

parsers = {}
validator = RuleEngine()


class GBDFormat(BaseHandler):

    def process(self, data_file, appnum):
        if not data_file:
            return

        collection_name = self.collection
        if collection_name.endswith("full"):
            collection_name = collection_name.replace("full", "")

        if not parsers.get(collection_name, None):
            parsers[collection_name] = Parser(collection_name, type=self.pipeline_type)
        parser = parsers.get(collection_name)
        office_extraction_date = data_file.get('archive_date')
        archive_name = data_file.get('archive_name')
        data = data_file.get('data', {})

        if not data:
            return
        errors = []
        ori_file = os.path.join(self.extraction_dir, data['ori'])

        # attempt the transformation to append to data_files
        # {'123': {'ori': _, 'st13': _, 'gbd': _}, '234': {'ori': _, 'st13': _, 'gbd': _}}
        try:
            gbd_str = parser.run(ori_file, raise_errors=True)
            gbd_data = json.loads(gbd_str)
            st13 = gbd_data.get('st13', None)

            # failed transformation
            if not st13:
                raise Exception('no st13 in gbd file !')
            # PL: the following doesn't make sense, if an Office status date is unknown, 
            # we should preserve this info rather that inventing a fake status date
            # it also breaks the indexing when we don't get the 'archive_date'
            #if not gbd_data.get('statusDate'):
            #    gbd_data['statusDate'] = office_extraction_date
        # transformation failed to execute
        except Exception as e:
            self.logger.error('transform - %s: %s' % (appnum, str(e) + traceback.format_exc()))
            return

        # get the QC of the file
        # [ { code: _, severity: _, message: _ } ]
        #try:
        #    qc_errors = validator.validate_with_dict(gbd_data)
        # validation failed to execute
        #except Exception as e:
        #    self.logger.error('validation - %s: %s' % (appnum, str(e) + traceback.format_exc()))
        #    return

        #for error in qc_errors:
        #    if error.get('severity', None) == ErrorSeverity.CRITICAL:
        #        raise Exception("%s : %s" % (appnum, error.get('message')))

        # set the qc in the gbd file
        #if qc_errors and len(qc_errors):
        #    gbd_data['qc'] = qc_errors

        gbd_data['runid'] = self.run_id

        # write the gbd.json file
        gbd_file = ori_file.replace('.xml', '.json')
        with open(gbd_file, 'w') as f:
            json.dump(gbd_data, f, indent=2)

        # back up and delete original data file
        # check if the collection is not amoung the collection with disable ori backup
        self.backup.store_doc_ori(ori_file, archive_name, st13, hard=False)
        gbd_file = rename_file(gbd_file, os.path.join(st13, self.run_id))

        # prepare data for analysis and idx
        doc = {
            'data_files': {
                'latest': {},
            },
            'img_files': [],
            'feature': "%s" % gbd_data.get('markFeature')}

        # set gbd, qc and st13 in the data_files
        data_file['st13'] = st13
        #data_file['qc'] = qc_errors or []
        data_file['qc'] = []
        data_file['gbd'] = gbd_file
        # update ori file in the data_files
        data_file['ori'] = os.path.relpath(ori_file,
                                           self.extraction_dir)
        data_file['doc'] = doc
