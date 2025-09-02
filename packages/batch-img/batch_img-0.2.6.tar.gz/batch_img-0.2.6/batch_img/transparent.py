"""class Transparent: set transparency on image file(s)
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


class Transparent:
    @staticmethod
    def set_white_pixel_transparent(img: Image.Image) -> None:
        """Set white pixels in RGBA image transparent in-place
        Non PNG white pixels Err: not enough values to unpack (expected 4, got 3)

        Args:
            img: RGBA image

        Returns:
            None
        """
        new_data = []
        for t_pixel in img.getdata():
            if len(t_pixel) == 4:
                r, g, b, a = t_pixel
                if (r, g, b) == (255, 255, 255):
                    new_data.append((r, g, b, 0))
                else:
                    new_data.append((r, g, b, a))
            else:
                # Fallback in case of RGB pixel (shouldn't happen after convert)
                r, g, b = t_pixel
                if (r, g, b) == (255, 255, 255):
                    new_data.append((r, g, b, 0))
                else:
                    new_data.append((r, g, b, 255))
        img.putdata(new_data)

    @staticmethod
    def set_transparency(img: Image.Image, transparency: int) -> None:
        """Set RGBA image transparency in-place

        Args:
            img: RGBA image
            transparency: 0 (fully transparent) <= int <= 255 (completely opaque)

        Returns:
            None
        """
        new_data = []
        for t_pixel in img.getdata():
            if len(t_pixel) == 4:
                r, g, b, _ = t_pixel
            else:
                r, g, b = t_pixel
            new_data.append((r, g, b, transparency))
        img.putdata(new_data)

    @staticmethod
    def do_1_image_transparency(args: tuple) -> tuple:
        """Set transparency on an image file.
        If the input file is JPEG, it will be saved as PNG file because JPEG does
        not support transparency

        Args:
            args: tuple of the below params:
            in_path: input file path
            out_path: output dir path or REPLACE
            transparency: 0 (fully transparent) <= int <= 255 (completely opaque)
            white: flag to make white pixels full transparent

        Returns:
            tuple: bool, str
        """
        in_path, out_path, transparency, white = args
        Common.set_log_by_process()
        try:
            with Image.open(in_path) as img:
                a_img = img.convert("RGBA")
                Transparent.set_transparency(a_img, transparency)
                extra = f"a{transparency}"
                if white:
                    Transparent.set_white_pixel_transparent(a_img)
                    extra = f"a{transparency}w"
                file = Common.set_out_file(in_path, out_path, extra)
                i_format = img.format
                if i_format == "JPEG":
                    i_format = "PNG"
                    file = Path(f"{file.parent}/{file.stem}.png")
                    log.debug(f"Revised {file=}")
                if EXIF in img.info:
                    exif_dict = piexif.load(img.info[EXIF])
                    exif_bytes = piexif.dump(exif_dict)
                    a_img.save(file, format=i_format, optimize=True, exif=exif_bytes)
                else:
                    a_img.save(file, format=i_format, optimize=True)
            log.debug(f"Saved transparent image to {file}")
            if out_path == REPLACE:
                os.replace(file, in_path)
                log.debug(f"Replaced {in_path} with the new tmp_file")
                file = in_path
            return True, file
        except (AttributeError, FileNotFoundError, ValueError) as e:
            log.error(e)
            return False, f"{in_path}:\n{e}"

    @staticmethod
    def all_images_transparency(
        in_path: Path, out_path: Path | str, transparency: int, white: bool
    ) -> bool:
        """Set transparency on all image files in a folder.
        If the input file is JPEG, it will be saved as PNG file because JPEG does
        not support transparency

        Args:
            in_path: input file path
            out_path: output dir path or REPLACE
            transparency: 0 (fully transparent) <= int <= 255 (completely opaque)
            white: flag to make white pixels full transparent

        Returns:
            bool: True - Success. False - Error
        """
        image_files = Common.prepare_all_files(in_path, out_path)
        tasks = [(f, out_path, transparency, white) for f in image_files]
        files_cnt = len(tasks)
        if files_cnt == 0:
            log.error(f"No image files at {in_path}")
            return False

        log.debug(f"Set transparency on {files_cnt} image files in multiprocess ...")
        success_cnt = Common.multiprocess_progress_bar(
            Transparent.do_1_image_transparency, "Set transparency", files_cnt, tasks
        )
        log.info(f"\nDone - set transparency on {success_cnt}/{files_cnt} files")
        return True
