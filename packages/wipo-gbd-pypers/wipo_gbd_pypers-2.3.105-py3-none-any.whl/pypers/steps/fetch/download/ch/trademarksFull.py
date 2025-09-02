import os
import shutil
import datetime
from requests.auth import HTTPBasicAuth
import os
import io
import json
import argparse
import time
import ntpath
import requests
from pathlib import Path
import yaml
from lxml import etree
from lxml.etree import fromstring
import uuid
import datetime
from pypers.steps.base.fetch_step_api import FetchStepAPI

import logging
import logging.handlers 

#get here pypers logging 
#import urllib3
#urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#logging.getLogger("urllib3").setLevel(logging.ERROR)

from . import get_auth_token

class TrademarksFull(FetchStepAPI):
    spec = {
        "version": "2.0",
        "descr": [
            "Fetch full update using REST API"
        ],
    }

    archive_size = 1000

    token = None

    def get_connections_info(self):
        return None, None

    def daterange(self, start_date, end_date):
        days = int((end_date - start_date).days)
        for n in range(days):
            yield start_date + datetime.timedelta(n+1)

    def get_intervals(self):
        """ 
        Return the intervals to be downloaded, in our case one interval is 30 days, so
        we enumerate approx. months from the month of the last update. In addition, as it is a full
        update, the starting date corresponds to the oldest available trademark application.
        """
        # get the date of the last update
        if not len(self.done_archives):
            # no done archives in dynamodb table gbd_pypers_done_archive 
            last_update = datetime.datetime.fromisoformat("1947-01-01")
            # to indicate a recent date for test, just update and uncomment below
            #last_update = datetime.datetime.fromisoformat("2024-01-19")
        else:
            # we get the day of the last update from the last "done_archive" file name stored 
            # in dynamodb table gbd_pypers_done_archive 
            # # expecting names like : 2018-01-01.TO.2018-01-31.1.txt
            last_update = sorted(self.done_archives)[-1].split('.')[2]
            if '_' in last_update:
                last_update = last_update.split('_')[0]
            last_update = datetime.datetime.fromisoformat(last_update)

        today = datetime.datetime.today()

        result = []
        current_date = last_update.strftime("%Y-%m-%d")

        addDays = datetime.timedelta(days=30)
        addDay = datetime.timedelta(days=1)
        one_date = last_update
        while one_date <= today:
            one_first_date = one_date + addDay
            current_date = one_first_date.strftime("%Y-%m-%d")
            one_second_date = one_date + addDays
            next_date = one_second_date.strftime("%Y-%m-%d")
            result.append( (current_date, next_date) )
            one_date = one_second_date
            current_date = next_date
        print(result)
        return result

    template_update = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" \
        "<ApiRequest xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"urn:ige:schema:xsd:datadeliverycore-1.0.0 urn:publicid:-:IGE:XSD+DATADELIVERYCORE+1.0.0:EN " \
        "urn:ige:schema:xsd:datadeliverycommon-1.0.0 urn:publicid:-:IGE:XSD+DATADELIVERYCOMMON+1.0.0:EN urn:ige:schema:xsd:datadeliverytrademark-1.0.0 urn:publicid:-:IGE:XSD+DATADELIVERYTRADEMARK+1.0.0:EN\" " \
        "xmlns=\"urn:ige:schema:xsd:datadeliverycore-1.0.0\" xmlns:tm=\"urn:ige:schema:xsd:datadeliverytrademark-1.0.0\">" \
        "<Action type=\"TrademarkSearch\">" \
        "<tm:TrademarkSearchRequest xmlns=\"urn:ige:schema:xsd:datadeliverycommon-1.0.0\">" \
            "<Representation details=\"Maximal\" image=\"Embed\"/>" \
            "<Query>" \
            "    <tm:ApplicationDate from=\"{{$start_date}}\" includeFrom=\"true\" to=\"{{$end_date}}\" includeTo=\"false\"></tm:ApplicationDate>" \
            "</Query>" \
            "<Sort>" \
            "    <LastUpdateSort>Ascending</LastUpdateSort>" \
            "</Sort>" \
        "</tm:TrademarkSearchRequest>" \
        "</Action>" \
        "</ApiRequest>"

    def lazy_get_auth_token(self, force=False):
        if self.token == None or force:
            self.token = get_auth_token(self.conn_params)
        return self.token

    def specific_api_process(self, session):
        self.api_url = "https://"+self.conn_params["apiHost"]+"/public/api/v1"

        if self.intervals is None:
            return

        # we maintain the size of individual archives to a stable number of records, typically 1000,
        # due to the strong variability of records per intervals over time
        current_chunks = []
        start_period = None
        index = 0

        for interval in self.intervals:
            print("download interval:", interval)
            chunks = self.trademark_update(interval[0], interval[1])
            print("total for interval", str(len(chunks)), "json chunks")

            self.logger.info('%s-%s: %d applications found' % (interval[0], interval[1], len(chunks)))

            if start_period == None:
                start_period = interval[0]

            if len(current_chunks) + len(chunks) < self.archive_size:
                current_chunks.extend(chunks)
            else:
                gap = self.archive_size - len(current_chunks)
                current_chunks.extend(chunks[:gap])

                # write output file with these chunks 
                output_chunk_file =  os.path.join(self.output_dir, 
                    '%s.TO.%s_%s.xml' % (start_period, interval[1], index))
                start_period = interval[1]
                index += 1

                print("output_chunk_file:", output_chunk_file)

                with open(output_chunk_file, 'w') as fh:
                    fh.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
                    fh.write("<trademarkBag>\n")
                    for current_chunk in current_chunks:
                        fh.write(etree.tostring(current_chunk, pretty_print=True).decode("utf-8"))
                    fh.write("</trademarkBag>")

                self.output_files.append(output_chunk_file)
                print(output_chunk_file, "written")

                current_chunks = chunks[gap:]

        # remaining chunks
        if len(current_chunks)>0:
            output_chunk_file =  os.path.join(self.output_dir, 
                    '%s.TO.%s_%s.xml' % (start_period, interval[1], index))

            with open(output_chunk_file, 'w') as fh:
                    fh.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
                    fh.write("<trademarkBag>\n")
                    for current_chunk in current_chunks:
                        fh.write(etree.tostring(current_chunk, pretty_print=True).decode("utf-8"))
                    fh.write("</trademarkBag>")

            self.output_files.append(output_chunk_file)
            print("last archive:" + output_chunk_file, "written")

        #raise Exception("HERE")

