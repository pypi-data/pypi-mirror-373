import os
import shutil
from pypers.utils.img import Convert as convert, \
    Generate as generate
from pypers.utils import img
from pypers.utils.utils import rename_file
from . import BaseHandler
import json

class GBDImage(BaseHandler):

    def _update_images(self, gbd_file, images):
        with open(gbd_file, 'r') as f:
            data = json.load(f)
        data['logos'] = images
        with open(gbd_file, 'w') as f:
            json.dump(data, f, indent=2)

    # self.img_files {'123': [{'ori': _}, {'ori: _'}], '234': [{'ori': _}]}
    def process(self, data_file, appnum):
        if not data_file:
            return
        st13 = data_file.get('st13', None)
        if not st13:
            return
        doc = data_file.get('doc')
        gbd_file = data_file.get('gbd')
        if not gbd_file:
            return
        logos = []
        data = data_file.get('imgs', [])
        if not data:
            self._update_images(gbd_file, logos)
            return

        _faded = []
        _corrupt = []
        _cropped = []
        # can have multiple images
        for idx, files in enumerate(data):
            if not files.get('ori', None):
                # Skip images that failed to download
                continue
            img_ori = os.path.join(self.extraction_dir, files['ori'])
            if not os.path.exists(img_ori):
                continue
            img_name, img_ext = os.path.splitext(os.path.basename(img_ori))

            # cv2 cannot work with gif => transform to png
            # convert gif to png
            # ------------------
            if img_ext.lower() == '.gif':
                img_ori = convert.from_gif(img_ori)
            elif img_ext.lower() == '.tif' or img_ext.lower() == '.tiff':
                img_ori = convert.from_tif(img_ori)

            # convert whatever the whatever-hi.%img_ext%
            # --------------------------------------------
            try:
                img_hgh = convert.to_hgh(img_ori, '%s-hi' % (img_name),
                                         img_ext='png')
            except Exception as e:
                _corrupt.append(appnum)
                continue

            # cropping image
            # --------------
            # -1: no change
            # 0: cropped
            # 1: faded
            # 2: corrupt
            try:
                result = img.crop(img_hgh, img_hgh)
                if result == 0:
                    _cropped.append(appnum)
                elif result == 1:
                    _faded.append(appnum)
                    continue
                elif result == 2:
                    _corrupt.append(appnum)
                    continue
            except Exception as e:
                _corrupt.append(appnum)
                continue

            # check if it is a zero-size image
            if os.stat(img_hgh).st_size == 0:
                _corrupt.append(appnum)
                continue

            # high image resize after crop
            # ----------------------------
            try:
                generate.high(img_hgh)
            except Exception as e:
                _corrupt.append(appnum)
                continue

            # high image generated => get its crc
            # -----------------------------------
            crc = img.get_crc(img_hgh)

            # rename high to use crc
            img_hgh = rename_file(img_hgh, '%s-hi' % crc)

            # generating thumbnail
            # --------------------
            try:
                img_thm = generate.thumbnail(img_hgh, crc)
            except Exception as e:
                _corrupt.append(appnum)
                self.logger.error('cannot generate thumbnail for %s' % img_ori)
                continue

            data[idx]['crc'] = crc

            data[idx]['ori'] = os.path.relpath(img_ori, self.extraction_dir)
            self.backup.store_img_ori(img_ori, st13, crc, hard=False)
            data[idx]['thum'] = os.path.relpath(img_thm, self.extraction_dir)
            self.backup.store_img_gbd(img_thm, st13, hard=True)
            data[idx]['high'] = os.path.relpath(img_hgh, self.extraction_dir)
            self.backup.store_img_gbd(img_hgh, st13, hard=False)

            doc['img_files'].append({
                'crc': crc,
                'img': img_hgh
            })
            logos.append(crc)
        self._update_images(gbd_file, logos)
