import os
import json
import subprocess
import requests
from pypers.core.interfaces import db
from . import BaseHandler

class Analyze(BaseHandler):
    skip_analyze_verbal_images = 'emtm, frtm, krtm, vntm'

    def analyze(self, items):
        img_files_for_analysis = []
        for item in items:
            data_file, appnum = item
            img_files_for_analysis.extend(self.process(data_file, appnum))

        # IMAGEANALYSIS STARTS HERE
        # -------------------------
        self.logger.debug('[ANALYZE][START] // %s image files to analyze' % len(img_files_for_analysis))
        # write fofn file
        fofn_file = os.path.join(self.extraction_dir, 'images.fofn')
        os.makedirs(os.path.dirname(fofn_file), exist_ok=True)
        with open(fofn_file, 'w') as f:
            f.write('\n'.join(img_files_for_analysis))

        self._run_analyze_command(fofn_file)
        for item in items:
            data_file, appnum = item
            record = data_file.get('doc', {})
            # loop records to find images with analysis files present
            lire_data = []

            for img_info in record.get('img_files', []):
                if img_info['img'] not in img_files_for_analysis:
                    continue
                img_path = os.path.dirname(img_info['img'])
                img_name = os.path.basename(img_info['img'])

                img_analysis_file = os.path.join(img_path,
                                                 img_name.replace('.png', '.json'))
                if not os.path.exists(img_analysis_file):
                    continue
                try:
                    with open(img_analysis_file, 'r') as f:
                        lire_data_img = json.loads(f.read())
                except Exception as e:
                    self.logger.error('Analysis failed for %s' % img_path)
                    continue
                # a newly analysed image !
                lire_data.append(lire_data_img)
                # done with image file
                # PL: for debug comment next line
                os.remove(img_analysis_file)
                # In order to keep the -hi.
                # os.remove(img_info['img'])
            if not lire_data:
                continue
            record['data_files']['latest']['image_analysis'] = lire_data
        os.remove(fofn_file)


    def process(self, data_file, appnum):
        if not data_file.get('doc', None):
            return []
        self.img_files = []
        img_files_for_analysis = []
        record = data_file.get('doc', {})

        # no images => move on
        if not len(record.get('img_files', [])):
            return []
        # read feature from record
        feature = record.get('feature')
        # PL: above is a bug, the field is called markFeature in gbd docs
        if feature == None:
            feature = record.get("markFeature")

        # read image_analysis from latest
        latest_data = record['data_files']['latest']
        latest_img_analysis = latest_data.get('image_analysis', [])

        for img_info in record['img_files']:
            img_file = img_info['img']

            is_analysed = self._is_analysed(img_info['crc'],
                                            latest_img_analysis)
            is_skipped = self._skip_feature(feature)

            # will not analyse image => remove
            if is_analysed or is_skipped:
                try:
                    os.remove(img_file)
                except:
                    pass
                continue

            img_files_for_analysis.append(img_file)
        return img_files_for_analysis

    def _is_analysed(self, crc, latest_img_analysis):
        # PL: if image analysis has failed due to LIRE vector missing, we want the
        # image analysis to be re-calculated
        for img in latest_img_analysis:
            if img == None:
                # it should never happen, but it happens
                self.logger.error("empty image in latest imageanalysis")
                continue
            if img.get('crc') == crc:
                if not "imgDescShape" in img or not "imgDescColor" in img or not "imgDescComposite" in img or not "imgDescConcept" in img:
                    return False
                if img.get("imgDescShape") == None or img.get("imgDescColor") == None or img.get("imgDescComposite") == None or img.get("imgDescConcept") == None:
                    return False
                # the two next ones just to be sure to cover every weird possibilities:
                if img.get("imgDescShape") == "null" or img.get("imgDescColor") == "null" or img.get("imgDescComposite") == "null" or img.get("imgDescConcept") == "null":
                    return False
                if img.get("imgDescShape") == "Null" or img.get("imgDescColor") == "Null" or img.get("imgDescComposite") == "Null" or img.get("imgDescConcept") == "Null":
                    return False
                return True
        return False

    def _skip_feature(self, feature):
        return feature == 'Word' and self.collection in self.skip_analyze_verbal_images

    def _run_analyze_command(self, fofn_file):
        jar_file = os.environ.get('IMAGEANALYSIS_JAR').strip()
        conf_url = os.environ.get('IMAGEANALYSIS_CONF_URL', '').strip()
        atac_url = os.environ.get('IMAGEANALYSIS_CLASSIF_ENDPOINT', '').strip()
        cmd = "java -jar %s analyzer --configuration %s --type %s --atac %s --fofn %s --threads 3 --outputContent index"
        cmd = cmd % (jar_file,
                     conf_url,
                     self.pipeline_type,
                     atac_url,
                     fofn_file)
        print(cmd)
        proc = subprocess.Popen(cmd.split(' '),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                close_fds=True)
        stdout, stderr = proc.communicate()

        rc = proc.returncode

        if rc != 0:
            self.logger.error(str(stderr))
            db.get_db_error().send_error(self.run_id,
                                         self.collection,
                                         {'source': 'image_analysis'},
                                         "%s %s" % (str(stdout), str(stderr)))
            raise Exception('Image analysis failed')
