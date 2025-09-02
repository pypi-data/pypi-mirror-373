import os

import requests
import xmltodict
import json
import time
from pypers.core.interfaces import db
from pypers.steps.base.extract import ExtractBase
import concurrent.futures


class TrademarksAPI(ExtractBase):
    """
    Extract GBTM archive
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

    def collect_files(self, file):
        f_name, ext = os.path.splitext(os.path.basename(file))
        self.add_xml_file(f_name, file)

    def unpack_archive(self, archive, dest):
        return archive

    def process_record(self, appNum):
        xml_dir = os.path.join(self.extraction_dir, 'xml')
        url = 'https://soap.ipo.gov.uk/trademark/data/%s' % appNum
        mapping = {
            'applicants': 'applicant',
            'representatives': 'representative'
        }
        namespaces = {
            'http://gb.tmview.europa.eu/trademark/data': None,
            'http://gb.tmview.europa.eu/trademark/applicant': None,
            'http://gb.tmview.europa.eu/trademark/representative': None
        }
        try:
            time.sleep(0.1)
            with requests.session() as session:
                raw_doc_data = session.get(url, timeout=0.8).content
                doc_data = xmltodict.parse(raw_doc_data,
                                           process_namespaces=True,
                                           namespaces=namespaces,
                                           namespace_separator='_',
                                           attr_prefix='_',
                                           cdata_key='__value')
                for type in ['applicants', 'representatives']:
                    address_path = doc_data.get('Transaction', {}).get('TradeMarkTransactionBody', {}).get(
                        'TransactionContentDetails', {}).get('TransactionData', {}).get('TradeMarkDetails', {}).get(
                        'TradeMark', {}).get('%sDetails' % mapping[type].capitalize(), {})
                    if not address_path:
                        continue
                    if not isinstance(address_path, list):
                        address_path = [address_path]
                    to_replace = doc_data.get('Transaction', {}).get('TradeMarkTransactionBody', {}).get(
                        'TransactionContentDetails', {}).get('TransactionData', {}).get('TradeMarkDetails', {}).get(
                        'TradeMark', {})
                    to_replace['%sDetails' % mapping[type].capitalize()] = []
                    for addr in address_path:
                        url = addr.get('%sKey' % mapping[type].capitalize(), {}).get('URI', None)
                        address_data = session.get(url, timeout=0.8).content
                        address_data = xmltodict.parse(address_data,
                                                       process_namespaces=True,
                                                       namespaces=namespaces,
                                                       namespace_separator='_',
                                                       attr_prefix='_',
                                                       cdata_key='__value')
                        address_data = address_data.get('Transaction', {}).get('TradeMarkTransactionBody', {}).get(
                            'TransactionContentDetails', {}).get('TransactionData', {}).get(
                            '%sDetails' % mapping[type].capitalize(), {}).get(mapping[type].capitalize(), {})
                        to_replace['%sDetails' % mapping[type].capitalize()].append(address_data)
                doc_data = doc_data.get('Transaction', {}).get('TradeMarkTransactionBody', {}).get(
                    'TransactionContentDetails', {}).get('TransactionData', {}).get('TradeMarkDetails', {})
                appxml_file = os.path.join(xml_dir, '%s.json' % appNum)
                with open(appxml_file, 'w') as f:
                    f.write(json.dumps(doc_data))

                self.manifest['data_files'].setdefault(appNum, {})
                self.manifest['data_files'][appNum]['ori'] = os.path.relpath(
                    appxml_file, self.extraction_dir)
                return appNum
        except Exception as e:
            self.logger.error("error for %s - %s " % (appNum, e))
            return None

    def _sub_arry_offset(self, max_paralel, length, offset):
        if offset + max_paralel < length:
            return offset + max_paralel
        return length

    def worker_parallel(self, items, caller, *args, **kwargs):
        max_workers = 3

        task_counter = 0
        # Make the list an iterator, so the same tasks don't get run repeatedly.

        with concurrent.futures.ThreadPoolExecutor() as executor:

            # Schedule the initial batch of futures.  Here we assume that
            # max_scans_in_parallel < total_segments, so there's no risk that
            # the queue will throw an Empty exception.
            futures = {
                executor.submit(caller, item, *args, **kwargs): item
                for item in items[task_counter:self._sub_arry_offset(
                    max_workers, len(items), task_counter)]
            }
            task_counter = len(futures)
            while futures:
                # Wait for the first future to complete.
                done, _ = concurrent.futures.wait(
                    futures, return_when=concurrent.futures.FIRST_COMPLETED
                )
                for fut in done:
                    res = fut.result()
                    futures.pop(fut)
                    yield res
                # Schedule the next batch of futures.  At some point we might run out
                # of entries in the queue if we've finished scanning the table, so
                # we need to spot that and not throw.
                for item in items[task_counter:self._sub_arry_offset(
                        len(done), len(items), task_counter)]:
                    task_counter += 1
                    futures[executor.submit(caller, item, *args, **kwargs)] = item

    def add_xml_file(self, filename, fullpath):
        xml_dir = os.path.join(self.extraction_dir, 'xml')
        if not os.path.exists(xml_dir):
            os.makedirs(xml_dir)
        with open(fullpath, 'r') as f:
            st13s = json.loads(f.read())

        st13_ok = []
        for entry in self.worker_parallel(st13s, self.process_record):
            if entry:
                st13_ok.append(entry)
        db.get_db_dirty().delete_items('gb', st13_ok)

    def process(self):
        pass