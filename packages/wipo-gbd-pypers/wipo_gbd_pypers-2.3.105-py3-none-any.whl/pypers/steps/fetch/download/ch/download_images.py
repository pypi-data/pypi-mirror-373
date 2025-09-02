from pypers.steps.fetch.common import DownloadIMG as PDownloadIMG

from . import get_auth_token
import requests
import time 
from requests.adapters import HTTPAdapter, Retry

class DownloadIMG(PDownloadIMG):
    token = None

    def lazy_get_auth_token(self, force=False):
        self.fetch_from = self.meta['pipeline']['input']
        if self.token == None or force:
            self.conn_params = self.fetch_from["from_api"]
            self.token = get_auth_token(self.conn_params)
        return self.token

    def do_download(self, uri, dest):
        proxy_params = {
            'http':  self.meta['pipeline']['input'].get('http_proxy', None),
            'https': self.meta['pipeline']['input'].get('https_proxy', None)
        }
        try:
            token = self.lazy_get_auth_token()
        except Exception as e: 
            return { "error": str(e) }
        header = {
            'Authorization': 'Bearer ' + token
        }
        try:
            time.sleep(.2)
            s = requests.Session()
            retries = Retry(total=5,
                            backoff_factor=0.2)
            s.mount('https://', HTTPAdapter(max_retries=retries))
            resp = s.get(uri, headers=header, proxies=proxy_params, stream=True, verify=False)
            #resp = requests.get(uri, headers=header, proxies=proxy_params, stream=True, verify=False)

            if resp.status_code == 200:
                with open(dest, 'wb') as f:
                    for chunk in resp:
                        f.write(chunk)
                return dest
            elif resp.status_code == 401 or resp.status_code == 403:
                # update authentication token
                try:
                    token = self.lazy_get_auth_token(force=True)
                except Exception as e:
                    result = { "error": str(e) }
                    token = None

                if token != None:
                    return self.do_download(uri, dest)
            elif response.status_code == 429:
                self.logger.error('image - quota limit exceeded')
            else:
                self.logger.error("Image downloading problem in %s: %d" % (uri, resp.status_code))
        except Exception as e: 
            self.logger.error("Image downloading problem in %s: %s" % (uri, e))
        return None


        
