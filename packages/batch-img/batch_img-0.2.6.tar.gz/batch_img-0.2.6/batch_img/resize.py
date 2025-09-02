"""class Resize: resize the image file(s)
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


class Resize:
    @staticmethod
    def resize_an_image(args: tuple) -> tuple:
        """Resize an image file and save to the output dir

        Args:
            args: tuple of the below params:
            in_path: input file path
            out_path: output dir path or REPLACE
            length: max pixels length (width or height)

        Returns:
            tuple: bool, output file path
        """
        in_path, out_path, length = args
        Common.set_log_by_process()
        try:
            with Image.open(in_path) as img:
                width, height = img.size
                new_size = Common.calculate_new_size(width, height, length)
                new_img = img.resize(new_size, Image.Resampling.LANCZOS, reducing_gap=3)

                # thumbnail() keep the aspect ratio, but shrink only, not enlarge
                # img.thumbnail((length, length), Image.Resampling.LANCZOS)

                file = Common.set_out_file(in_path, out_path, f"{length}")
                if EXIF in img.info:
                    exif_dict = piexif.load(img.info[EXIF])
                    exif_bytes = piexif.dump(exif_dict)
                    new_img.save(file, img.format, optimize=True, exif=exif_bytes)
                else:
                    new_img.save(file, img.format, optimize=True)
            log.debug(f"Saved resized image to {file}")
            if out_path == REPLACE:
                os.replace(file, in_path)
                log.debug(f"Replaced {in_path} with the new tmp_file")
                file = in_path
            return True, file
        except (AttributeError, FileNotFoundError, ValueError) as e:
            log.error(e)
            return False, f"{in_path}:\n{e}"

    @staticmethod
    def resize_all_progress_bar(
        in_path: Path, out_path: Path | str, length: int
    ) -> bool:
        """Resize all image files in the given dir

        Args:
            in_path: input dir path
            out_path: output dir path or REPLACE
            length: max length (width or height) in pixels

        Returns:
            bool: True - Success. False - Error
        """
        image_files = Common.prepare_all_files(in_path, out_path)
        tasks = [(f, out_path, length) for f in image_files]
        files_cnt = len(tasks)
        if files_cnt == 0:
            log.error(f"No image files at {in_path}")
            return False

        log.debug(f"Resize {files_cnt} image files in multiprocess ...")
        success_cnt = Common.multiprocess_progress_bar(
            Resize.resize_an_image, "Resize image files", files_cnt, tasks
        )
        log.info(f"\nSuccessfully resized {success_cnt}/{files_cnt} files")
        return True
