"""class Rotate: rotate image file(s) to clockwise angle
Copyright © 2025 John Liu
"""

import os
from pathlib import Path

import piexif
import pillow_heif
from loguru import logger as log
from PIL import Image

from batch_img.common import Common
from batch_img.const import EXIF, REPLACE

pillow_heif.register_heif_opener()


class Rotate:
    @staticmethod
    def rotate_1_image(args: tuple) -> tuple:
        """Rotate an image file and save to the output dir

        Args:
            args: tuple of the below params:
            in_path: input file path
            out_path: output dir path or REPLACE
            angle_cw: rotation angle clockwise: 90, 180, or 270

        Returns:
            tuple: bool, str
        """
        in_path, out_path, angle_cw = args
        Common.set_log_by_process()
        if angle_cw == 0:
            log.debug(f"No rotate as {angle_cw=}")
            return False, in_path
        if angle_cw not in {90, 180, 270}:
            return False, f"Bad {angle_cw=}. Only allow 90, 180, 270"
        try:
            with Image.open(in_path) as img:
                exif_dict = {"0th": {}, "Exif": {}}
                if EXIF in img.info:
                    exif_dict = piexif.load(img.info[EXIF])
                exif_dict["0th"][piexif.ImageIFD.Orientation] = 1
                exif_bytes = piexif.dump(exif_dict)

                file = Common.set_out_file(in_path, out_path, f"{angle_cw}cw")
                # img.rotate() for any angle (slower & slight quality loss)
                rotated_img = img
                if angle_cw == 90:
                    rotated_img = img.transpose(Image.ROTATE_270)
                elif angle_cw == 180:
                    rotated_img = img.transpose(Image.ROTATE_180)
                elif angle_cw == 270:
                    rotated_img = img.transpose(Image.ROTATE_90)

                rotated_img.save(file, img.format, exif=exif_bytes, optimize=True)
            log.debug(f"Saved ({angle_cw}°) clockwise rotated to {file}")
            if out_path == REPLACE:
                os.replace(file, in_path)
                log.debug(f"Replaced {in_path} with the new tmp_file")
                file = in_path
            return True, file
        except (AttributeError, FileNotFoundError, ValueError) as e:
            log.error(e)
            return False, f"{in_path}:\n{e}"

    @staticmethod
    def rotate_all_in_dir(in_path: Path, out_path: Path | str, angle_cw: int) -> bool:
        """Rotate all image files in the given dir

        Args:
            in_path: input dir path
            out_path: output dir path or REPLACE
            angle_cw: rotation angle clockwise: 90, 180, or 270

        Returns:
            bool: True - Success. False - Error
        """
        if angle_cw not in {90, 180, 270}:
            log.error(f"Bad {angle_cw=}. Only allow 90, 180, 270")
            return False
        image_files = Common.prepare_all_files(in_path, out_path)
        tasks = [(f, out_path, angle_cw) for f in image_files]
        files_cnt = len(tasks)
        if files_cnt == 0:
            log.error(f"No image files at {in_path}")
            return False

        log.debug(f"Rotate {files_cnt} image files in multiprocess ...")
        success_cnt = Common.multiprocess_progress_bar(
            Rotate.rotate_1_image, "Rotate image files", files_cnt, tasks
        )
        log.info(f"\nSuccessfully rotated {success_cnt}/{files_cnt} files")
        return True
