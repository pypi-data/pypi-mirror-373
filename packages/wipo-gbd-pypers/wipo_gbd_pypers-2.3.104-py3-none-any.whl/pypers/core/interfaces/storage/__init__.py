from .s3 import S3Storage
from .filesystem import FSStorage
import os
import boto3
import botocore
import boto3.s3.transfer as s3transfer
from pypers.core.interfaces.storage.test import MockS3
import json
import queue
from threading import Thread

_storage = None
s3_uploader = None


def get_storage():
    global _storage
    global s3_uploader
    if _storage:
        return _storage
    if os.environ.get('GBD_STORAGE', 'S3') != 'S3':
        _storage = FSStorage()
    else:
        #s3_uploader = S3FastUploader()
        _storage = S3Storage()
    return _storage


class S3FastUploader:
    """S3 manager"""

    def __init__(self):
        workers = 20
        if os.environ.get("S3_URL", None):
            endpoint_url = os.environ['S3_URL']
        else:
            endpoint_url = None
        if os.environ.get("GITHUB_TOKEN", None):
            self.s3 = MockS3()
            self.s3client = MockS3()
            self.transfer_config = ''

        else:
            self.session = boto3.Session()
            self.s3 = boto3.client('s3', endpoint_url=endpoint_url)
            self.botocore_config = botocore.config.Config(max_pool_connections=workers)
            self.s3client = self.session.client('s3', endpoint_url=endpoint_url, config=self.botocore_config)
            self.transfer_config = s3transfer.TransferConfig(
                use_threads=True,
                max_concurrency=workers,
            )
        self.enclosure_queue = queue.Queue()
        worker = Thread(target=self.fast_upload, args=(self.enclosure_queue,))
        worker.setDaemon(True)
        worker.start()
        self.enclosure_queue.join()

    def fast_upload(self, q):
        if os.environ.get("GITHUB_TOKEN", None):
            return
        s3t = s3transfer.S3Transfer(client=self.s3client, config=self.transfer_config)
        while True:
            raw_data = q.get()
            bucket_name = raw_data.get('bucket_name')
            src = raw_data.get('src')
            dst = raw_data.get('dst')
            to_del = raw_data.get('delete')
            s3t.upload_file(
                src, bucket_name, dst,
            )
            if to_del:
                try:
                    os.remove(src)
                except:
                    pass
            q.task_done()
        s3t.shutdown()
