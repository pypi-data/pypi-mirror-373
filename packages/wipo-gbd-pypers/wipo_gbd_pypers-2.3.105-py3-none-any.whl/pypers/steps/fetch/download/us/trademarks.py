import os
import re
import time
import json
from bs4 import BeautifulSoup
#from pypers.steps.base.fetch_step_http import FetchStepHttpAuth
from pypers.steps.base.fetch_step_api import FetchStepAPI
from pypers.utils.utils import ls_dir
import datetime 
import subprocess

#from selenium import webdriver
#from selenium.webdriver.chrome.options import Options
#from selenium.webdriver.common.by import By
#from selenium.webdriver.support.wait import WebDriverWait

class Trademarks(FetchStepAPI):

    pattern = re.compile("^apc(\d+)\.zip$")

    spec = {
        "version": "2.0",
        "descr": [
            "Fetch using HTTP GET"
        ],
        "args":
        {
            "params": [
                {
                    "name": "file_xml_regex",
                    "type": "str",
                    "descr": "regular expression to filter files",
                    "value": ".*"
                },
                {
                    "name": "file_img_regex",
                    "type": "str",
                    "descr": "regular expression to filter files",
                    "value": ".*"
                }
            ],
        }
    }

    token = None

    def get_connections_info(self):
        return None, None

    def _process_from_local_folder(self):
        # getting files from local dir
        if self.fetch_from.get('from_dir'):
            self.logger.info(
                'getting %s files that match the regex [%s] from %s' % (
                    'all' if self.limit == 0 else self.limit,
                    '%s or %s' % (self.file_xml_regex, self.file_img_regex),
                    self.fetch_from['from_dir']))
            xml_archives = ls_dir(
                os.path.join(self.fetch_from['from_dir'], '*'),
                regex=self.file_xml_regex, limit=self.limit,
                skip=self.done_archives)

            img_archives = ls_dir(
                os.path.join(self.fetch_from['from_dir'], '*'),
                regex=self.file_img_regex % ('.*'), limit=self.limit,
                skip=self.done_archives)
            self.output_files = xml_archives + img_archives
            return True
        return False

    def daterange(self, start_date, end_date):
        days = int((end_date - start_date).days)
        for n in range(days):
            yield start_date + datetime.timedelta(n+1)

    def get_intervals(self):
        """ 
        Return the intervals to be downloaded, in our case one interval is one day, so
        we enumerate days from the day of the last update 
        """
        # get the date of the last update
        if not len(self.done_archives):
            # no done archives in dynamodb table gbd_pypers_done_archive 
            last_update = (datetime.datetime.today() - datetime.timedelta(1))
        else:
            # we get the day of the last update from the last "done_archive" file name stored 
            # in dynamodb table gbd_pypers_done_archive 
            # expecting names like : apc250831.zip
            # we might have some directory prefix to prune
            local_archives = []
            for archive in self.done_archives:
                if "/" in archive:
                    archive = os.path.basename(archive)
                if archive.startswith("hrs"):
                    archive = archive.replace("hrs", "apc")
                local_archives.append(archive)

            last_update = sorted(local_archives)[-1].split('.')[0]
            last_update = last_update.replace("apc", "")
            # some old hrs180102a.zip formats might still exist in the list
            if len(last_update) == 7:
                last_update = last_update[0:7]

            last_update = "20" + last_update[:2] + "-" + last_update[2:4] + "-" + last_update[4:]
            last_update = datetime.datetime.fromisoformat(last_update)

        today = datetime.datetime.today()
        current_date = last_update.strftime("%Y-%m-%d")
        result = []
        for one_date in self.daterange(last_update, today):
            next_date = one_date.strftime("%Y-%m-%d")
            result.append( (current_date, next_date) )
            current_date = next_date

        print(result)
        return result

    def specific_api_process(self, session):
        """
        Download new archives using the USPTO Open Data API
        """
        self.token = self.conn_params["credentials"]["key"]
        self.api_url = "https://"+self.conn_params["base_url"]+"/api/v1/datasets/products"

        # the following command can be used to retrieve the list of trademark data files for a given range of time
        cmd = "curl -X GET " \
            "https://api.uspto.gov/api/v1/datasets/products/trtdxfap?fileDataFromDate=%s&fileDataToDate=%s&includeFiles=true " \
            "-H 'Accept: application/json " \
            "-H 'Content-Type: application/json " \
            "-H 'x-api-key: %s " \
            "-o %s"

        # the response follows this pattern
        # { "bulkDataProductBag": [
        #  { "productFileBag": {
        #       "fileDataBag": [ 
        #           { "fileName": "apc250831.zip",
        #             "fileDownloadURI": "https://api.uspto.gov/api/v1/datasets/products/files/TRTDXFAP/apc250831.zip",

        # the following is the pattern for downloading the daily trademark data files (e.g. apc250830.zip)
        url_pattern = self.api_url  + "/files/TRTDXFAP/apc%s.zip"
        cmd_download = 'wget --header="x-api-key:%s" -q --retry-connrefused --waitretry=15 ' \
            '--read-timeout=60 --timeout=15 -t 5 ' \
            '-P %s %s '
        count = 0
        for interval in self.intervals:
            if self.limit and count == self.limit:
                break
            local_date = interval[1][2:]
            local_date = local_date.replace("-", "")

            url = url_pattern % (local_date)
            local_cmd_download = cmd_download % (self.token, self.output_dir, url)
            print(local_cmd_download)
            try:
                subprocess.check_call(local_cmd_download, shell=True)
            except Exception as e:
                self.logger.warning("Error in %s: %s" % (cmd, e))
                raise e

            output_file = os.path.join(self.output_dir, "apc"+local_date+".zip")
            self.output_files.append(output_file)
            count += 1
            
