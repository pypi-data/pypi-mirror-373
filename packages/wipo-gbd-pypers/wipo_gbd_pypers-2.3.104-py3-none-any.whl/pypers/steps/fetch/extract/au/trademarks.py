import json
import math
import requests
from pypers.steps.base.extract import ExtractBase


class Trademarks(ExtractBase):
    """
    Extract AUTM archive
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }

    slice_size = 60000

    # we get the data_files from archive extract
    # need to collect img urls for download
    def process(self):

        # divide appnums into chunks of 100
        appnum_list_full = list(self.manifest['data_files'].keys())

        # only consider a slice based on the index present in the done file or 0 if not present
        # and the slize size given as parameter
        archive_name = self.manifest['archive_file']

        ind1 = archive_name.rfind("_")
        ind2 = archive_name.rfind("_", 0, ind1)
        if ind1 == -1 or ind2 == -1:
            self.logger.error("index parsing issue: %s" % (archive_name))
            return

        index_to = archive_name[ind1+1:ind1+2]
        index_from = archive_name[ind2+1:ind2+2]

        index1 = -1
        index2 = -1

        try:
            index1 = int(index_from)
        except ValueError as e:
            self.logger.error("index parsing issue: %s: %s" % (index_from, e))

        try:
            index2 = int(index_to)
        except ValueError as e:
            self.logger.error("index parsing issue: %s: %s" % (index_to, e))

        max_bound = min((index1+1)*self.slice_size, len(appnum_list_full))
        #appnum_list = appnum_list_full[index1*self.slice_size:max_bound]

        appnum_list = appnum_list_full

        self.logger.info("processing %s records" % (str(len(appnum_list))))

        chunk_size = 100
        chunk_nb = int(math.ceil(float(len(appnum_list))/chunk_size))

        appnum_chunk_list = [
            appnum_list[i*chunk_size:i*chunk_size+chunk_size]
            for i in range(chunk_nb)]

        media_url = 'https://search.ipaustralia.gov.au/trademarks/external/' \
                    'api-v2/media?markId=%s'
        proxy_params, auth = self.get_connection_params('from_web')
        for appnum_chunk in appnum_chunk_list:
            with requests.session() as session:
                response = session.get(media_url % ','.join(appnum_chunk),
                                       proxies=proxy_params, auth=auth)
                medias = json.loads(response.content)

                for media in medias:
                    appnum = media['markId']
                    for idx, img in enumerate(media.get('images', [])):
                        self.add_img_url(appnum, img['location'])

