from pypers.steps.base.step_generic import EmptyStep
from .data_handler import GBDFormat
from .img_handler import GBDImage
from .dyncopy_handler import DynCopy
from .dynlive_handler import DynLive
from .analyze_handler import Analyze
from pypers.core.interfaces import db

from pypers.core.interfaces.storage.backup import Backup
import json
import os


class ETLProcess(EmptyStep):
    """
    Process manifests file files into subdirectories.
    Rename files and logos to appnum
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ],
        "args":
        {
            "inputs": [
                {
                    "name": "manifest",
                    "descr": "the manifest list",
                    "iterable": True
                }
            ],
            "outputs": [
                {
                    "name": "idx_files",
                    "descr": "the extracted data GBD FILES organized by appnum"
                },
                {
                    "name": "extraction_dir",
                    "descr": "the extracted dir"
                }
            ]
        }
    }

    # self.manifest ORIFILES_DIR/run_id/type/collection/office_extraction_date/archive_name/manifest.json
    def process(self):
        #collection = self.collection.replace('_harmonize', '')
        collection = self.collection
        ind = self.collection.find("_")
        if ind != -1:
            collection = self.collection[:ind]

        self.extraction_dir = os.path.dirname(self.manifest)
        self.backup_processor = Backup(self.output_dir, self.pipeline_type, collection)

        params = {
            'collection': collection,
            'pipeline_type':self.pipeline_type,
            'extraction_dir': self.extraction_dir,
            'run_id': self.run_id,
            'output_dir': self.output_dir,
            'logger': self.logger,
            'backup_handler': self.backup_processor
        }

        self.processors = [GBDFormat(**params), GBDImage(**params), DynCopy(**params), DynLive(**params)]
        #self.indexer = IdxTransform(**params)
        with open(self.manifest, 'r') as f:
            manifest_data = json.load(f)
        data_files = self._filter_missing_files(manifest_data.get('files', {}))
        appnum_files_flat = [(data, appnum) for appnum, data in data_files.items()]
        idx_paths = []
        for entry in self.worker_parallel(appnum_files_flat, self._pre_process_record):
            if not entry[0]:
                self.logger.error("Preprocess for %s failed" % entry[1])
        analyzer = Analyze(**params)
        analyzer.analyze(appnum_files_flat)
        self.backup_processor.run_upload_command()

        for item in appnum_files_flat:
            data_file, appnum = item
            #res = data_file.get('doc', {}).get('local_path_gbd', None)
            res = data_file.get('gbd')

            if res:
                record = data_file.get('doc', {})
                dyn_live_path = os.path.join(self.output_dir, '%s.dyn' % appnum)
                with open(dyn_live_path, 'w') as f:
                    f.write(json.dumps(record['data_files']['latest']))
                try:
                    if 'data' in data_file.keys():
                        os.remove(os.path.join(self.extraction_dir, data_file['data']['ori']))
                    if 'imgs' in data_file.keys():
                        for logo in data_file['imgs']:
                            if not logo.get('ori', None):
                                continue
                            os.remove(os.path.join(self.extraction_dir, logo['ori']))
                except:
                    # Just cleanup, not throwing any errors.
                    pass
                # WARNING: These are now GBD files. Not renaming due to huge impact on pipelines
                idx_paths.append({'gbd': res, 'dyn_live': dyn_live_path })
        self.idx_files = [idx_paths]
        self.extraction_dir = [self.extraction_dir]

    def _pre_process_record(self, item):
        data_file, appnum = item
        try:
            for processor in self.processors:
                getattr(processor, 'process')(data_file, appnum)
        except Exception as e:
            self.logger.error('Failed to process %s' % appnum)
            self.logger.error(e)
            return (False, appnum)
        return (True, appnum)

    def _process_record(self, item):
        data_file, appnum = item
        try:
            getattr(self.indexer, 'process')(data_file, appnum)
            res = data_file.get('doc', {}).get('idx', None)
        except Exception as e:
            self.logger.error('Failed to process %s' % appnum)
            res = None
        if res:
            try:
                if 'data' in data_file.keys():
                    os.remove(os.path.join(self.extraction_dir, data_file['data']['ori']))
                if 'imgs' in data_file.keys():
                    for logo in data_file['imgs']:
                        if not logo.get('ori', None):
                            continue
                        os.remove(os.path.join(self.extraction_dir, logo['ori']))
            except:
                # Just cleanup, not throwing any errors.
                pass
        return res

    def _file_exists(self, file):
        file_path = os.path.join(self.extraction_dir, file)
        return os.path.exists(file_path)

    def _filter_missing_files(self, unfiltered):
        filtered = {}
        for key, item in unfiltered.items():
            item_present = True
            if 'data' in item.keys():
                item_present = item_present and self._file_exists(item['data']['ori'])
            if 'imgs' in item.keys():
                for logo in item['imgs']:
                    if not logo.get('ori', None):
                        continue
                    item_present = item_present and self._file_exists(logo['ori'])
            if item_present:
                filtered[key] = item
        return filtered



