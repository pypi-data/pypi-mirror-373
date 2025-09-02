import os
import shutil
import datetime
import os
import io
import json
import time
import ntpath
from pathlib import Path
import yaml
import uuid
import subprocess
import zipfile
import re
import math
from bs4 import BeautifulSoup
from pypers.steps.base.fetch_step_http import FetchStepHttpAuth 

class Trademarks(FetchStepHttpAuth):
    spec = {
        "version": "2.0",
        "descr": [
            "Fetch using HTTP with Basic Auth"
        ],
    }

    chunk_size = 60000

    def check_slice_done(self, archive_base_name, index):
        for done_archive in self.done_archives:
            # check completed archives
            ind1 = done_archive.rfind("_")
            ind2 = done_archive.rfind("_", 0, ind1)
            if ind1 == -1 or ind2 == -1:
                continue
            index_to = done_archive[ind1+1:ind1+2]
            index_from = done_archive[ind2+1:ind2+2]

            index1 = int(index_from)
            index2 = int(index_to)

            if archive_base_name == done_archive[:ind2]:
                if index1 == index:
                    return True
        return False

    def parse_links(self, archive_name, count, cmd=None, archive_path=None,
                    callback=None, archive_url=None):
        """
        archives are considered by slice of a certain size, because they are
        initially too large for complete processing with the default memory. 
        For example if an archive contains 120,000 files for a slice size of 
        50,000, it will be considered 3 times at 3 different indices:
        archive.zip ->  archive_1_3.zip, archive_2_3.zip, archive_3_3.zip
        """
        if self.limit and count >= self.limit:
            return count, True
        if archive_name in self.done_archives:
            return count, False

        if not archive_path:
            archive_path = archive_name
        if not archive_url:
            archive_url = os.path.join(self.page_url, archive_path)

        index1 = -1
        index2 = -1
        for done_archive in self.done_archives:
            # check completed archives
            ind1 = done_archive.rfind("_")
            ind2 = done_archive.rfind("_", 0, ind1)
            if ind1 == -1 or ind2 == -1:
                continue
            index_to = done_archive[ind1+1:ind1+2]
            index_from = done_archive[ind2+1:ind2+2]

            index1 = int(index_from)
            index2 = int(index_to)

            if archive_name.replace(".zip", "") == done_archive[:ind2]:
                if index_from == index_to:
                    # this archive is fully processed (index equals max_index)
                    return count, False
                else:
                    # this archive is partially processed, we need to identify the next index
                    # to process
                    while(index1<10):
                        if self.check_slice_done(archive_name.replace(".zip", ""), index1):
                            # this index is already processed
                            index1+=1
                        else:
                            # this index is not processed yet, move on to its processing
                            break
                    if index1>9:
                        # this is a hard limit for the max number of slices for the same archive file
                        return count, False
            else:
                index1 = -1
                index2 = -1

        #if not self.rgx.match(archive_name):
        #    return count, False
        archive_dest = os.path.join(self.output_dir, archive_name)
        self.logger.info('>> downloading: %s to %s' % (archive_url, archive_dest))

        if cmd:
            cmd = cmd % (archive_url, self.output_dir)
            retry = 0
            limit_retry = self.cmd_retry_limit
            while True:
                try:
                    subprocess.check_call(cmd.split(' '))
                    break
                except Exception as e:
                    self.logger.warning("Error in %s: %s" % (cmd, e))
                    retry += 1
                    self.logger.info("Retry %s: %s" % (retry, cmd))
                    if retry == limit_retry:
                        raise e
            #os.rename(os.path.join(self.output_dir, archive_name), archive_dest)
            
        elif callback:
            callback(archive_dest_with_index, archive_url)
        
        count += 1

        # get the number of files in the archive and the max index for the archive
        # warning, we have a zip in a zip for autm archives
        if index2 == -1:
            local_count = 0
            with zipfile.ZipFile(archive_dest, "r") as zfile:
                for name in zfile.namelist():
                    if re.search(r'\.zip$', name) is not None:
                        # zip file in zip file
                        with zipfile.ZipFile(zfile.open(name)) as zfile2:
                            local_count = len(zfile2.namelist())
                            count+=local_count
                    else:
                        local_count+=1
            index2 = int(math.ceil(float(local_count)/self.chunk_size)) - 1
        if index1 == -1:
            index1 = 0

        archive_name_with_index = archive_name.replace(".zip", "_" + str(index1)+ "_" + str(index2)+ ".zip")
        archive_dest_with_index = os.path.join(self.output_dir, archive_name_with_index)

        # remove in the downloaded archive the files outside the considered slice,
        # this is necessary to avoid other pypers process to considered out of slice files
        local_count = 0
        local_full_count = 0
        in_slice = False
        with zipfile.ZipFile (archive_dest_with_index, 'w') as zout:
            with zipfile.ZipFile(archive_dest, "r") as zfile:
                for item0 in zfile.infolist():
                    name = item0.filename
                    if re.search(r'\.zip$', name) is not None:
                        with zipfile.ZipFile(zfile.open(name)) as zfile2:
                            for item in zfile2.infolist():
                                if local_full_count > (index1+1)*self.chunk_size:
                                    break;
                                if local_full_count < (index1)*self.chunk_size:
                                    local_full_count += 1
                                    continue
                                if local_count > self.chunk_size:
                                    break
                                buffer = zfile2.read(item.filename)
                                zout.writestr(item, buffer)
                                local_count += 1
                                local_full_count += 1
                    else:
                        # no zip in zip, this case could happen in the future
                        if local_full_count > (index1+1)*self.chunk_size:
                            break;
                        if local_full_count < (index1)*self.chunk_size:
                            local_full_count += 1
                            continue
                        if local_count > self.chunk_size:
                            break   
                        buffer = zfile2.read(item0.filename)
                        zout.writestr(item0, buffer)
                        local_count += 1
                        local_full_count += 1

        os.remove(os.path.join(self.output_dir, archive_name))

        self.logger.info('>> repackaging: %s to %s' % (os.path.join(self.output_dir, archive_name), archive_dest_with_index))
        self.output_files.append(archive_dest_with_index)
        if self.limit and count >= self.limit:
            return count, True
        return count, False

    def specific_http_auth_process(self, session):
        count = 0
        marks_page = session.get(self.page_url, proxies=self.proxy_params,
                                 auth=self.auth)
        marks_dom = BeautifulSoup(marks_page.text, 'html.parser')
        # find marks links
        a_elts = marks_dom.findAll('a', href=self.rgx)
        a_links = [a.attrs['href'] for a in a_elts]
        a_links.reverse()
        print(a_links)

        cmd = 'wget -q --user=%s --password=%s'
        cmd += ' %s --directory-prefix=%s'
        cmd = cmd % (self.conn_params['credentials']['user'],
                     self.conn_params['credentials']['password'],
                     '%s', '%s')
        for archive_name in a_links:
            count, should_break = self.parse_links(archive_name, count, cmd=cmd)
            if should_break:
                break

