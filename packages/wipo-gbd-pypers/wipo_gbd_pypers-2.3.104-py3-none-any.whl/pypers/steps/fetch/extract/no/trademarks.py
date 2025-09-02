import os
import re
import requests
import codecs
from pypers.steps.base.extract import ExtractBase
from pypers.utils import utils

import json

class Trademarks(ExtractBase):
    """
    Extract NOTM marks information from the API response
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }

    # a file with trademarks in XML
    def unpack_archive(self, archive, dest):
        self.logger.debug('processing file %s' % archive)

        results = []

        try:
            with open(archive) as f:
                results = json.load(f)
        except Exception as e: 
            self.logger.error("JSON parsing failed for %s: %s" % (archive, e))

        if len(results) == 0:
            return

        for result in results:
            try:
                appnum = result["trademarkBag"]["trademark"][0]["trademarkTypeChoice1"]["applicationNumber"][0]["applicationNumberText"]
                # sanitize
                appnum = appnum.replace('/', '')

                # in some cases the year prefix is missing from the applicationNumberText, we can get it from the applicationDate field
                """
                if len(appnum)<7:
                    # mising year prefix
                    try:
                        appdate = result["trademarkBag"]["trademark"][0]["trademarkTypeChoice2"]["applicationDate"]
                        # get the year
                        if appdate_year and len(appdate_year)>4:
                            appdate_year = appdate[:4]
                            appnum = appdate_year+appnum
                    except:
                        self.logger.error("Could not get the application date for application number %s for %s" % (appnum, archive))
                        continue
                """
            except:
                self.logger.error("Could not get the application number for %s" % (archive))
                continue
            
            appjson_file = os.path.join(dest, appnum+".json")
            with open(appjson_file, 'w') as fh:
                json.dump(result, fh)

            self.add_xml_file(appnum, appjson_file)

            # get the image url
            try:
                img_uri = result["trademarkBag"]["trademark"][0]["markRepresentation"]["markReproduction"]["markImageBag"]["markImage"][0]["fileName"]            
                self.add_img_url(appnum, img_uri)
            except:
                # no image
                pass
            

    def collect_files(self, dest):
        pass

    def process(self):
        pass
        #raise Exception("HERE")
