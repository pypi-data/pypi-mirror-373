import os
import mimetypes
import xml.dom.minidom as md
from pypers.utils.xmldom import save_xml
from pypers.steps.base.extract import ExtractBase
import re
from pypers.utils import utils
import shutil

class Trademarks(ExtractBase):
    """
    Extract PETM archive
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ],
        "args":
        {
            "outputs": [
                {
                    "name": "del_list",
                    "descr": "del file that contains a list of application"
                             " numbers to be deleted"
                }
            ],
        }
    }

    def preprocess(self):
        self.data_files = {}
        self.img_files = {}
        self.media_files = {}
        # self.archives is a tuple of (date, {archive_name: xxx, archives[]})

        if not len(self.archives):
            return

        extraction_date = self.archives[0]
        archive_name = self.archives[1]['name']
        archives = self.archives[1]['archives']
        # prepare destination dir under pipeline scratch dir
        self.extraction_dir = os.path.join(
            self.meta['pipeline']['output_dir'],
            '__scratch',
            extraction_date,
            archive_name
        )

        # deletes the directory if prev exists
        utils.mkdir_force(self.extraction_dir)

        self.manifest = {'archive_name': archive_name,
                         'archive_file': archive_name,
                         'archive_date': extraction_date,
                         'extraction_dir': self.extraction_dir,
                         'data_files': {},
                         'img_files': {},
                         'media_files': {}}
        for archive in archives:
            extraction = os.path.join(self.extraction_dir, os.path.basename(archive))
            self.collect_files(self.unpack_archive(archive, extraction))

    def file_in_archive(self, file, path):
        f_name, ext = os.path.splitext(os.path.basename(file))
        appnum = None
        # appnum can be infered from f_name:
        # 000878700A-2021.xml -> 878700A2021
        result = re.search(r".*PE5([\dA-Z\-]+).*", f_name)
        if len(result.groups()) != 0:
            appnum = result.group(1)
            # remove leading 0 
            appnum = appnum.lstrip("0")
            #appnum = f_name.replace(".xml", "")
            appnum = appnum.replace("-", "")
            #appnum = appnum.lstrip("0")
        if ext.lower() == '.xml':
            self.add_xml_file(f_name, os.path.join(path, file))
        elif ext.lower() == '.jpg' or ext.lower() == '.png':
            # we are sure we have an image
            if appnum != None:
                self.add_img_file(appnum, os.path.join(path, file))
            else:
                self.add_img_file(file, os.path.join(path, file))
        else:
            file_mime = mimetypes.guess_type(file)[0]
            if (file_mime or '').startswith('image/'):
                if appnum != None:
                    self.add_img_file(appnum, os.path.join(path, file))
                else:
                    self.add_img_file(file, os.path.join(path, file))

    def add_xml_file(self, filename, fullpath):
        xml_dir = os.path.join(self.extraction_dir, 'xml')
        if not os.path.exists(xml_dir):
            os.makedirs(xml_dir)
        try:
            xml_dom = md.parse(fullpath)
            trdmrks = xml_dom.getElementsByTagName('TradeMark')
        except:
            return
        # reversed to get newer updates first
        # sometimes same trademark is included twice
        # get the last one
        appnum = None
        for mark in reversed(trdmrks):
            appnum_tag = mark.getElementsByTagName('ApplicationNumber')[0]
            if not appnum_tag or not appnum_tag.firstChild:
                self.logger.info('%s Empty ApplicationNumber' % mark)
                continue
            appnum = mark.getElementsByTagName('ApplicationNumber')[0].firstChild.nodeValue
            # some massage to have something like the img and ensure association
            # data + image
            appnum = appnum.replace("-", "")
            appnum = appnum.lstrip("0")
        if appnum == None:
            self.logger.info('%s missing ApplicationNumber' % fullpath)
            return
        appxml_file = os.path.join(xml_dir, '%s.xml' % appnum)
        shutil.copy(fullpath, appxml_file)

        self.manifest['data_files'].setdefault(appnum, {})
        self.manifest['data_files'][appnum]['ori'] = os.path.relpath(
            appxml_file, self.extraction_dir
        )
        #os.remove(fullpath)

    def process(self):
        pass