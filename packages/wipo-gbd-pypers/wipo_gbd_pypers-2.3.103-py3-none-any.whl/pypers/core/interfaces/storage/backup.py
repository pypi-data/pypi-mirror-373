import os
import json
import shutil
import time
from . import get_storage
from pypers.utils.utils import appnum_to_subdirs
import subprocess
from pypers.core.interfaces import db

from pypers.core.interfaces.config.pypers_storage import ARCHIVES_BUCKET, RAW_DOCUMENTS, \
    RAW_IMAGES_BUCKET, GBD_DOCUMENTS, IMAGES_BUCKET, IDX_BUCKET


"""
Back up utility for gbd-assets
"""
class Backup:
    def __init__(self, location_fofn, pipeline_type, collection):
        self.location = location_fofn
        self.pipeline_type = pipeline_type
        self.collection = collection
        self.file_list = []
        self.storage = get_storage()


    def run_upload_command(self):
        if os.environ.get('GBD_STORAGE', 'S3') != 'S3':
            return
        fofn_name = os.path.join(self.location, '%s_%s_%s' % (self.pipeline_type, self.collection, time.time()))

        with open('%s.fofn' % fofn_name, 'w') as f:
            files_to_wirte = '\n'.join([' '.join(x[:-1]) for x in self.file_list])
            f.write(files_to_wirte)
        jar_file = os.environ.get('IMAGEANALYSIS_JAR').strip()
        region = os.environ.get('AWS_DEFAULT_REGION', '').strip()
        if os.environ.get("GITHUB_TOKEN", None):
            return
        cmd = "java -jar %s up --region %s --fofn %s"
        cmd = cmd % (jar_file,
                     region,
                     '%s.fofn' % fofn_name)
        proc = subprocess.Popen(cmd.split(' '),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                close_fds=True)
        stdout, stderr = proc.communicate()
        rc = proc.returncode

        if rc != 0:
            db.get_db_error().send_error(self.location,
                                         self.collection,
                                         {'source': 's3_uploader'},
                                         "%s %s" % (str(stdout), str(stderr)))
            raise Exception("S3 upload failed")
        output_name = '%s.fofn.done' % fofn_name
        if not os.path.exists(output_name):
            return
        with open(output_name, 'r') as f:
            done_items = f.read().split('\n')
        for el in self.file_list:
            if el[0] in done_items and el[-1] is True:
                try:
                    os.remove(el[0])
                except:
                    pass

    # hard => store and delete
    def _do_store(self, ori_file, bucket_name, bucket_path, hard, new_name=None):
        #/root/workspace/classes_references/vienna/v9.en.xml gbd-assets-idx-files-eu-central-1-161581150093 test/vienna/v9.en.xml
        #ori_file  bucket_name bucket_path hard
        if not os.path.exists(ori_file):
            return False
        _, file_name = os.path.split(ori_file)
        if new_name:
            name, ext = os.path.splitext(file_name)
            file_name = '%s%s' % (new_name, ext)

        # set the location for storage
        bucket_file = os.path.join(bucket_path, file_name)
        self.file_list.append([ori_file, bucket_name, bucket_file, hard])
        return True

    # ori data files go into STORAGE_DOCS_GBD/type/collection/archive/st13.ext
    def store_doc_ori(self, ori_file, archive_name, st13, hard=False):
        bucket_name = RAW_DOCUMENTS
        bucket_path = os.path.join(self.pipeline_type,
                                   self.collection,
                                   archive_name)

        return self._do_store(ori_file, bucket_name, bucket_path, hard, new_name=st13)

    # ori img files go into STORAGE_IMGS_ORI/type/collection/st13/crc.ext
    def store_img_ori(self, ori_file, st13, crc, hard=False):
        bucket_name = RAW_IMAGES_BUCKET
        bucket_path = os.path.join(self.pipeline_type,
                                   self.collection,
                                   st13)
        return self._do_store(ori_file, bucket_name, bucket_path, hard, new_name=crc)

    # gbd data files go into STORAGE_DATA_GBD/type/collection/st13/run_id.json
    def store_doc_gbd(self, gbd_file, st13, hard=False):
        bucket_name = GBD_DOCUMENTS
        bucket_path = os.path.join(self.pipeline_type,
                                   self.collection,
                                   st13)
        local_backup = os.path.join(os.environ.get('GBDFILES_DIR', '/data/'),
                                    self.pipeline_type,
                                    self.collection,
                                    appnum_to_subdirs(st13),
                                    st13)
        if os.path.exists(gbd_file):
            os.makedirs(local_backup, exist_ok=True)
            shutil.copy(gbd_file, os.path.join(local_backup, os.path.basename(gbd_file)))
        if self._do_store(gbd_file, bucket_name, bucket_path, hard):
            return os.path.join(local_backup, os.path.basename(gbd_file))
        return None


    # gbd img files go into STORAGE_IMGS_GBD/type/collection/st13/run_id.json
    def store_img_gbd(self, img_file, st13, hard=False):
        bucket_name = IMAGES_BUCKET
        bucket_path = os.path.join(self.pipeline_type,
                                   self.collection,
                                   st13)

        return self._do_store(img_file, bucket_name, bucket_path, hard)

    # ori img files go into STORAGE_IMGS_ORI/type/collection/archive.zip
    def store_archive(self, archive, hard=False):
        bucket_name = ARCHIVES_BUCKET
        bucket_path = os.path.join(self.pipeline_type,
                                   self.collection)

        return self._do_store(archive, bucket_name, bucket_path, hard)


    # idx files go into STORAGE_DATA_IDX/type/collection/st13/idx.json
    def store_doc_idx(self, idx_file, st13, hard=False):
        bucket_name = IDX_BUCKET
        bucket_path = os.path.join(self.pipeline_type,
                                   self.collection,
                                   st13)
        return self._do_store(idx_file, bucket_name, bucket_path, hard)

