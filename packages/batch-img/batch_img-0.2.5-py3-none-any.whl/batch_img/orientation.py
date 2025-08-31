"""class Orientation: detect if the image file(s) is upside down or sideways
Copyright © 2025 John Liu
"""

import os
from pathlib import Path

import cv2
import numpy as np
import piexif
import pillow_heif
from loguru import logger as log
from PIL import Image

from batch_img.common import Common
from batch_img.const import EXIF

pillow_heif.register_heif_opener()

ROTATION_MAP = {  # map to the clockwise angle to correct
    "bottom": 0,
    "top": 180,
    "left": 270,  # rotated right
    "right": 90,  # rotated left
}
EXIF_CW_ANGLE = {
    1: 0,
    2: 0,
    3: 180,
    4: 180,
    5: 270,
    6: 270,
    7: 90,
    8: 90,
}
FLOOR_THRESHOLD = 0.73
SKY_THRESHOLD = 0.31


class Orientation:
    @staticmethod
    def get_exif_orientation(file: Path) -> int:
        """Get image orientation in EXIF data

        Args:
            file: image file path

        Returns:
            int: clockwise angle: 0, 90, 180, 270 or -1
        """
        try:
            with Image.open(file) as img:
                if EXIF not in img.info:
                    log.warning(f"No EXIF data in {file}")
                    return -1
                exif_info = Common.decode_exif(img.info[EXIF])
                if "Orientation" in exif_info:
                    return EXIF_CW_ANGLE.get(exif_info["Orientation"])
            log.warning(f"No 'Orientation' tag in {exif_info=}")
            return -1
        except (AttributeError, FileNotFoundError, ValueError) as e:
            log.error(e)
            return -1

    @staticmethod
    def set_exif_orientation(file: Path, o_val: int) -> bool:
        """Set orientation in the EXIF of an image file

        Args:
            file: image file path
            o_val: orientation value int

        Returns:
            bool: True - Success. False - Error
        """
        if o_val not in {1, 2, 3, 4, 5, 6, 7, 8}:
            log.error(f"Quit due to bad orientation value: {o_val=}")
            return False
        try:
            tmp_file = Path(f"{file.parent}/{file.stem}_tmp{file.suffix}")
            with Image.open(file) as img:
                exif_dict = {"0th": {}, "Exif": {}}
                if EXIF in img.info:
                    exif_dict = piexif.load(img.info[EXIF])
                exif_dict["0th"][piexif.ImageIFD.Orientation] = o_val
                exif_bytes = piexif.dump(exif_dict)
                img.save(tmp_file, img.format, exif=exif_bytes, optimize=True)
            log.debug(f"Saved the updated EXIF image to {tmp_file}")
            os.replace(tmp_file, file)
            log.debug(f"Replaced {file} with tmp_file")
            return True
        except (AttributeError, FileNotFoundError, ValueError) as e:
            log.error(e)
            return False

    @staticmethod
    def get_floor_score(img) -> float:
        """Get the floor score for every 90 degree rotated image

        Args:
            img: OpenCV img

        Returns:
            float:
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h = gray.shape[0]
        top, bottom = gray[: h // 3], gray[-h // 3 :]

        edges = cv2.Canny(gray, 50, 150)
        top_e, bot_e = edges[: h // 3], edges[-h // 3 :]
        edge_diff = np.mean(bot_e) - np.mean(top_e)
        brightness_diff = np.mean(bottom) - np.mean(top)

        score = edge_diff + brightness_diff
        confidence = 1 / (1 + np.exp(-score / 20))  # by sigmoid
        return round(float(confidence), 3)

    def detect_floor_by_edge(self, file: Path) -> tuple:
        """Get image orientation by floor edge

        Args:
            file: image file path

        Returns:
            tuple: clockwise angle to correct, confidence as float
        """
        scores = {}
        with Image.open(file) as safe_img:
            opencv_img = np.array(safe_img)
            if opencv_img is None:
                raise ValueError(f"Failed to load {file}")
        for angle_cw in (0, 90, 180, 270):
            img = self._rotate_image(opencv_img, angle_cw)
            scores[angle_cw] = self.get_floor_score(img)
        log.debug(f"{scores=}")
        best_angle = max(scores, key=scores.get)
        score = scores[best_angle]
        log.debug(f"{best_angle=}, {score=}")
        if score < FLOOR_THRESHOLD:
            log.warning(f"{score=} is less than {FLOOR_THRESHOLD=}")
            return -1, score
        return best_angle, score

    @staticmethod
    def _rotate_image(img, angle: int):
        """Helper to rotate image by the clock wise angle degree

        Args:
            img: image data
            angle: angle degree int: 0, 90, 180, 270

        Returns:
            image data
        """
        if angle == 90:
            return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        if angle == 180:
            return cv2.rotate(img, cv2.ROTATE_180)
        if angle == 270:
            return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        return img

    def get_cw_angle_by_face(self, file: Path) -> int:
        """Get image orientation by face using Haar Cascades:
        * Fastest but least accurate
        * Works best with frontal faces
        * May produce false positives

        Args:
            file: image file path

        Returns:
            int: clockwise angle: 0, 90, 180, 270, or -1
        """
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        with Image.open(file) as safe_img:
            opencv_img = np.array(safe_img)
            if opencv_img is None:
                raise ValueError(f"Failed to load {file}")
            for angle_cw in (0, 90, 180, 270):
                img = self._rotate_image(opencv_img, angle_cw)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(
                    gray, scaleFactor=1.2, minNeighbors=6
                )
                if len(faces) > 0:
                    return angle_cw
        log.warning(f"Found no face in {file}")
        return -1

    @staticmethod
    def get_orientation_by_floor(file: Path) -> int:
        """Get image orientation by floor

        Args:
            file: image file path

        Returns:
            int: clockwise angle: 0, 90, 180, 270
        """
        with Image.open(file) as img:
            opencv_img = np.array(img)
            if opencv_img is None:
                raise ValueError(f"Failed to load {file}")

        # Convert to HSV for color-based floor detection
        hsv = cv2.cvtColor(opencv_img, cv2.COLOR_BGR2HSV)
        # Heuristic: floors are often low saturation, medium-low value (gray/brown)
        lower_floor = np.array([0, 0, 30])
        upper_floor = np.array([180, 100, 180])
        mask = cv2.inRange(hsv, lower_floor, upper_floor)

        h, w, _ = opencv_img.shape
        regions = {
            "top": mask[0 : h // 3, :],
            "bottom": mask[2 * h // 3 :, :],
            "left": mask[:, 0 : w // 3],
            "right": mask[:, 2 * w // 3 :],
        }
        counts = {k: cv2.countNonZero(v) for k, v in regions.items()}
        log.debug(f"Floor pixels cnt: {counts=}")

        max_region = max(counts, key=counts.get)
        log.debug(f"{max_region=}, {file.name}")
        return ROTATION_MAP.get(max_region)

    @staticmethod
    def get_cw_angle_by_sky(file: Path) -> tuple:
        """Get image orientation by sky, clouds

        Args:
            file: image file path

        Returns:
            tuple: clockwise angle: 0, 90, 180, 270 or -1, confidence
        """
        with Image.open(file) as img:
            opencv_img = np.array(img)
            if opencv_img is None:
                raise ValueError(f"Failed to load {file}")

        hsv = cv2.cvtColor(opencv_img, cv2.COLOR_BGR2HSV)
        sky_mask = cv2.inRange(hsv, np.array([90, 20, 70]), np.array([140, 255, 255]))
        cloud_mask = cv2.inRange(hsv, np.array([0, 0, 180]), np.array([180, 70, 255]))
        sky_cloud_mask = cv2.bitwise_or(sky_mask, cloud_mask)

        h, w, _ = opencv_img.shape
        regions = {
            "top": sky_cloud_mask[0 : h // 3, :],
            "bottom": sky_cloud_mask[2 * h // 3 :, :],
            "left": sky_cloud_mask[:, 0 : w // 3],
            "right": sky_cloud_mask[:, 2 * w // 3 :],
        }
        counts = {k: cv2.countNonZero(v) for k, v in regions.items()}
        log.debug(f"Sky / Cloud: {counts=}")
        max_region = max(counts, key=counts.get)
        total_cnt = sum(v for v in counts.values())
        max_cnt = counts[max_region]
        confidence = round(max_cnt / total_cnt, 3)
        log.debug(f"{total_cnt=}, {max_cnt=}, {confidence=}")
        log.debug(f"{max_region=}, {file.name=}")
        if confidence < SKY_THRESHOLD:
            log.warning(f"{confidence=} is less than {SKY_THRESHOLD=}")
            return -1, confidence
        return ROTATION_MAP.get(max_region), confidence
