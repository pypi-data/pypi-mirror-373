"""class NoGps - Remove GPS location info in image file(s)
Copyright © 2025 John Liu
"""

import os
from pathlib import Path

import pillow_heif
from loguru import logger as log
from PIL import Image

from batch_img.common import Common
from batch_img.const import EXIF, REPLACE

pillow_heif.register_heif_opener()


class NoGps:
    @staticmethod
    def remove_1_image_gps(args: tuple) -> tuple:
        """Remove GPS location info in an image file

        Args:
            args: tuple of the below params:
            in_path: input file path
            out_path: output dir path or REPLACE

        Returns:
            tuple: bool, output file path
        """
        in_path, out_path = args
        Common.set_log_by_process()
        try:
            with Image.open(in_path) as img:
                if EXIF not in img.info:
                    msg = f"Skip as no EXIF in {in_path}"
                    log.debug(msg)
                    return True, f"Skip as no EXIF in {in_path}"
                removed, exif_bytes = Common.remove_exif_gps(img.info[EXIF])
                if removed:
                    file = Common.set_out_file(in_path, out_path, "NoGPS")
                    img.save(file, img.format, optimize=True, exif=exif_bytes)
                else:
                    msg = f"No 'GPS' in EXIF of {in_path}"
                    log.debug(msg)
                    return True, msg

            log.debug(f"Saved the no GPS info image to {file}")
            if out_path == REPLACE:
                os.replace(file, in_path)
                log.debug(f"Replaced {in_path} with the new tmp_file")
                file = in_path
            return True, file
        except (AttributeError, FileNotFoundError, ValueError) as e:
            log.error(e)
            return False, f"{in_path}:\n{e}"

    @staticmethod
    def remove_all_images_gps(in_path: Path, out_path: Path | str) -> bool:
        """Remove GPS info in all image files in the given dir

        Args:
            in_path: input dir path
            out_path: output dir path or REPLACE

        Returns:
            bool: True - Success. False - Error
        """
        image_files = Common.prepare_all_files(in_path, out_path)
        tasks = [(f, out_path) for f in image_files]
        files_cnt = len(tasks)
        if files_cnt == 0:
            log.error(f"No image files at {in_path}")
            return False

        log.debug(f"Remove GPS info in {files_cnt} image files in multiprocess ...")
        success_cnt = Common.multiprocess_progress_bar(
            NoGps.remove_1_image_gps, "Remove GPS in image files", files_cnt, tasks
        )
        log.info(f"\nSuccessfully removed GPS in {success_cnt}/{files_cnt} files")
        return True
