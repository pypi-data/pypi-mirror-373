import os
import mimetypes
import xml.dom.minidom as md
from pypers.utils.xmldom import save_xml
from pypers.steps.base.extract import ExtractBase
import re
from pypers.utils import utils

class Trademarks(ExtractBase):
    """
    Extract MCTM archive
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
        # PL: fix for images, images need to be added here, not when the xml file is parsed because
        # nothing garantee the right order (and actually the order is wrong usually)
        # appnum can be infered from f_name:
        # 2025-07-21-MC500000000017290.xml -> 17290
        # MC500000000032792.jpg -> 32792
        # regex is ".*MC5(\d+).*"
        result = re.search(r".*MC5(\d+).*", f_name)
        if len(result.groups()) != 0:
            appnum = result.group(1)
            # remove leading 0 
            appnum = appnum.lstrip("0")
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
        for mark in reversed(trdmrks):
            appnum_tag = mark.getElementsByTagName('ApplicationNumber')[0]
            if not appnum_tag or not appnum_tag.firstChild:
                self.logger.info('%s Empty ApplicationNumber' % mark)
                continue
            appnum = mark.getElementsByTagName('ApplicationNumber')[0].firstChild.nodeValue
            appxml = md.Document()
            # appxml = xml_tmpl.cloneNode(deep=True)
            appxml.appendChild(mark)
            appxml_file = os.path.join(xml_dir, '%s.xml' % appnum)
            save_xml(appxml, appxml_file, addindent='  ', newl='\n')

            self.manifest['data_files'].setdefault(appnum, {})
            self.manifest['data_files'][appnum]['ori'] = os.path.relpath(
                appxml_file, self.extraction_dir
            )
            # PL: the following is wrong, there is no garantee that the images have already 
            # been extracted at this point... see the fix at the level of file_in_archive()
            '''
            img_tag = mark.getElementsByTagName('MarkImageFilename')
            if len(img_tag):
                img_val = img_tag[0].firstChild.nodeValue
                if img_val:
                    img_name = os.path.basename(img_val)
                    #img_name = img_name[0:img_name.index('.')]
                    img_file = self.img_files.get(img_name)
                    #img_file = self.img_files.get(appnum)
                    if img_file:
                        self.add_img_file(appnum, img_file)
            '''
        os.remove(fullpath)

    def process(self):
        pass