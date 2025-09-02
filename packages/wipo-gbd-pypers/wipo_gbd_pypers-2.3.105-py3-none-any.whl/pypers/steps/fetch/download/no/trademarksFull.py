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
#import requests
import http.client
from pathlib import Path
import yaml
import uuid
import datetime
from pypers.steps.base.fetch_step_api import FetchStepAPI

import logging
import logging.handlers 

#get here pypers logging 
#import urllib3
#urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#logging.getLogger("urllib3").setLevel(logging.ERROR)

class TrademarksFull(FetchStepAPI):
    spec = {
        "version": "2.0",
        "descr": [
            "Fetch full update using REST API"
        ],
    }

    archive_size = 1000

    token = None
    page_size = 200

    def get_connections_info(self):
        return None, None

    def get_intervals(self):
        """ 
        Return the intervals to be downloaded, in our case one interval is 30 days, so
        we enumerate approx. months from the month of the last update. In addition, as it is a full
        update, the starting date corresponds to the oldest available trademark application.
        """
        # get the date of the last update
        if not len(self.done_archives):
            # no done archives in dynamodb table gbd_pypers_done_archive 
            last_update = datetime.datetime.fromisoformat("1885-01-01")
            # to indicate a recent date for UAT, update and uncomment below
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

    def trademark_update(self, start_date, end_date):
        json_chunks = []
        header = {
            "Ocp-Apim-Subscription-Key": self.token,
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }

        # slice api url for http.client
        host = self.api_url.replace("https://", "")
        pos = host.find("/")
        if pos != -1:
            url_path = host[pos:]
            host = host[:pos]
        else:
            self.logger.warning("Suspicious API URL: ", self.api_url)
            url_path = "/"

        page_number = 0
        totalHitsCount = -1
        currentHitsCount = 0
        while page_number != -1:
            conn = http.client.HTTPSConnection(host)
            payload = json.dumps({
                "applicationDateFrom": start_date,
                "applicationDateTo": end_date,
                "pageSize": self.page_size,
                "pageNumber": page_number
            })

            conn.request("POST", url_path, payload, header)
            res = conn.getresponse()
            data = res.read()
            response = data.decode("utf-8")
            response = json.loads(response)

            if res.status == 200:
                result = { "json": response }
                totalHitsCount = response["totalHitsCount"]
            else:
                result = { "error": response.content }
                page_number = -1

            if "error" not in result and "json" in result:
                local_json_chunks = result["json"]["results"]
                if local_json_chunks != None and len(local_json_chunks)>0:
                    for local_json_chunk in local_json_chunks:
                        json_chunks.append(local_json_chunk["trademarkApplication"])
                    
                    # double check for pagination for safety
                    if len(local_json_chunks) == self.page_size or currentHitsCount < totalHitsCount:
                        page_number += 1
                        currentHitsCount += len(local_json_chunks)
                    else:
                        page_number = -1
                else:
                    page_number = -1
            else:
                page_number = -1

        return json_chunks

    def specific_api_process(self, session):
        self.api_url = "https://"+self.conn_params["base_url"]+"/Trademark/v1/search/json"
        self.token = self.conn_params["credentials"]["key"]

        if self.intervals is None:
            return

        # we maintain the size of individual archives to a stable number of records, typically 1000,
        # due to the strong variability of records per intervals over time
        current_chunks = []
        start_period = None
        index = 0
        nb_intervals_processed = 0

        for interval in self.intervals:
            if self.limit and nb_intervals_processed == self.limit:
                break
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
                    '%s.TO.%s_%s.json' % (start_period, interval[1], index))
                start_period = interval[1]
                index += 1

                print("output_chunk_file:", output_chunk_file)

                with open(output_chunk_file, 'w') as fh:
                    json.dump(current_chunks, fh)

                self.output_files.append(output_chunk_file)
                print(output_chunk_file, "written")

                current_chunks = chunks[gap:]
            nb_intervals_processed += 1

        # remaining chunks
        if len(current_chunks)>0:
            output_chunk_file =  os.path.join(self.output_dir, 
                    '%s.TO.%s_%s.json' % (start_period, interval[1], index))

            with open(output_chunk_file, 'w') as fh:
                json.dump(current_chunks, fh)

            self.output_files.append(output_chunk_file)
            print("last archive:" + output_chunk_file, "written")

        #raise Exception("HERE")