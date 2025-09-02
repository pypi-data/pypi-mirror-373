import os

from pypers.utils import utils as ut
from pypers.core.interfaces.db import get_operation_db, get_done_file_manager, get_db_config
import json
from pypers.steps.base.step_generic import EmptyStep
from pypers.utils.utils import clean_folder, delete_files


class Notify(EmptyStep):

    spec = {
        "version": "2.0",
        "descr": [
            "Notifies by email about the update"
        ],
        "args":
        {
            "inputs": [
                {
                    "name": "flag",
                    "descr": "flag that index is done",
                },
                {
                    "name": "manifest",
                    "descr": "the manifest list",
                }
            ],
            "params": [
                {
                    "name": "reply_to",
                    "descr": "email sender",
                    "value": "gbd@wipo.int"
                }
            ]
        }
    }

    def process(self):
        #self.collection_name = self.collection.replace('_harmonize', '')
        self.collection_name = self.collection
        ind = self.collection.find("_")
        if ind != -1:
            self.collection_name = self.collection[:ind]

        if self.is_operation:
            if 'em' in self.collection_name:
                get_operation_db().completed(self.run_id, 'emap')
            else:
                get_operation_db().completed(self.run_id, self.collection_name)
        for manifest in self.manifest:
            with open(manifest, 'r') as f:
                manifest_data = json.load(f).get('done_archives', {})
            if manifest_data:
                processed_paths = manifest_data['archives']
                should_reset = manifest_data['should_reset']
                get_done_file_manager().update_done(self.collection_name, self.run_id,
                                                    processed_paths,
                                                    should_reset=should_reset)
                break
        default_recpients = os.environ.get(
            "DEFAULT_RECIPIENTS", 'nicolas.hoibian@wipo.int,patrice.lopez@wipo.int').split(',')

        recipients = list(set(default_recpients + get_db_config().get_email(self.collection_name)))
        # Report
        report = {}
        total_makrs = 0
        
        total_imgs = 0
        for manifest in self.manifest:
            with open(manifest, 'r') as f:
                m_data = json.load(f)
            for appnum in m_data.get('files', {}).keys():
                item = m_data['files'][appnum]
                archive_name = os.path.basename(item.get('archive_file'))
                if not report.get(archive_name, None):
                    report[archive_name] = {
                        'marks': 0,
                        'images': 0
                    }
                if item.get('data', {}).get('ori', {}) and not os.path.exists(item['data']['ori']):
                    report[archive_name]['marks'] += 1
                    total_makrs += 1
                for img in item.get('imgs', []):
                    if img.get('ori', {}) and not os.path.exists(img['ori']):
                        report[archive_name]['images'] += 1
                        total_imgs += 1

        full_report = {
            'marks': total_makrs,
            'images': total_imgs,
            'archive': report,
            'archives': report.keys(),
        }
        if full_report and full_report['marks'] != 0:
            collection =  self.collection_name
            collection_type = self.pipeline_type

            subject = "%s %s data update in WIPO's Global %s Database" % (
                collection.upper()[0:2], collection.upper()[2:4],
                self.pipeline_type)
            html = ut.template_render(
                'notify_%s_update.html' % collection_type,
                report=full_report)
            ut.send_mail(
                self.reply_to, recipients, subject, html=html, server=os.environ.get("MAIL_SERVER", None),
                password=os.environ.get("MAIL_PASS", None),
                username=os.environ.get("MAIL_USERNAME", None))

        pipeline_dir = self.meta['pipeline']['output_dir']
        delete_files(pipeline_dir, patterns=['.*json'])
        clean_folder(pipeline_dir)
