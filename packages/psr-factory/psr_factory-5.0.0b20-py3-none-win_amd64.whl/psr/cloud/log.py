# PSR Cloud. Copyright (C) PSR, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import logging
import os


def get_logger(
    id: int, quiet: bool, debug_mode: bool, log_dir: str = os.getcwd()
) -> logging.Logger:
    logger = logging.getLogger(str(id))
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(message)s")

    if debug_mode:
        os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(f"{log_dir}/psr_cloud_console_{id}.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if not quiet:
        console_handler = logging.StreamHandler()
        if debug_mode:
            console_handler.setLevel(logging.DEBUG)
        else:
            console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def enable_log_timestamp(logger: logging.Logger, enable: bool) -> None:
    for handler in logger.handlers:
        if enable:
            handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
        else:
            handler.setFormatter(logging.Formatter("%(message)s"))
