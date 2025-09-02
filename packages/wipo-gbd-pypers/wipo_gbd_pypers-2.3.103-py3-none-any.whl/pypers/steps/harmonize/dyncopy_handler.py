import os

from pypers.core.interfaces.db.cache import CachedCopy
from . import BaseHandler

class DynCopy(BaseHandler):

    def process(self, data_file, appnum):
        # nothing has been extracted
        if not data_file:
            return

        office_extraction_date = data_file.get('archive_date')
        archive_name = data_file.get('archive_name')
        gbd_extraction_date = data_file.get('gbd_extraction_date')
        img_info = data_file.get('imgs', [])
        data_info = data_file.get('data', {})
        #qc_info = data_file.get('qc', None)
        st13 = data_file.get('st13', None)

        # data file failed to transform => skip data & images
        if not st13:
            return None

        # data file failed to run QC => skip data & images
        #if qc_info == '__FAIL__':
        #    return None

        # a copy record for dynamodb
        dydb_copy = {'st13': st13,
                     'run_id': self.run_id,
                     'archive':archive_name,
                     'gbd_collection': self.collection,
                     'gbd_type': self.pipeline_type,
                     'office_extraction_date': office_extraction_date,
                     'gbd_extraction_date': gbd_extraction_date,
                     'biblio': os.path.basename(data_info.get('ori'))}

        for img in img_info:
            # failed to transform => skip
            if not img.get('high', None):
                continue

            # add img name to dynamodb copy
            dydb_copy.setdefault('logo', [])
            dydb_copy['logo'].append(os.path.basename(img.get('ori')))
        # saving the copy
        key = "%s_%s_%s" % (self.collection, st13, office_extraction_date)
        dydb_docs_copies_tbl = CachedCopy(self.output_dir, key, document=dydb_copy)
        dydb_docs_copies_tbl.save_db_documnet([key])
