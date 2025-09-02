import os
import subprocess
from pypers.core.interfaces.storage.backup import Backup
from pypers.core.interfaces import db
from pypers.utils.utils import clean_folder, delete_files
from pypers.steps.base.step_generic import EmptyStep
#from pypers.utils.package_explorer import write_masks_to_json
from pypers.core.interfaces.config.pypers_storage import GBD_DOCUMENTS, IDX_BUCKET, IMAGES_BUCKET
from .index import Index

class RefreshIndex(Index):
    """
    Index / Backup / DyDb publish
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ],
        "args":
        {
            'inputs': [
                {
                    'name': 'idx_files',
                    'descr': 'files to be indexed',
                },
                {
                    'name': 'extraction_dir',
                    'descr': 'files to be indexed',
                },

            ],
            'outputs': [
                {
                    'name': 'flag',
                    'descr': 'flag for done'
                }
            ]
        }
    }

    # "files" : {
    #     "st13" : {
    #         "idx" : "000/st13/idx.json",
    #         "latest" : "000/st13/latest.json"
    #     },
    #     ...
    # }
    def process(self):
        region = os.environ.get('AWS_DEFAULT_REGION', 'eu-central-1')
        if not len(self.idx_files):
            return
        #self.collection_name = self.collection.replace('_harmonize', '')
        self.collection_name = self.collection
        ind = self.collection.find("_")
        if ind != -1:
            self.collection_name = self.collection[:ind]

        self.backup = Backup(self.output_dir, self.pipeline_type, self.collection_name)

        st13s = {}
        # rewrite paths to absolute paths
        # Make sure to get st13 here and after upload to s3/ local disc + dyndb.
        for archive in self.idx_files:
            st13s.update({os.path.basename(os.path.dirname(record['gbd'])): {
                'gbd':record['gbd'],
                'dyn_live': record['dyn_live']}
            for record in archive})
        live_documents = []
        for st13 in st13s.keys():
            gbd_file = st13s[st13]['gbd']
            local_path = self.backup.store_doc_gbd(gbd_file, st13, hard=True)
            st13s[st13]['local_gbd'] = local_path
            live_documents.append(st13s[st13]['dyn_live'])
        self.backup.run_upload_command()

        db.get_pre_prod_db().put_items(live_documents)

        for folder in self.extraction_dir:
            clean_folder(folder)

    def postprocess(self):
        self.flag = [1]
