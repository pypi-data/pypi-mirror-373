import os
import mimetypes
import xml.etree.ElementTree as ET
from pypers.utils.xmldom import clean_xmlfile
from pypers.steps.base.extract import ExtractBase


class Designs(ExtractBase):
    """
    Extract IPAS archive
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ],
        "args":
        {
            "params": [
                {
                    "name": "version",
                    "descr": "the version of the WIPO Publish used",
                    "value": "1.5.0"
                }
            ]
        }
    }

    img_files_found = {}
    img_files_required = {}

    def file_in_archive(self, file, path, archive_name=None):
        fname, ext = os.path.splitext(os.path.basename(file))
        # path: <archive>/KHM01368334/
        # file: KHM01368334_biblio.xml
        if ext.lower() == '.xml':
            appnum = os.path.basename(path)
            if fname.endswith('_biblio'):
                self.add_xml_file(appnum, os.path.join(path, file))

        # path: <archive>/KHM01368334/ATTACHMENT/
        # file: logo.jpeg
        else:
            # get appnum
            file_mime = mimetypes.guess_type(file)[0]
            if (file_mime or '').startswith('image/'):
                self._add_img_file(fname, os.path.join(path, file))
            elif file_mime == 'application/zip':
                self.archive_in_archive(file, path)

    def _add_img_file(self, appnum, fullpath):
        self.img_files_found[appnum] = fullpath

    def _add_img_file_req(self, appnum, fullpath):
        self.img_files_required.setdefault(appnum, [])
        self.img_files_required[appnum].append(fullpath)

    def add_xml_file(self, filename, fullpath):
        ns = 'http://www.wipo.int/standards/XMLSchema/designs'
        ET.register_namespace('', ns)
        dsnnum = 0  # no DesignReference in xml, use a counter
        fullpath = clean_xmlfile(fullpath, overwrite=True)

        context = ET.iterparse(fullpath, events=('end',))
        for event, elem in context:
            if elem.tag[0] == "{":
                uri, tag = elem.tag[1:].split("}")
            else:
                tag = elem.tag

            if tag == 'DesignApplication':
                dsnnum += 1
                try:
                    appnum = elem.find(
                        '{%(ns)s}DesignApplicationNumber' % {'ns': ns}).text
                except Exception as e:
                    continue
                appnum = "%s-%s" % (appnum, dsnnum)
                self.manifest['data_files'].setdefault(appnum, {})
                self.manifest['data_files'][appnum]['ori'] = os.path.relpath(
                    fullpath, self.extraction_dir
                )

                design_elems = elem.findall(
                    '{%(ns)s}DesignDetails/{%(ns)s}Design' % {'ns': ns})
                for design_elem in design_elems:
                    view_elems = design_elem.findall(
                        '{%(ns)s}DesignRepresentationSheetDetails/'
                        '{%(ns)s}DesignRepresentationSheet/'
                        '{%(ns)s}RepresentationSheetFilename' % {'ns': ns})

                    for idx, view_elem in enumerate(view_elems):
                        try:
                            img_name, _ = os.path.splitext(view_elem.text)
                        except Exception as e:
                            continue
                        self._add_img_file_req(appnum, img_name)

    def process(self):
        for appnum in self.img_files_required.keys():
            for img in self.img_files_required[appnum]:
                if img in self.img_files_found.keys():
                    self.add_img_file(appnum, self.img_files_found[img])
