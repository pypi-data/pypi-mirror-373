import os
import re
import requests
import codecs
from pypers.steps.base.extract import ExtractBase
from pypers.utils import utils

from lxml import etree

class Trademarks(ExtractBase):
    """
    Extract CHTM marks information from the API response
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }

    slice_size = 10000

    # a file with trademarks in XML
    def unpack_archive(self, archive, dest):
        self.logger.debug('processing file %s' % archive)

        # segment the xml file into smaller chunks if necessary 
        archives = []
        piece = 0
        nb_trademark = 0
        current_file_out = archive.replace(".xml", "_"+str(piece)+".xml")
        archives.append(current_file_out)
        output = open(current_file_out, 'w')

        with open(archive, 'r') as file: 
            for line in file: 
                output.write(line)
                if line.startswith("<tmk:Trademark "):
                    nb_trademark += 1
                elif line.startswith("</tmk:Trademark>"):
                    if nb_trademark >= self.slice_size:
                        output.write("</trademarkBag>")
                        output.close()
                        archives.append(current_file_out)
                        nb_trademark = 0
                        piece += 1
                        current_file_out = archive.replace(".xml", "_"+str(piece)+".xml")
                        output = open(current_file_out, 'w')
                        output.write("<trademarkBag>")
        output.close()
        archives.append(current_file_out)

        print(archives)

        parser = etree.XMLParser(ns_clean=True, dtd_validation=False, load_dtd=False, no_network=True, recover=True, encoding='utf-8')
        for the_archive in archives:
            xml_root = None
            try:
                xml_root = etree.parse(the_archive, parser=parser)
            except Exception as e: 
                self.logger.error("XML parsing failed for %s: %s" % (the_archive, e))

            nss = { "com": "http://www.wipo.int/standards/XMLSchema/ST96/Common", "tmk": "http://www.wipo.int/standards/XMLSchema/ST96/Trademark" }
            trademark_nodes = xml_root.xpath("//tmk:Trademark", namespaces=nss)
            appnum_nodes = xml_root.xpath("//tmk:Trademark/com:ApplicationNumber/com:ApplicationNumberText/text()", namespaces=nss)
            for index, trademark_node in enumerate(trademark_nodes):
                if appnum_nodes != None and len(appnum_nodes)>index:
                    appnum = appnum_nodes[index]

                    # sanitize
                    appnum = appnum.replace('/', '')
                    appxml_file = os.path.join(dest, appnum+".xml")
                    with open(appxml_file, 'w') as fh:
                        fh.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
                        fh.write(etree.tostring(trademark_node, pretty_print=True).decode("utf-8"))
                    self.add_xml_file(appnum, appxml_file)

                    results = trademark_node.xpath("./tmk:MarkRepresentation/tmk:MarkReproduction/tmk:MarkImageBag/tmk:MarkImage/com:FileName/text()", namespaces=nss)
                    if results != None and len(results)>0:
                        self.add_img_url(appnum, str(results[0]))
        #print(str(len(self.manifest["img_files"])))

    def collect_files(self, dest):
        pass

    def process(self):
        pass
        #raise Exception("HERE")
