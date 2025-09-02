import os
from pypers.core.interfaces import msgbus
from pypers.utils.utils import delete_files, clean_folder
from pypers.steps.fetch.common.cleanup import Cleanup as BaseCleanup
from pypers.core.interfaces.db import get_done_file_manager


class CleanupAP(BaseCleanup):

    def postprocess(self):
        output_dir = os.path.join(os.environ['WORK_DIR'],
                                  self.run_id,
                                  self.pipeline_type,
                                  self.collection)
        should_reset = self.reset_done != 0
        processed_paths = [
            p[p.find('/0/') + len('/0/'):]
            for p in self.processed_list]
        get_done_file_manager().update_done(self.collection, self.run_id,
                                            processed_paths,
                                            should_reset=should_reset)
        #if int(self.chain):
        force_restart = self.meta['pipeline'].get('force_restart', 'False')
        msgbus.get_msg_bus().send_message(self.run_id,
                                          type='commons',
                                          collection="emrp",
                                          custom_config=['pipeline.output_dir=%s' % output_dir,
                                                         'pipeline.forced_restarted=%s' % force_restart,
                                                         'pipeline.is_operation=%s' % self.is_operation,
                                                         'steps.clean.chain=1'])
        pipeline_dir = self.meta['pipeline']['output_dir']
        delete_files(pipeline_dir, patterns=['.*_output.json', '.*_input.json'])
        clean_folder(pipeline_dir)
