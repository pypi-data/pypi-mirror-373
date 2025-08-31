"""class Log - config logging
Copyright © 2025 John Liu
"""

import json
import os
import sys
from datetime import datetime
from os.path import dirname

from loguru import logger

from batch_img.const import PKG_NAME, TS_FORMAT


class Log:
    _file = ""
    _conf = {}

    @staticmethod
    def load_config(path: str) -> dict:
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error load JSON config file: {path}\n{e}")
            return {}

    @staticmethod
    def _get_settings() -> tuple:
        """Get log settings from config

        Returns:
            tuple
        """
        if not Log._conf:
            Log._conf = Log.load_config(f"{dirname(__file__)}/config.json")
        level = Log._conf.get("level")
        if not level:
            level = "INFO"
        mode = Log._conf.get("mode")
        to_file = Log._conf.get("to_file")
        if mode == "dev":
            logformat = (
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | {process} | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>"
            )
            backtrace = True
            diagnose = True
        else:
            # Simplify production log output
            logformat = "<level>{message}</level>"
            backtrace = False
            diagnose = False
        return level, logformat, backtrace, diagnose, to_file

    @staticmethod
    def init_log_file() -> str:
        """Set up the unique name log file for each run

        Returns:
            str: log file path
        """
        if Log._file:  # init only once
            return Log._file

        logger.remove()
        level, logformat, backtrace, diagnose, to_file = Log._get_settings()
        logger.add(
            sys.stderr,
            level=level,
            format=logformat,
            backtrace=backtrace,
            diagnose=diagnose,
        )
        if not to_file:
            return Log._file
        Log._file = f"run_{PKG_NAME}_{datetime.now().strftime(TS_FORMAT)}.log"
        log_f = f"{os.getcwd()}/{Log._file}"
        logger.add(
            log_f, level=level, format=logformat, backtrace=backtrace, diagnose=diagnose
        )
        return Log._file

    @staticmethod
    def set_worker_log():
        """Set up the logger for each worker process in multiprocessing

        Returns:
            logger: for this worker process
        """
        logger.remove()
        level, logformat, backtrace, diagnose, to_file = Log._get_settings()
        logger.add(
            sys.stderr,
            level=level,
            format=logformat,
            backtrace=backtrace,
            diagnose=diagnose,
        )
        # Not log to file in prod for better user experience
        if not to_file:
            return logger
        f = f"run_{PKG_NAME}_{datetime.now().strftime(TS_FORMAT)}.log"
        log_file = f"{os.getcwd()}/{f}"
        logger.add(
            log_file,
            level=level,
            format=logformat,
            backtrace=backtrace,
            diagnose=diagnose,
        )
        return logger
