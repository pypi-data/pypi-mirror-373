"""class Border: add border to the image file(s)
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


class Border:
    @staticmethod
    def border_1_image(args: tuple) -> tuple:
        """Add internal border to an image file, not to expand the size

        Args:
            args: tuple of the below params:
            in_path: input file path
            out_path: output dir path or REPLACE
            bd_width: border width int
            bd_color: border color str

        Returns:
            tuple: bool, str
        """
        in_path, out_path, bd_width, bd_color = args
        Common.set_log_by_process()
        try:
            with Image.open(in_path) as img:
                width, height = img.size
                box = Common.get_crop_box(width, height, bd_width)
                cropped_img = img.crop(box)
                bd_img = Image.new(img.mode, (width, height), bd_color)
                bd_img.paste(cropped_img, (bd_width, bd_width))

                file = Common.set_out_file(in_path, out_path, f"bw{bd_width}")
                if EXIF in img.info:
                    exif_dict = piexif.load(img.info[EXIF])
                    exif_bytes = piexif.dump(exif_dict)
                    bd_img.save(file, img.format, optimize=True, exif=exif_bytes)
                else:
                    bd_img.save(file, img.format, optimize=True)
            log.debug(f"Saved image with border to {file}")
            if out_path == REPLACE:
                os.replace(file, in_path)
                log.debug(f"Replaced {in_path} with the new tmp_file")
                file = in_path
            return True, file
        except (AttributeError, FileNotFoundError, ValueError) as e:
            log.error(e)
            return False, f"{in_path}:\n{e}"

    @staticmethod
    def border_all_in_dir(
        in_path: Path, out_path: Path | str, bd_width: int, bd_color: str
    ) -> bool:
        """Add border to all image files in the given dir

        Args:
            in_path: input dir path
            out_path: output dir path or REPLACE
            bd_width: border width int
            bd_color: border color str

        Returns:
            bool: True - Success. False - Error
        """
        image_files = Common.prepare_all_files(in_path, out_path)
        tasks = [(f, out_path, bd_width, bd_color) for f in image_files]
        files_cnt = len(tasks)
        if files_cnt == 0:
            log.error(f"No image files at {in_path}")
            return False

        log.debug(f"Add border to {files_cnt} image files in multiprocess ...")
        success_cnt = Common.multiprocess_progress_bar(
            Border.border_1_image, "Add border to image files", files_cnt, tasks
        )
        log.info(f"\nSuccessfully added border to {success_cnt}/{files_cnt} files")
        return True
