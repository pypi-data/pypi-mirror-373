import os
import sys
import shutil
import subprocess
from pypers.utils import download
from pypers.steps.base.step_generic import EmptyStep
from pypers.utils import utils

class DownloadIMG(EmptyStep):
    spec = {
        "version": "2.0",
        "descr": [
            "download images for extractions"
        ],
        "args":
        {
            "params": [
                {
                    "name": "avoid_cache",
                    "descr": "avoid caching",
                    "value": 0
                },
                {
                    "name": "file_ext",
                    "descr": "the extension of images to be downloaded",
                    "value": "jpg"
                },
                {
                    "name": "limit",
                    "type": "int",
                    "descr": "the upper limit of the archives to download. "
                             "default 0 (all)",
                    "value": 0
                },
                {
                    "name": "use_wget",
                    "type": "int",
                    "descr": "Flag to change the way to download the image",
                    "value": 0
                },
                {
                    "name": "ori_ref_dir",
                    "type": "str",
                    "descr": "the directory that contains the original files",
                    "value": "/efs-etl/collections/downloads/"
                }
            ],
            "inputs": [
                {
                    "name": "manifest",
                    "descr": "the manifest of extraction",
                    "iterable": True
                }
            ],
            "outputs": [
                {
                    "name": "manifest",
                    "descr": "manifest file listing the content of archive"
                }
            ]
        }
    }


    def do_download(self, uri, dest):
        # needed for imgs download
        proxy_params = {
            'http':  self.meta['pipeline']['input'].get('http_proxy', None),
            'https': self.meta['pipeline']['input'].get('https_proxy', None)
        }
        if self.use_wget == 1:
            cmd = 'wget -q -O %s -t 5 %s' % (dest, uri)
            try:
                subprocess.check_call(cmd.split(' ') + ['--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"'])
                return dest
            except Exception as e:
                self.logger.error("Downloading problem with wget in %s: %s" % (uri, e))
                return None
        else:
            try:
                rh = download.download(
                    uri, wait_secs=.2,
                    http_proxy=proxy_params['http'],
                    https_proxy=proxy_params['https'])
                with open(dest, 'wb') as fh:
                    fh.write(rh.read())
                rh.close()
                return dest
            except Exception as e:
                self.logger.error("Downloading problem in %s: %s" % (uri, e))
                return None

    def process(self):
        if isinstance(self.manifest, list):
            return
        # nothing to do here. exit.
        if not len(self.manifest.keys()):
            return

        totryagain = []
        self.download_counter = 0
        extraction_dir = os.path.join(self.manifest['extraction_dir'], 'downloaded_imgs')
        os.makedirs(extraction_dir, exist_ok=True)
        # input can come from multiple extract steps
        for appnum in self.manifest['img_files'].keys():
            self.process_appnum(appnum, totryagain, extraction_dir)
        #if len(totryagain):
        #    self.logger.info('\n\nRETRYING %s downloads' % len(totryagain))
        #    self.process_appnum(appnum, [], extraction_dir)
        self.manifest = [self.manifest]

    def process_appnum(self, appnum, retry_buffer, extraction_dir):
        """ Return Error and  nb downloaded files"""
        imgs_urls = self.manifest['img_files'][appnum]
        for idx, img in enumerate(imgs_urls, start=1):
            if self.limit != 0 and self.download_counter == self.limit:
                break
            error_appnum, increment = self.process_single(img, idx, appnum, extraction_dir)
            if error_appnum:
                retry_buffer.append(error_appnum)
            self.download_counter += increment

    def get_from_cache(self, appnum, idx):
        cache_path = os.path.join(
            self.ori_ref_dir,
            self.collection,
            utils.appnum_to_subdirs(appnum),
        )
        os.makedirs(cache_path, exist_ok=True)
        cache_path = os.path.join(
            cache_path,
            '%s.%d.%s' % (appnum, idx, self.file_ext)
        )
        if os.path.exists(cache_path):
            return cache_path, True
        return cache_path, False

    def process_single(self, img, idx, appnum, extraction_dir):
        """ Return Error and  nb downloaded files"""
        if not img.get('url', None):
            return None, 0
        img_file = os.path.join(extraction_dir, '%s.%d.%s' % (
            appnum, idx, self.file_ext))
        dest = os.path.join(extraction_dir, img_file)

        if os.path.exists(dest):
            downloaded_file = dest
            increment = 0
        else:
            if self.avoid_cache:
                downloaded_file = self.do_download(img['url'], dest)
                if downloaded_file:
                    increment = 1
            else:
                #Caching....
                cache_path, is_cached = self.get_from_cache(appnum, idx)
                if is_cached:
                    shutil.copy(cache_path, dest)
                    downloaded_file = dest
                    increment = 0
                else:
                    downloaded_file = self.do_download(img['url'], dest)
                    if downloaded_file:
                        shutil.copy(dest, cache_path)
                        increment = 1
        if downloaded_file:
            self.logger.info('SUCCESS downloading %s' % (img['url']))
            img['ori'] = os.path.relpath(downloaded_file, self.manifest['extraction_dir'])
            img.pop('url')
            return None, increment
        else:
            self.logger.error('ERROR   downloading %s' % (img['url']))
            return appnum, 0
