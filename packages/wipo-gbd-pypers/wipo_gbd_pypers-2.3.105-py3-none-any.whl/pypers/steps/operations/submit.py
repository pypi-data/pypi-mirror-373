import datetime
import os
import time
import requests
from pypers.steps.base.step_generic import EmptyStep
from pypers.core.interfaces.db import get_cron_db, get_operation_db, get_db
from pypers.core.interfaces import msgbus
import boto3
from pypers.utils import utils as ut


class Submit(EmptyStep):
    """
    Triggers the fetch pipelines based on the db conf. Monitors the execution of them.
    Once all the triggered pipelines are done, it sends the publish message.

    There is a maximum of 10 hours to complete all the triggered pipelines, which can be 
    changed manually in the check_still_running() method. However, longer pipeline should
    rather be managed outside daily operations. 
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Triggers the fetch pipelines based on the db conf. "
            "Monitors the execution of them. Once all the triggered "
            "pipelines are done, it sends the publish message"
        ],

    }

    def get_scheduled_tasks(self):
        db_config = get_cron_db().read_config(self.pipeline_type)
        current_day = datetime.datetime.today().strftime('%w')
        to_return = []
        for collection in db_config.keys():
            if db_config[collection][int(current_day)] == '1':
                to_return.append(collection)
        return to_return

    def check_still_running(self):

        for coll in get_operation_db().get_run(self.run_id):
            max_start = datetime.datetime.now() - datetime.timedelta(hours=10)
            max_start = max_start.strftime('%Y-%m-%d %H:%M:%S.%f')
            start_time =  coll.get('start_time', None)
            if coll.get('pipeline_status', None) == 'RUNNING':
                res = get_db().step_config.has_step_blocked(self.run_id,  coll['collection'])
                if res:
                    output_dir = os.path.join(os.environ['WORK_DIR'],
                                              self.run_id,
                                              self.pipeline_type,
                                              coll['collection'])
                    msgbus.get_msg_bus().send_message(
                        self.run_id,
                        collection=res,
                        type=self.pipeline_type,
                        custom_config=['pipeline.output_dir=%s' % output_dir,
                                       'pipeline.is_operation=True',
                                       'steps.clean.chain=1'])
                if start_time and max_start > start_time:
                    # Fail the pipeline
                    get_operation_db().completed(
                        self.run_id,
                        coll.get('collection', None),
                        success=False)
                    continue
                return True
        return False


    def process(self):
        cron_tab = self.get_scheduled_tasks()
        # Create the monitoring
        get_operation_db().create_run(self.run_id, cron_tab)
        # Trigger the messages
        batch_size = 20
        counter = 0
        for collection in cron_tab:
            output_dir = os.path.join(os.environ['WORK_DIR'],
                                      self.run_id,
                                      self.pipeline_type,
                                      collection)
            msgbus.get_msg_bus().send_message(
                self.run_id,
                collection=collection,
                type=self.pipeline_type,
                custom_config=['pipeline.output_dir=%s' % output_dir,
                               'pipeline.is_operation=True',
                               'steps.clean.chain=1'])
            counter += 1
            if counter == batch_size:
                counter = 0
                time.sleep(60 * 5) # sleep 10 minutes

        # Loop for endings
        while self.check_still_running():
            self.logger.debug("Just check for pipeline ending. Still working..")
            time.sleep(60)
        if not self.pipeline_type == 'commons':
            suffix = '' if self.pipeline_type == 'brands' else '_GDD'
            solr = os.environ.get('SLRW_URL%s' % suffix)

            # Trigger publish
            url = "%s/admin/cores?action=backup_and_release&target=%s&name=%s&repository=s3" % (
                solr,
                self.pipeline_type,
                self.run_id
            )
            result = requests.get(url)
            if result.status_code != requests.codes.ok:
                self.logger.error("%s failed with %s" % (url, result.status_code))
                result.raise_for_status()

        # Email results
        results = get_operation_db().get_run(self.run_id)

        default_recpients = os.environ.get(
            "DEFAULT_RECIPIENTS", 'nicolas.hoibian@wipo.int,patrice.lopez@wipo.int').split(',')

        recipients = list(set(default_recpients))
        full_report = {
            'type' : self.pipeline_type,
            'counter': len(results),
            'pipelines': []
        }
        for r in results:
            full_report['pipelines'].append(
                {
                    'name': r['collection'],
                    'status': r['pipeline_status']
                }
            )

        subject = "Operation %s type %s is being released" % (
            self.run_id, self.pipeline_type)
        html = ut.template_render(
            'notify_operation_update.html',
            report=full_report)
        ut.send_mail(
            'gbd@wipo.int', recipients, subject, html=html, server=os.environ.get("MAIL_SERVER", None),
            password=os.environ.get("MAIL_PASS", None),
            username=os.environ.get("MAIL_USERNAME", None))
