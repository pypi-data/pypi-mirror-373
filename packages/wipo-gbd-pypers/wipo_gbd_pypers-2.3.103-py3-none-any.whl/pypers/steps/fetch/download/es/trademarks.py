import os
import shutil
import datetime
import time

from pypers.steps.base.fetch_step_http import FetchStepHttpAuth

class Trademarks(FetchStepHttpAuth):
    spec = {
        "version": "2.0",
        "descr": [
            "Fetch using HTTP with Basic Auth"
        ],
    }

    def daterange(self, start_date, end_date):
        days = int((end_date - start_date).days)
        for n in range(days):
            yield start_date + datetime.timedelta(n+1)

    def get_intervals(self):
        """ 
        Return the intervals to be downloaded, in our case one interval is one day, so
        we enumerate days from the day of the last update 
        """
        # get the date of the last update
        if not len(self.done_archives):
            # no done archives in dynamodb table gbd_pypers_done_archive 
            last_update = (datetime.datetime.today() - datetime.timedelta(1))
        else:
            # we get the day of the last update from the last "done_archive" file name stored 
            # in dynamodb table gbd_pypers_done_archive 
            # # expecting names like : 20180107.zip
            last_update = sorted(self.done_archives)[-1].split('.')[0]
            last_update = last_update[0:4]+"-"+last_update[4:6]+"-"+last_update[6:]
            last_update = datetime.datetime.fromisoformat(last_update)

        today = datetime.datetime.today()

        result = []
        current_date = last_update.strftime("%Y-%m-%d")

        for one_date in self.daterange(last_update, today):
            next_date = one_date.strftime("%Y-%m-%d")
            result.append( (current_date, next_date) )
            current_date = next_date

        print(result)
        return result

    # https://sede.oepm.gob.es/eSede/datos/es/catalogo/descargar.jsp?u=INVENCIONES/FULLTEXT_XML/2020/09/11/FULLTEXT_XML_20200911.zip&t=zt5m6H9Mye04E3uwJGUdsPxDyACK7mUwMJqivRKEyaIfxPblKFd9WAU6cux1xt7X
    # https://sede.oepm.gob.es/eSede/datos/en/catalogo/descargar.jsp?u=MARCAS/BIBLIO/2025/08/02/20250802.zip
    """
        "from_web": {
            "url": "https://sede.oepm.gob.es/eSede/datos/en/catalogo/descargar.jsp?u=MARCAS/BIBLIO",
            "token": "zt5m6H9Mye04E3uwJGUdsPxDyACK7mUwMJqivRKEyaIfxPblKFd9WAU6cux1xt7X"
        }
    """

    def specific_http_auth_process(self, session):
        count = 0
        session.verify = False

        base_url = self.conn_params['url']
        token = self.conn_params['token']

        self.intervals = self.get_intervals()

        if self.intervals is None:
            return
        nb_intervals_processed = 0
        for interval in self.intervals:
            if self.limit and nb_intervals_processed == self.limit:
                break
            print("download interval:", interval)

            interval_piece = interval[1].split("-")
            url = base_url + "/" + interval_piece[0] + "/" + interval_piece[1] + "/" + interval_piece[2] + "/" + interval[1].replace("-", "") + ".zip&t=" + token
            save_path = os.path.join(self.output_dir, interval[1].replace("-", "") + ".zip")

            chunk_size = 128
            r = session.get(url, stream=True, verify=False)
            with open(save_path, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    fd.write(chunk)

            self.output_files.append(save_path)
            nb_intervals_processed += 1


