import os
import shutil
import re
import json

from datetime import datetime

from pypers.steps.base.step_generic import EmptyStep

class Organize(EmptyStep):
    """
    Organize files into subdirectories.
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
                    "descr": "the manifest of extraction",
                    "iterable": True
                }
            ],
            "outputs": [
                {
                    "name": "manifest",
                    "descr": "the manifest after staging json"
                }
            ],
              "params": [
                {
                    "name": "archive_splitter_nb",
                    "type": "int",
                    "descr": "number used to split in multiple archives",
                    "value": 0
                },
                  {
                      "name": "mask_input",
                      "type": "str",
                      "descr": "Mask for appnums to convert to int",
                      "value": "(.*)"
                  }
            ]
        }
    }

    """
    "manifest" : {
      "archive_date" : "2021-08-20",
      "archive_file" : "/path/to/archiveA.zip",
      "archive_name" : "archiveA",
      "data_files" : {
         "appnum" : {
            "ori" : "rel/path/to/data/file.xml"
         },
         ...
      },
      "img_files" : {
         "appnum" : [
            {
               "ori" : "rel/path/to/img/file.jpg"
            }
         ],
         ...
      },
      "extraction_dir" : "/path/to/root/extraction/dir/",
    }
    """

    def organize(self):
        # nothing to do
        if not len(self.manifest['data_files'].keys()):
            return
        archive_date = self.manifest['archive_date']
        archive_name = self.manifest['archive_name']
        archive_file = self.manifest['archive_file']

        # STAGE the original files
        ori_path = os.path.join(os.environ.get('ORIFILES_DIR'), # mandatory ENV VARIABLE - we do not want to make defaults
                                self.run_id,
                                self.pipeline_type,
                                self.collection,
                                archive_date,
                                archive_name)

        os.makedirs(ori_path, exist_ok=True)

        # -- move the data files to ori stage
        for appnum, item in self.manifest['data_files'].items():
            if os.path.exists(os.path.join(self.manifest['extraction_dir'], item.get('ori'))):
                self._move_object(ori_path, item.get('ori'))

        # -- move the image files to ori stage
        for appnum, item in self.manifest['img_files'].items():
            for img in item:
                if os.path.exists(os.path.join(self.manifest['extraction_dir'], img.get('ori', ''))):
                    self._move_object(ori_path, img.get('ori', None))
        # -- create manifest file in ori stage
        manifest = {}
        manifest['files'] = {}
        for key in self.manifest['data_files'].keys():
            if key not in manifest['files']:
                manifest['files'][key] = {}
            manifest['files'][key]['data'] = self.manifest['data_files'][key]
        for key in self.manifest['img_files'].keys():
            if key not in manifest['files']:
                manifest['files'][key] = {}
            manifest['files'][key]['imgs'] = self.manifest['img_files'][key]
        for key in manifest['files'].keys():
            manifest['files'][key].update({
                'gbd_extraction_date': datetime.now().strftime('%Y-%m-%d'),
                'archive_date' : self.manifest['archive_date'],
                'archive_name' : self.manifest['archive_name'],
                'archive_file' : self.manifest['archive_file'],
            })

        self.manifest = os.path.join(ori_path, 'manifest.json')

        with open(self.manifest, 'w') as f:
            json.dump(manifest, f, indent=2)

        self.manifest = [self.manifest]

    def key_processer(self, key):
        r = re.compile(self.mask_input)
        key = ''.join([x for x in r.match(key).groups()])
        return int(key) % self.archive_splitter_nb

    def organize_in_multiple(self):
        # nothing to do
        if not len(self.manifest['data_files'].keys()):
            return
        archive_date = self.manifest['archive_date']
        archive_name = self.manifest['archive_name']
        archive_file = self.manifest['archive_file']

        # STAGE the original files
        ori_gen_path = os.path.join(os.environ.get('ORIFILES_DIR'),
                                    # mandatory ENV VARIABLE - we do not want to make defaults
                                    self.run_id,
                                    self.pipeline_type,
                                    self.collection,
                                    archive_date,
                                    "%s_%s" % (archive_name, "%s"))
        manifests = []
        for i in range(0, self.archive_splitter_nb):
            os.makedirs(ori_gen_path % i, exist_ok=True)
            manifests.append({'files': {}})

        # -- move the data files to ori stage
        for appnum, item in self.manifest['data_files'].items():
            ori_path = ori_gen_path % self.key_processer(appnum)
            if os.path.exists(os.path.join(self.manifest['extraction_dir'], item.get('ori'))):
                self._move_object(ori_path, item.get('ori'))

        # -- move the image files to ori stage
        for appnum, item in self.manifest['img_files'].items():
            for img in item:
                ori_path = ori_gen_path % self.key_processer(appnum)
                if os.path.exists(os.path.join(self.manifest['extraction_dir'], img.get('ori', ''))):
                    self._move_object(ori_path, img.get('ori', None))
        # -- create manifest file in ori stage

        for key in self.manifest['data_files'].keys():
            manifest = manifests[self.key_processer(key)]
            if key not in manifest['files']:
                manifest['files'][key] = {}
            manifest['files'][key]['data'] = self.manifest['data_files'][key]
        for key in self.manifest['img_files'].keys():
            manifest = manifests[self.key_processer(key)]
            if key not in manifest['files']:
                manifest['files'][key] = {}
            manifest['files'][key]['imgs'] = self.manifest['img_files'][key]
        for i in range(0, self.archive_splitter_nb):
            manifest = manifests[i]
            for key in manifest['files'].keys():
                manifest['files'][key].update({
                    'gbd_extraction_date': datetime.now().strftime('%Y-%m-%d'),
                    'archive_date': self.manifest['archive_date'],
                    'archive_name': self.manifest['archive_name'],
                    'archive_file': self.manifest['archive_file'],
                })
            ori_path = ori_gen_path % i
            tmp = os.path.join(ori_path, 'manifest.json')
            with open(tmp, 'w') as f:
                json.dump(manifest, f, indent=2)
        self.manifest = []
        for i in range(0, self.archive_splitter_nb):
            ori_path = ori_gen_path % i
            self.manifest.append(os.path.join(ori_path, 'manifest.json'))

    def process(self):
        if self.archive_splitter_nb == 0:
            self.organize()
        else:
            self.organize_in_multiple()

    def _move_object(self, write_root, file):
        if not file:
            return

        src_file = os.path.join(self.manifest['extraction_dir'], file)
        dest_file = os.path.join(write_root, file)

        dest_dir = os.path.dirname(dest_file)
        os.makedirs(dest_dir, exist_ok=True)
        shutil.move(src_file, dest_file)

