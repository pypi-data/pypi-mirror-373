import os
import re
import time
import ftplib
import socket
import subprocess

from pypers.utils import ftpw
from pypers.steps.base.fetch_step import FetchStep

class FTP_EM(FetchStep): 

    spec = {
        "version": "2.0",
        "descr": [
            "Fetch archives from either a local dir or FTP server"
        ],
        "args":
        {
            "params": [
                {
                    "name": "ftp_dir",
                    "type": "str",
                    "descr": "directory to look into. overrides the "
                             "pipeline input ftp_dir",
                    "value": ""
                },
                {
                    "name": 'no_sub_dirs',
                    "type": "int",
                    "value": 0
                 },
                {
                    "name": "use_wget",
                    "type": "int",
                    "descr": "force use of wget to retreive file",
                    "value": 0
                },
                {
                    "name": "sleep_secs",
                    "type": "int",
                    "descr": "secs to sleep to check if FTP dir is hot",
                    "value": 5
                }
            ]
        }
    }

    from_type = 'from_ftp'

    # This is a (hardcoded) date threshold for considering updates. Every update before this date will be ignored.
    # In pratice this is the date of the last global refresh.
    # Using it avoids to add hundred of done archives in dynamodb after a global refresh following a long
    # interrupted loading.
    from_date = '2025-01-21'
    
    # the folling normally is the same as the regex in group step, so we could add 
    # the regex as input parameter of this class
    date_pattern = r".*DIFF_.*_(\d{4})(\d{2})(\d{2}).*"

    def done_dates(self):
        """
        Translate done archives into list of done dates, to keep track of processed publication dates
        rather than individual archive names
        """
        done_dates = []
        for f in self.done_archives:
            # get the date
            matches = re.search(self.date_pattern, f)
            if matches == None:
                self.logger.warning("no matches for: ", f)
                continue
            groups = matches.groups()
            if len(groups) < 3:
                self.logger.warning("invalid number of matches: ", f)
                continue
            date = matches.group(1)+"-"+matches.group(2)+"-"+matches.group(3)
            if date not in done_dates:
                done_dates.append(date)
        return done_dates

    def specific_process(self):
        # getting files from ftp serverfiles_path
        ftp_params = self.fetch_from['from_ftp']
        self.output_files = []
        self.logger.info('getting %s files from ftp %s' % (
            'all' if self.limit == 0 else self.limit, ftp_params.get('ftp_server', '')))
        if ftp_params.get('ftp_passwd', None):
            self.logger.info('Connecting to %s:%s%s@%s/%s' % (
                ftp_params['ftp_user'],
                re.sub(r'.', '*', ftp_params['ftp_passwd'][:-4]),
                ftp_params['ftp_passwd'][-4:],
                ftp_params['ftp_server'],
                self.ftp_dir or ftp_params['ftp_dir']
            ))
        else:
            self.logger.info('Connecting to %s/%s' % (
                ftp_params['ftp_server'],
                self.ftp_dir or ftp_params['ftp_dir']
            ))

        ftp = ftplib.FTP(ftp_params['ftp_server'])
        ftp.login(ftp_params.get('ftp_user', ''), ftp_params.get('ftp_passwd', ''))
        ftp.cwd('/')

        # optimize socket params for download task
        # this is for the connected not to be dropped by the remote server
        # due in inactivity (noop every 1sec)

        ftp.sock.setsockopt(socket.SOL_SOCKET,  socket.SO_KEEPALIVE,   1)
        try:
            ftp.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE,  60)
        except Exception as e:
            # On mac os TCP_KEEPIDLE dose not exists.
            pass
        ftp.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 75)

        list_1 = []
        ftp.retrlines('LIST', list_1.append)
        time.sleep(self.sleep_secs)
        list_2 = []
        ftp.retrlines('LIST', list_2.append)

        if not list_1 == list_2:
            ftp.quit()
            raise Exception('FTP folder is HOT. Exit.')

        self.logger.info('FTP folder is cold. Moving on ...')

        ftp_dir = self.ftp_dir or ftp_params['ftp_dir']
        ftpwalk = ftpw.FTPWalk(ftp)

        # looks for files recursively
        flist = []
        r = re.compile(self.file_regex, re.IGNORECASE)
        for path, files in ftpwalk.walk(path=ftp_dir):
            for f in files:
                if r.match(f):
                    flist.append(os.path.join(path, f))

        # if we process a limited number of archives, we need to group and 
        # reorder files based on their dates in order to keep set of compatible files 
        # note that in this case, the limit number corresponds to the number of 
        # group of archives from the same date, not the number of individual archives

        date_map = {}                            
        for f in flist:
            # get the date
            matches = re.search(self.date_pattern, f)
            if matches == None:
                self.logger.warning("no matches for: ", f)
                continue
            groups = matches.groups()
            if len(groups) < 3:
                self.logger.warning("invalid number of matches: ", f)
                continue
            date = matches.group(1)+"-"+matches.group(2)+"-"+matches.group(3)

            if date <= self.from_date:
                continue

            if date not in date_map:
                date_map[date] = []
            if f not in date_map[date]:
                date_map[date].append(f)

        local_done_dates = self.done_dates()

        count = 0
        reversed = True
        if self.limit:
            reversed = False

        local_done_dates = self.done_dates()
        
        if self.use_wget:
            ftp.quit()  # done with ftp lib here
        else:
            ftp.set_debuglevel(2)
            ftp.voidcmd('TYPE I')
            ftp.set_pasv(True)
            ftp.cwd('/')

        for date in sorted(date_map.keys(), reverse=reversed):
            if self.limit and count >= self.limit:
                break
            if date in local_done_dates:
                continue
            #print(date, str(len(date_map[date])), "files at this date")
            for f in date_map[date]: 
                filename = os.path.basename(f)  # 123.zip
                filepath = os.path.relpath(f, ftp_dir)  # dir/123.zip

                #if self.no_sub_dirs and os.path.dirname(filepath) not in  ('', '/'):
                #    continue

                dest_dir = os.path.join(self.output_dir, os.path.dirname(filepath))
                dest_file = os.path.join(dest_dir, filename)

                try:
                    os.makedirs(dest_dir, exist_ok=True)
                except Exception as e:
                    self.logger.error("failed to create destination directory: ", dest_dir)
                    continue

                if self.use_wget:
                    cmd = 'wget -q --no-passive-ftp --ftp-user=%s ' \
                          '--ftp-password=%s ftp://%s%s -O %s' % (
                            ftp_params['ftp_user'],
                            ftp_params['ftp_passwd'],
                            ftp_params['ftp_server'],
                            os.path.join(ftp_dir, f),
                            dest_file)
                    self.logger.info('\nusing wget to retreive file')
                    self.logger.info('------------------------------')
                    self.logger.info('\n  '.join(cmd.split(' ')))
                    self.logger.info('------------------------------')
                    subprocess.check_call(cmd.split(' '))
                else:
                    res = ftp.retrbinary('RETR %s' % f, open(dest_file, 'wb').write)
                    self.logger.info(res)
                    if not res.startswith('226'):  
                        # 226 = success
                        os.remove(dest_file)
                        raise Exception('FTP failed to transfer successfully')
                self.output_files.append(dest_file)
            count += 1  

        if not self.use_wget:
            ftp.quit()
