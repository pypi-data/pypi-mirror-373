from pypers.core.interfaces import db
from . import BaseHandler


class DynLive(BaseHandler):

    def process(self, data_file, appnum):
        st13 = data_file['st13']
        doc = data_file.get('doc')
        archive_name = data_file.get('archive_name')
        gbd_extraction_date = data_file.get('gbd_extraction_date')
        office_extraction_date = data_file.get('archive_date')
        crcs = [x['crc'] for x in data_file.get('imgs', []) if 'crc' in x.keys()]
        # -- latest dynamodb doc
        # try first to load from gbd_docs_live table
        dydb_doc = db.get_pre_prod_db().get_document(st13)
        # if not, create a new one
        if not dydb_doc:
            dydb_doc = {'st13': st13,
                        'gbd_collection': self.collection,
                        'gbd_type': self.pipeline_type
                        }

        # set the header information
        dydb_header = {'latest_run_id': self.run_id,
                       'archive':  archive_name,
                       'gbd_collection': self.collection,
                       'gbd_extraction_date': gbd_extraction_date,
                       'office_extraction_date': office_extraction_date
                       }

        dydb_doc.update(dydb_header)

        # set the logo names
        if len(crcs):
            dydb_doc.update({'logo': crcs})

        doc['data_files']['latest'] = dydb_doc
