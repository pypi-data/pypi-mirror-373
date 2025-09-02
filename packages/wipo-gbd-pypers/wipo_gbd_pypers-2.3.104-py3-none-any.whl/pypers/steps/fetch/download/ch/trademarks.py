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
from pypers.steps.base.fetch_step_api import FetchStepAPI

import logging
import logging.handlers 

#get here pypers logging 
#import urllib3
#urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#logging.getLogger("urllib3").setLevel(logging.ERROR)

from . import get_auth_token

class Trademarks(FetchStepAPI):
    spec = {
        "version": "2.0",
        "descr": [
            "Fetch updates using REST API"
        ],
    }

    token = None

    def get_connections_info(self):
        return None, None

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
            # # expecting names like : 2018-01-07.TO.2018-01-08.1.txt
            last_update = sorted(self.done_archives)[-1].split('.')[2]
            if '_' in last_update:
                last_update = last_update.split('_')[0]
            last_update = datetime.datetime.fromisoformat(last_update)

        today = datetime.datetime.today()

        result = []
        current_date = last_update.strftime("%Y-%m-%d")

        for one_date in self.daterange(last_update, today):
            next_date = one_date.strftime("%Y-%m-%d")
            result.append( (current_date, next_date) )
            current_date = next_date

        print(result)
        return result

    def lazy_get_auth_token(self, force=False):
        if self.token == None or force:
            self.token = get_auth_token(self.conn_params)
        return self.token

    template_update = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" \
        "<ApiRequest xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"urn:ige:schema:xsd:datadeliverycore-1.0.0 urn:publicid:-:IGE:XSD+DATADELIVERYCORE+1.0.0:EN " \
        "urn:ige:schema:xsd:datadeliverycommon-1.0.0 urn:publicid:-:IGE:XSD+DATADELIVERYCOMMON+1.0.0:EN urn:ige:schema:xsd:datadeliverytrademark-1.0.0 urn:publicid:-:IGE:XSD+DATADELIVERYTRADEMARK+1.0.0:EN\" " \
        "xmlns=\"urn:ige:schema:xsd:datadeliverycore-1.0.0\" xmlns:tm=\"urn:ige:schema:xsd:datadeliverytrademark-1.0.0\">" \
        "<Action type=\"TrademarkSearch\">" \
        "<tm:TrademarkSearchRequest xmlns=\"urn:ige:schema:xsd:datadeliverycommon-1.0.0\">" \
            "<Representation details=\"Maximal\" image=\"Embed\"/>" \
            "<Query>" \
            "    <LastUpdate from=\"{{$start_date}}\" includeFrom=\"true\" to=\"{{$end_date}}\" includeTo=\"false\"></LastUpdate>" \
            "</Query>" \
            "<Sort>" \
            "    <LastUpdateSort>Ascending</LastUpdateSort>" \
            "</Sort>" \
        "</tm:TrademarkSearchRequest>" \
        "</Action>" \
        "</ApiRequest>"

    def trademark_update(self, start_date, end_date):
        try:
            token = self.lazy_get_auth_token()
        except Exception as e: 
            return { "error": str(e) }

        xml_chunks = []

        header = {
            'Authorization': 'Bearer ' + token,
            'Accept': 'application/xml',
            'Content-Type': 'application/xml'
        } 

        body_xml = self.prepare_template(self.template_update, startDate=start_date, endDate=end_date)

        response = requests.post(self.api_url, headers=header, data=body_xml,  verify=False)

        if response.status_code == 200:
            result = { "xml": response.text }
        elif response.status_code == 401 or response.status_code == 403:
            # update authentication token
            try:
                token = self.lazy_get_auth_token(force=True)
            except Exception as e:
                result = { "error": str(e) }

            if token != None:
                header = {
                    'Authorization': 'Bearer ' + token,
                    'Content-Type': 'application/xml',
                    'Accept': 'application/xml' 
                } 
                response = requests.post(self.api_url, headers=header, data=body_xml, verify=False)
                if response.status_code == 200:
                    result = { "xml": response.text }
                else:
                    result = { "error": response.content }
        elif response.status_code == 429:
            self.logger.error('metadata - quota limit exceeded')
            result = { "error": response.content }
        else:
            result = { "error": response.content }

        if "error" not in result and "xml" in result:
            next_page_token, local_xml_chunks = self.process_xml_response(result["xml"].encode('utf-8'))
            if local_xml_chunks != None and len(local_xml_chunks)>0:
                xml_chunks.extend(local_xml_chunks)
            
            while next_page_token != None:
                next_page_token, local_xml_chunks = self.fetching_next_page(next_page_token)
                if local_xml_chunks != None and len(local_xml_chunks)>0:
                    xml_chunks.extend(local_xml_chunks)
                    #print(str(len(local_xml_chunks)), "xml chunks added...")
                    #print("total", str(len(xml_chunks)), "xml chunks")

        return xml_chunks

    template_next_page = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" \
                        "<ApiRequest xmlns=\"urn:ige:schema:xsd:datadeliverycore-1.0.0\">" \
                        "<Continuation name=\"NextPage\">{{$token}}</Continuation>" \
                        "</ApiRequest>"

    def fetching_next_page(self, next_page_token):
        try:
            token = self.lazy_get_auth_token()
        except Exception as e: 
            return _, { "error": str(e) }

        header = {
            'Authorization': 'Bearer ' + token,
            'Accept': 'application/xml',
            'Content-Type': 'application/xml'
        } 

        body_xml = self.prepare_template(self.template_next_page, nextPageToken=next_page_token)
        
        response = requests.post(self.api_url, headers=header, data=body_xml, verify=False)

        if response.status_code == 200:
            result = { "xml": response.text }
        elif response.status_code == 401 or response.status_code == 403:
            #print("next page fetch failed...")

            # update authentication token
            try:
                token = self.lazy_get_auth_token(force=True)
            except Exception as e:
                result = { "error": str(e) }

            if token != None:
                header = {
                    'Authorization': 'Bearer ' + token,
                    'Content-Type': 'application/xml',
                    'Accept': 'application/xml' 
                } 
                response = requests.post(self.api_url, headers=header, data=body_xml, verify=False)
                if response.status_code == 200:
                    result = { "xml": response.text }
                else:
                    result = { "error": response.content }
        else:
            result = { "error": response.content }

        next_page_token = None
        xml_chunks = None

        if "error" not in result and "xml" in result:
            next_page_token, local_xml_chunks = self.process_xml_response(result["xml"].encode('utf-8'))
            if local_xml_chunks != None and len(local_xml_chunks)>0:
                xml_chunks = local_xml_chunks

        return next_page_token, xml_chunks

    def process_xml_response(self, xml_string):
        """
        Return the next page token, a list of XML chunks corresponding each to one trademark and 
        the list of corresponding application numbers
        """
        parser = etree.XMLParser(ns_clean=True, dtd_validation=False, load_dtd=False, no_network=True, recover=True, encoding='utf-8')
        try:
            xml_root = fromstring(xml_string, parser=parser)
        except Exception as e: 
            print(e)
            return None, None
        return self.get_next_page_token(xml_root), self.get_xml_chunks(xml_root)

    def get_appnum_from_chunks(self, xml_root):
        nss = { "com": "http://www.wipo.int/standards/XMLSchema/ST96/Common", "tmk": "http://www.wipo.int/standards/XMLSchema/ST96/Trademark" }
        return xml_root.xpath("//tmk:Trademark/com:ApplicationNumber/com:ApplicationNumberText/text()", namespaces=nss)

    def prepare_template(self, template, uuidValue=None, timeStamp=None, nextPageToken=None, startDate=None, endDate=None):
        body_xml = template

        if startDate != None:
            body_xml = body_xml.replace("{{$start_date}}", startDate)
        if endDate != None:
            body_xml = body_xml.replace("{{$end_date}}", endDate)

        if nextPageToken != None:
            body_xml = body_xml.replace("{{$token}}", nextPageToken)

        return body_xml

    def get_next_page_token(self, xml_root):
        nss = { "api": "urn:ige:schema:xsd:datadeliverycore-1.0.0" }
        results = xml_root.xpath("//api:Continuations/api:Continuation[@name='NextPage']/text()", namespaces=nss)
        if len(results) == 1:
            return results[0]
        else:
            return None

    def get_xml_chunks(self, xml_root):
        nss = { "tmk": "http://www.wipo.int/standards/XMLSchema/ST96/Trademark" }
        return xml_root.xpath("//tmk:Trademark", namespaces=nss)

    def specific_api_process(self, session):
        self.api_url = "https://"+self.conn_params["apiHost"]+"/public/api/v1"

        if self.intervals is None:
            return
        nb_intervals_processed = 0
        for interval in self.intervals:
            if self.limit and nb_intervals_processed == self.limit:
                break
            print("download interval:", interval)
            chunks = self.trademark_update(interval[0], interval[1])
            print("total for interval", str(len(chunks)), "XML chunks")

            self.logger.info('%s-%s: %d applications found' % (interval[0], interval[1], len(chunks)))

            # write output file with these chunks 
            output_chunk_file =  os.path.join(self.output_dir, 
                '%s.TO.%s_%s.xml' % (interval[0], interval[1], len(chunks)))

            print("output_chunk_file:", output_chunk_file)

            with open(output_chunk_file, 'w') as fh:
                fh.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
                fh.write("<trademarkBag>\n")
                for chunk in chunks:
                    fh.write(etree.tostring(chunk, pretty_print=True).decode("utf-8"))
                    fh.flush()
                fh.write("</trademarkBag>")
            self.output_files.append(output_chunk_file)

            print(output_chunk_file, "written")

            nb_intervals_processed += 1

        #raise Exception("HERE")


       