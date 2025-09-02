from os.path import realpath, dirname
from pypers import import_all

class BaseHandler(object):

    def __init__(self,
                 collection=None,
                 pipeline_type=None,
                 run_id=None,
                 extraction_dir=None,
                 output_dir=None,
                 backup_handler=None,
                 logger=None):
        self.output_dir = output_dir
        self.pipeline_type = pipeline_type
        self.collection = collection
        self.extraction_dir = extraction_dir
        self.run_id = run_id
        self.backup = backup_handler
        self.logger = logger
        self.conf = None
        self.custom_init()


    def custom_init(self):
        pass

    def process(self, data_file, appnum):
        raise NotImplemented

# Import all Steps in this directory.
import_all(namespace=globals(), dir=dirname(realpath(__file__)))

