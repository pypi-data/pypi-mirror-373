"""class Common: common utilities
Copyright © 2025 John Liu
"""

import importlib.metadata
import itertools
import json
import subprocess
import tomllib
from base64 import b64encode
from datetime import datetime
from multiprocessing import Pool, cpu_count, current_process
from os.path import getmtime, getsize
from pathlib import Path
from time import time

import httpx
import piexif
import pillow_heif
from loguru import logger as log
from packaging import version  # compare versions safely
from PIL import Image, ImageChops
from PIL.TiffImagePlugin import IFDRational
from tqdm import tqdm

from batch_img.const import (
    EXIF,
    EXPIRE_HOUR,
    PATTERNS,
    PKG_NAME,
    REPLACE,
    TS_FORMAT,
    UNKNOWN,
    VER,
)
from batch_img.log import Log

pillow_heif.register_heif_opener()
VER_CACHE = Path(f"~/.{PKG_NAME}_version_cache.json").expanduser()


class Common:
    @staticmethod
    def get_version(pkg_name: str) -> str:
        """Get this package version by various ways

        Args:
            pkg_name: package name str

        Returns:
            str:
        """
        try:
            return importlib.metadata.version(pkg_name)
        except (FileNotFoundError, ImportError, ValueError) as e:
            log.warning(f"importlib.metadata.version() Error: {e}")
            log.debug("Get version from pyproject.toml file")
            pyproject = Path(__file__).parent.parent / "pyproject.toml"
            with open(pyproject, "rb") as f:
                return tomllib.load(f)["project"][VER]

    @staticmethod
    def get_latest_pypi_ver(pkg_name: str, expire_hr: int = EXPIRE_HOUR):
        """Get the package latest version on PyPI with local cache

        Args:
            pkg_name: package name str
            expire_hr: cache expiration hour int

        Returns:
            str: latest version on PyPI
        """
        jsn_url = f"https://pypi.org/pypi/{pkg_name}/json"
        latest_ver = ""
        try:
            if pkg_name in str(VER_CACHE) and VER_CACHE.exists():
                with open(VER_CACHE, encoding="utf-8") as f:
                    cache = json.load(f)
                    if time() - cache["timestamp"] < expire_hr * 3600:
                        latest_ver = cache["version"]
            if not latest_ver:
                response = httpx.get(jsn_url, timeout=5)
                if response.status_code != 200:
                    msg = f"⚠️ Error get data from PyPI: {jsn_url}"
                    log.error(msg)
                    return UNKNOWN
                latest_ver = response.json()["info"]["version"]
                d_cache = {"timestamp": int(time()), "version": latest_ver}
                with open(VER_CACHE, "w", encoding="utf-8") as f:
                    json.dump(d_cache, f)
            return latest_ver
        except (httpx.RequestError, KeyError, json.JSONDecodeError) as e:
            raise e

    @staticmethod
    def check_latest_version(pkg_name: str) -> str:
        """Check if the installed version is the latest one

        Args:
            pkg_name: package name str

        Returns:
            str
        """
        msg = ""
        try:
            latest_ver = Common.get_latest_pypi_ver(pkg_name)
            cur_ver = Common.get_version(pkg_name)
            if version.parse(cur_ver) < version.parse(latest_ver):
                msg = (
                    f"🔔 Update available: {cur_ver}  →  {latest_ver}\n"
                    f"Run '{pkg_name} --update'"
                )
                log.info(msg)
        except (httpx.RequestError, KeyError, json.JSONDecodeError) as e:
            msg = f"Error get PyPI data: {e}"
            log.error(msg)
        return msg

    @staticmethod
    def update_package(pkg_name: str) -> str:
        """Update the package to the latest version

        Args:
            pkg_name: package name str

        Returns:
            str
        """
        Log.init_log_file()
        msg = Common.check_latest_version(pkg_name)
        if "Update available" not in msg:
            return msg
        log.info(f"🔄 Updating {pkg_name} ...")
        cmd = f"uv pip install --upgrade {pkg_name}"
        try:
            Common.run_cmd(cmd)
            msg = "✅ Update completed."
            log.info(msg)
        except subprocess.CalledProcessError as e:
            msg = f"❌ Update {pkg_name}: {e}"
            log.error(msg)
        return msg

    @staticmethod
    def run_cmd(cmd: str) -> tuple:
        """Run a command on the host and get the output

        Args:
            cmd (str): a command line with options

        Returns:
            tuple: returnCode, StdOut, StdErr
        """
        log.debug(f"{cmd=}")
        try:
            p = subprocess.run(
                cmd, capture_output=True, text=True, shell=True, check=True
            )
            r_code = p.returncode
            stdout = p.stdout
            stderr = p.stderr
            log.debug(f"'{cmd}'\n {r_code=}\n {stdout=}\n {stderr=}")
            return r_code, stdout, stderr
        except subprocess.CalledProcessError as e:
            log.exception(e)
            raise e

    @staticmethod
    def file_to_base64(file: Path) -> str:
        """Encode a file to base64 str

        Args:
            file: input file path

        Returns:
            str:
        """
        with open(file, "rb") as f:
            return b64encode(f.read()).decode("utf-8")

    @staticmethod
    def readable_file_size(in_bytes: int) -> str:
        """Convert bytes to human-readable KB, MB, or GB

        Args:
            in_bytes: input bytes integer

        Returns:
            str
        """
        for _unit in ["B", "KB", "MB", "GB"]:
            if in_bytes < 1024:
                break
            in_bytes /= 1024
        res = f"{in_bytes} B" if _unit == "B" else f"{in_bytes:.1f} {_unit}"
        return res

    @staticmethod
    def remove_exif_gps(exif_data: bytes) -> tuple:
        """Remove GPS info from the EXIF data

        Args:
            exif_data: bytes

        Returns:
            tuple: bool, bytes
        """
        exif_dict = piexif.load(exif_data)
        if "GPS" in exif_dict and exif_dict["GPS"]:
            exif_dict.pop("GPS")
            exif_bytes = piexif.dump(exif_dict)
            log.debug("Removed GPS info in EXIF")
            return True, exif_bytes
        log.debug("No GPS in EXIF")
        return False, exif_data

    @staticmethod
    def decode_exif(exif_data: bytes) -> dict:
        """Decode the EXIF data

        Args:
            exif_data: bytes

        Returns:
            dict
        """
        exif_dict = piexif.load(exif_data)
        _dict = {}
        for ifd_name, val in exif_dict.items():
            # Canon EOS 5D Mark II 'thumbnail': b'\xff\xd8\xff\xdb...
            # 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte
            if not val or ifd_name == "thumbnail":
                continue
            for tag_id, value in val.items():
                tag_name = piexif.TAGS[ifd_name].get(tag_id, {}).get("name", tag_id)
                _dict[tag_name] = value
        # log.info(f"{_dict=}")
        for key in (
            "FNumber",
            "FocalLength",
            "MakerNote",
            "SceneType",
            "SubjectArea",
            "Software",
            "HostComputer",
            "UserComment",
        ):
            if key in _dict:
                _dict.pop(key)
        keys = list(_dict.keys())
        for keyword in (
            "DateTime",
            "OffsetTime",
            "SubSecTime",
            "Tile",
            "Pixel",
            "Lens",
            "Resolution",
            "Value",
        ):
            for key in keys:
                if key.startswith(keyword) or key.endswith(keyword):
                    _dict.pop(key)
        _res = {
            k: (v.decode() if isinstance(v, bytes) else v) for k, v in _dict.items()
        }
        log.debug(f"{_res=}")
        return _res

    @staticmethod
    def get_image_data(file: Path) -> tuple:
        """Get image file data

        Args:
            file: image file path

        Returns:
            tuple: data, info
        """
        size = getsize(file)
        m_ts = datetime.fromtimestamp(getmtime(file)).strftime(TS_FORMAT)
        with Image.open(file) as img:
            data = img.convert("RGB")
            d_info = {
                "file_size": Common.readable_file_size(size),
                "file_ts": m_ts,
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "info": img.info,
            }
            for key in ("icc_profile", "xmp"):
                if key in img.info:
                    img.info.pop(key)
            if EXIF in img.info:
                exif_data = img.info.pop(EXIF)
                d_info[EXIF] = Common.decode_exif(exif_data)

        return data, d_info

    @staticmethod
    def jsn_serial(obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, IFDRational):
            return float(obj)
        if isinstance(obj, bytes):
            return obj.decode()
        raise TypeError(
            f"Object of type {obj.__class__.__name__} is not JSON serializable"
        )

    @staticmethod
    def are_images_equal(path1: Path, path2: Path) -> bool:
        """Check if two image files are visually equal pixel-wise

        Args:
            path1: image1 file path
            path2: image2 file path

        Returns:
            bool: True - visually equal, False - not visually equal
        """
        data1, meta1 = Common.get_image_data(path1)
        data2, meta2 = Common.get_image_data(path2)

        s1 = f"{path1}:\n{json.dumps(meta1, indent=2, default=Common.jsn_serial)}"
        log.debug(s1)
        s2 = f"{path2}:\n{json.dumps(meta2, indent=2, default=Common.jsn_serial)}"
        log.debug(s2)
        is_equal = ImageChops.difference(data1, data2).getbbox() is None
        log.debug(f"{is_equal=}")
        return is_equal

    @staticmethod
    def get_crop_box(width, height, border_width) -> tuple[float, float, float, float]:
        """Get the crop box tuple

        Args:
            width: image width int
            height: image height int
            border_width: border width int

        Returns:
            tuple[float, float, float, float]
        """
        crop_left = border_width
        crop_top = border_width
        crop_right = width - border_width
        crop_bottom = height - border_width
        return crop_left, crop_top, crop_right, crop_bottom

    @staticmethod
    def calculate_new_size(width: int, height: int, max_len: int) -> tuple[int, int]:
        """Calculate the new size with the same aspect ratio

        Args:
            width: image width int
            height: image height int
            max_len: max length int

        Returns:
            tuple: new_width, new_height
        """
        # Calculate to keep aspect ratio
        if width > height:
            ratio = max_len / width
        else:
            ratio = max_len / height
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        return new_width, new_height

    @staticmethod
    def prepare_all_files(in_path: Path, out_path: Path | str):
        """

        Args:
            in_path: input dir path
            out_path: output dir path or REPLACE

        Returns:
            iterable: files list generator
        """
        if out_path != REPLACE:
            out_path.mkdir(parents=True, exist_ok=True)
        # Fix Path.glob() got 2x count on Windows 10
        tmp = [in_path.glob(p, case_sensitive=True) for p in PATTERNS]
        _files = itertools.chain.from_iterable(set(tmp))
        return _files

    @staticmethod
    def multiprocess_progress_bar(func, desc: str, all_cnt: int, tasks: list) -> int:
        """Run task in multiprocess with progress bar

        Args:
            func: function to be run in multiprocess
            desc: description str
            all_cnt: all tasks cnt int
            tasks: tasks list for multiprocess pool

        Returns:
            int: success_cnt
        """
        success_cnt = 0
        workers = max(cpu_count(), 4)

        with Pool(workers) as pool:
            with tqdm(total=all_cnt, desc=desc) as pbar:
                for ok, res in pool.imap_unordered(func, tasks):
                    if ok:
                        success_cnt += 1
                    else:
                        tqdm.write(f"Error: {res}")
                    pbar.update(1)
        return success_cnt

    @staticmethod
    def set_out_file(in_path: Path, out_path: Path, extra: str = "") -> Path:
        """Set the output file path

        Args:
            in_path: input file path
            out_path: output dir path
            extra: extra str in output file name

        Returns:
            Path:
        """
        if out_path == REPLACE:
            out_file = Path(f"{in_path.parent}/{in_path.stem}_tmp{in_path.suffix}")
            return out_file
        out_path.mkdir(parents=True, exist_ok=True)
        out_file = out_path
        if out_path.is_dir():
            filename = f"{in_path.stem}_{extra}{in_path.suffix}"
            out_file = Path(f"{out_path}/{filename}")
        return out_file

    @staticmethod
    def set_log_by_process() -> None:
        """Do log setting in a worker process.
        loguru config doesn’t propagate across processes.

        Returns:
            None
        """
        if current_process().name != "MainProcess":
            Log.set_worker_log()
