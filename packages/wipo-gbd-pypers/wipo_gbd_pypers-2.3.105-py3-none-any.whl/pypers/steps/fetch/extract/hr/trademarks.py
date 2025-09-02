import os
import re
import copy 
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from lxml import etree
from pypers.utils import utils
from pypers.steps.base.extract import ExtractBase

class Trademarks(ExtractBase):
    """
    Extract Trademarks archive
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }

    old_url_it = "http://it-app.dziv.hr"
    new_cti_url = "https://cti.dziv.hr"

    def preprocess(self):
        self.xml_data_map = {"AP": {}, "RE": {}}
        self.data_files = {}
        self.img_files = {}
        self.media_files = {}

        if not len(self.archives):
            return

        extraction_part = self.archives[0]
        archive_file = self.archives[1]
        archive_name = os.path.basename(self.archives[1]).replace(".zip", "")
        # prepare destination dir under pipeline scratch dir
        self.extraction_dir = os.path.join(
            self.meta['pipeline']['output_dir'],
            '__scratch',
            extraction_part,
            archive_name
        )

        # deletes the directory if prev exists
        utils.mkdir_force(self.extraction_dir)

        self.manifest = {'archive_name': archive_name,
                         'archive_file': archive_file,
                         'archive_date': extraction_part,
                         'extraction_dir': self.extraction_dir,
                         'data_files': {},
                         'img_files': {},
                         'media_files': {}}

        # unpack the archives and collect the files
        self.collect_files(self.unpack_archive(archive_file, self.extraction_dir))

    def file_in_archive(self, file, path):
        appnum, ext = os.path.splitext(os.path.basename(file))
        ind = appnum.find("HR")
        appnum = appnum[ind:]
        if ext.lower() == '.xml':
            self.add_xml_file(appnum, os.path.join(path, file))

    def process(self): 
        pass

    def download_requests(self, url, proxies=None):
        try:
            retry = Retry(
                total=5,
                backoff_factor=2,
                status_forcelist=[429, 500, 502, 503, 504],
            )

            adapter = HTTPAdapter(max_retries=retry)

            session = requests.Session()
            session.mount('http://', adapter)
            session.mount('https://', adapter)

            response = session.get(url, timeout=120, proxies=proxies)
            if response.ok:
                return response.text
            else:
                self.logger.error("download failed for %s with code %s" % (url, str(response.status_code)))
        except Exception as e:
            self.logger.error("connection failed for %s" % (url))
            self.logger.error(e)
        return None

    def add_xml_file(self, appnum, fullpath):
        # we need to grab URI for applicant, representative and images
        # in each XML file, then inject ApplicantDetails and 
        # RepresentativeDetails fragments in the XML document and save 
        # the XML for the transformation
        proxy_params = self.get_connection_params()
        parser = etree.XMLParser(ns_clean=True, dtd_validation=False, load_dtd=False, no_network=True, recover=True, encoding='utf-8')

        # first parse the available XML, which is the TM view XML file (incomplete, 
        # it has no representa tive information)
        root_xml = None
        try:
            parsed_xml = etree.parse(fullpath, parser)
            root_xml = parsed_xml.getroot()
        except Exception as e: 
            self.logger.error("XML parsing failed for %s: %s" % (fullpath, e))
            return

        if root_xml is not None:
            # this is the namespace for the TM View format
            ns = {"tm": "http://www.oami.europa.eu/TM-Search"}

            # get the complete XML record of the trademark, with representative information
            url_full = root_xml.xpath("//tm:TradeMarkDetails/tm:TradeMark/tm:TradeMarkURI/text()", namespaces=ns)
            if url_full != None and len(url_full)>0:
                url_full = url_full[0]

            full_xml_record = self.download_requests(url_full, proxies=proxy_params)
            if full_xml_record == None:
                self.logger.error("Fail to access full XML record at %s" % (url_full))
                return

            root_xml = None
            try:
                root_xml = etree.fromstring(bytes(bytearray(full_xml_record, encoding='utf-8')), parser)
            except Exception as e: 
                self.logger.error("XML parsing failed for full XML record %s: %s" % (fullpath, e))
                return

        # this is the namespace of the full record
        #ns = {"tm": "http://hr.tmview.europa.eu/trademark/data"}
        ns = {"tm": "http://tmview.europa.eu/trademark/data"}

        if root_xml is not None: 
            app_num = root_xml.xpath("//tm:TradeMarkDetails/tm:TradeMark/tm:ApplicationNumber/text()", namespaces=ns)
            if app_num != None and len(app_num)>0:
                app_num = app_num[0]
            if app_num:
                if not app_num[:1].isdigit():
                    app_num = app_num[1:]
                app_num = str(app_num)
            else:
                self.logger.error("Missing application number for %s" % (fullpath))
                return

            # start injecting applicant information
            app_uri = root_xml.xpath("//tm:ApplicantDetails/tm:ApplicantKey/tm:URI/text()", namespaces=ns)
            if app_uri != None and len(app_uri)>0:
                app_uri = app_uri[0]
            if app_uri:
                app_uri = str(app_uri)
                root_app_xml = None
                # check if the entity is in the local data map, otherwise online look-up
                if app_uri not in self.xml_data_map["AP"]:

                    #if app_uri.startswith(self.old_url_it):
                    #    app_uri = app_uri.replace(self.old_url_it, self.new_cti_url)

                    fragment = self.download_requests(app_uri, proxies=proxy_params)
                    if fragment != None:
                        self.xml_data_map["AP"][app_uri] = fragment
                        #self.xml_data_map["AP"][app_uri] = self.xml_data_map["AP"][app_uri].replace("http://hr.tmview.europa.eu/trademark/applicant", "http://tmview.europa.eu/trademark/data")
                        #self.xml_data_map["AP"][app_uri] = self.xml_data_map["AP"][app_uri].replace("http://tmview.europa.eu/trademark/applicant", "http://tmview.europa.eu/trademark/data")

                if app_uri in self.xml_data_map["AP"]:
                    try:
                        # parse the fragment
                        root_app_xml = etree.fromstring(bytes(bytearray(self.xml_data_map["AP"][app_uri], encoding='utf-8')), parser)
                    except Exception as e: 
                        self.logger.error("XML parsing failed for %s: %s" % (app_uri, e))

                if root_app_xml != None:
                    # inject the fragment
                    #app_fragment = root_app_xml.xpath("//tm:ApplicantDetails/tm:Applicant", namespaces=ns)
                    app_fragment = root_app_xml.xpath("//ApplicantDetails/Applicant", namespaces=ns)
                    if app_fragment != None and len(app_fragment)>0:
                        app_fragment = app_fragment[0]

                    # complement with applicant URI
                    applicant_URI_node = etree.Element("{http://tmview.europa.eu/trademark/data}ApplicantURI")
                    applicant_URI_node.text = app_uri
                    app_fragment.insert(0, applicant_URI_node)

                    # update the document
                    applicant_details_node = root_xml.xpath("//tm:ApplicantDetails", namespaces=ns)
                    if applicant_details_node != None and len(applicant_details_node)>0:
                        applicant_details_node = applicant_details_node[0]

                    # remove the existing children
                    for elem in applicant_details_node:
                        # remove the child
                        applicant_details_node.remove(elem)
                    # and replace them with the applicant fragment
                    applicant_details_node.insert(0, app_fragment)

            # injecting representative information
            rep_uri = root_xml.xpath("//tm:RepresentativeDetails/tm:RepresentativeKey/tm:URI/text()", namespaces=ns)
            if rep_uri != None and len(rep_uri)>0:
                rep_uri = rep_uri[0]
            if rep_uri:
                root_rep_xml = None
                # check if the entity is in the local data map, otherwise online look-up
                if rep_uri not in self.xml_data_map["RE"]:   

                    #if rep_uri.startswith(self.old_url_it):
                    #    rep_uri = rep_uri.replace(self.old_url_it, self.new_cti_url)

                    fragment = self.download_requests(rep_uri, proxies=proxy_params)
                    if fragment != None:
                        self.xml_data_map["RE"][rep_uri] = fragment
                        #self.xml_data_map["RE"][rep_uri] = self.xml_data_map["RE"][rep_uri].replace("http://tmview.europa.eu/trademark/representative", "http://tmview.europa.eu/trademark/data")

                if rep_uri in self.xml_data_map["RE"]:
                    try:
                        # parse the fragment
                        root_rep_xml = etree.fromstring(bytes(bytearray(self.xml_data_map["RE"][rep_uri], encoding='utf-8')), parser)
                    except Exception as e: 
                        self.logger.error("XML parsing failed for %s: %s" % (rep_uri, e))

                if root_rep_xml != None:
                    # inject the fragment
                    rep_fragment = root_rep_xml.xpath("//RepresentativeDetails/Representative", namespaces=ns)
                    if rep_fragment != None and len(rep_fragment)>0:
                        rep_fragment = rep_fragment[0]

                    # complement with representative URI
                    representative_URI_node = etree.Element("{http://tmview.europa.eu/trademark/data}RepresentativeURI")
                    representative_URI_node.text = rep_uri
                    rep_fragment.insert(0, representative_URI_node)

                    # update the document
                    representative_details_node = root_xml.xpath("//tm:RepresentativeDetails", namespaces=ns)
                    if representative_details_node != None and len(representative_details_node)>0:
                        representative_details_node = representative_details_node[0]

                    # remove the existing children
                    for elem in representative_details_node:
                        # remove the child
                        representative_details_node.remove(elem)
                    # and replace them with the representative fragment
                    representative_details_node.insert(0, rep_fragment)

            # save final complete document
            xml_data_rename = os.path.join(os.path.dirname(fullpath), '%s.xml' % app_num)
            et = etree.ElementTree(root_xml)
            with open(xml_data_rename, 'wb') as f:
                f.write(etree.tostring(et, encoding="utf-8", xml_declaration=True, pretty_print=True))
            os.remove(fullpath)

            self.manifest['data_files'].setdefault(app_num, {})
            self.manifest['data_files'][app_num]['ori'] = os.path.relpath(
                xml_data_rename, self.extraction_dir
            )

            img_uri = root_xml.xpath("//tm:MarkImageDetails/tm:MarkImage/tm:MarkImageURI/text()", namespaces=ns)
            if img_uri != None and len(img_uri)>0:
                img_uri = img_uri[0]
            if img_uri:
                self.add_img_url(app_num, img_uri)

