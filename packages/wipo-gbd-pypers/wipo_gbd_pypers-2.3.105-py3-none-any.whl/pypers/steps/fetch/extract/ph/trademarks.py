import os
import math
import subprocess
import shutil
from pypers.utils import utils
from lxml import etree
from pypers.steps.base.extract import ExtractBase


class Trademarks(ExtractBase):
    """
    Extract PHTM archives
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }

    
    def preprocess(self):
        self.counter_xml = 0
        self.data_files = {}
        self.img_files = {}
        self.media_files = {}
        # self.archives is a tuple of (date, {archive_name: xxx, archives[]})

        if not len(self.archives):
            return

        extraction_date = self.archives[0]
        archive_file = self.archives[1]
        archive_name = os.path.basename(archive_file).replace(".zip", "")
        archives = self.archives[1:]
        # prepare destination dir under pipeline scratch dir
        self.extraction_dir = os.path.join(
            self.meta['pipeline']['output_dir'],
            '__scratch',
            extraction_date,
            archive_name
        )

        # deletes the directory if prev exists
        utils.mkdir_force(self.extraction_dir)

        xml_dir = os.path.join(self.extraction_dir, 'xml')
        os.makedirs(xml_dir, exist_ok=True)

        self.manifest = {'archive_name': archive_name,
                         'archive_file': archive_file,
                         'archive_date': extraction_date,
                         'extraction_dir': self.extraction_dir,
                         'data_files': {},
                         'img_files': {},
                         'media_files': {}}
        for archive in archives:
            self.collect_files(self.unpack_archive(archive, os.path.join(self.extraction_dir, os.path.basename(archive))))
    

    def add_xml_file(self, filename, fullpath):
        self.logger.info('\nprocessing file: %s' % (fullpath))

        xml_dir = os.path.join(self.extraction_dir, 'xml')

        #clean_xmlfile(fullpath, readenc='utf-16le', writeenc='utf-8', overwrite=True)

        # sometimes it happens that we get
        # an empty update. ex: 20151225
        with open(fullpath, 'r') as fh:
            lines = fh.readlines()
            if len(lines) < 1:
                return

        parser = etree.XMLParser(ns_clean=True, dtd_validation=False, load_dtd=False, no_network=True, recover=True, encoding='utf-8')
        xml_root = None
        try:
            xml_root = etree.parse(fullpath, parser=parser)
        except Exception as e: 
            self.logger.error("XML parsing failed for %s: %s" % (fullpath, e))

        if xml_root == None:
            return

        nss = { "tmk": "http://www.wipo.int/standards/XMLSchema/trademarks", "wo": "http://www.wipo.int/standards/XMLSchema/wo-trademarks" }
        appnum_nodes = xml_root.xpath("//tmk:TradeMark/tmk:ApplicationNumber/text()", namespaces=nss)
        if appnum_nodes != None and len(appnum_nodes)>0:
            appnum = str(appnum_nodes[0])

            # sanitize appnum
            appnum = appnum.replace('/', '').replace('-', '').replace('(', '-').replace(')', '')

            app_file = os.path.join(xml_dir, '%s.xml' % (appnum))
            shutil.copyfile(fullpath, app_file)

            self.manifest['data_files'].setdefault(appnum, {})
            self.manifest['data_files'][appnum]['ori'] = os.path.relpath(
                app_file, self.extraction_dir
            )

            img_nodes = xml_root.xpath("//tmk:TradeMark//tmk:MarkImage", namespaces=nss)
            if img_nodes and len(img_nodes)>0:
                for img_node in img_nodes:         
                    img_node_filename = img_node.xpath("./tmk:MarkImageFilename/text()", namespaces=nss)
                    img_format_node = img_node.xpath("./tmk:MarkImageFileFormat/text()", namespaces=nss)

                    if img_node_filename and len(img_node_filename)>0:
                        img_node_filename = img_node_filename[0]

                    if img_node_filename:
                        if img_format_node and len(img_format_node)>0:
                            img_format_node = img_format_node[0]

                        ind = img_node_filename.find("/")
                        img_file = None
                        if img_format_node and len(img_format_node)>0:
                            if ind != -1:
                                img_node_subpath = img_node_filename[:ind]
                                if img_node_filename.find(".") == -1:
                                    img_node_filename = img_node_filename[ind+1:]+"."+img_format_node.lower()
                                img_file = os.path.join(os.path.dirname(fullpath), img_node_subpath, img_node_filename)
                            else:
                                if img_node_filename.find(".") == -1:
                                    img_node_filename = img_node_filename+"."+img_format_node.lower()
                                img_file = os.path.join(os.path.dirname(fullpath), img_node_filename)
                        else:
                            if ind != -1:
                                img_node_subpath = img_node_filename[:ind]
                                img_file = os.path.join(os.path.dirname(fullpath), img_node_subpath, img_node_filename[ind+1:])
                            else:
                                img_file = os.path.join(os.path.dirname(fullpath), img_node_filename)
                        if img_file:
                            self.add_img_file(appnum, img_file)
        # remove the file when done with it
        os.remove(fullpath)

    def add_img_file(self, appnum, fullpath):
        if appnum == "logo":
            return

        if os.environ.get('GBD_DEV_EXTRACT_LIMIT', None):
            if len(self.manifest['img_files'].keys()) >= int(
                    os.environ.get('GBD_DEV_EXTRACT_LIMIT')):
                return

        path = os.path.relpath(fullpath, self.extraction_dir)

        self.manifest['img_files'].setdefault(appnum, [])
        self.manifest['img_files'][appnum].append(
            {'ori': path}
        )

    def process(self):
        pass

