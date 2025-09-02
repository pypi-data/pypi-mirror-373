import logging
import os
from datetime import date


def log_setup(file_path: str,
              etl_name: str,
              loging_level: str) -> None:
    '''Set up the configuration for the logger'''
    os.makedirs(file_path, exist_ok=True)
    log_file_path = f"{file_path}/{etl_name}_{date.today()}"

    format_str = (
        f"time=%(asctime)s | lvl=%(levelname)s | comp={etl_name} "
        f"| op=%(name)s: %(filename)s[%(lineno)d]: %(funcName)s "
        f"| msg=%(message)s"
    )

    logging.basicConfig(
        level=logging.getLevelName(loging_level),
        format=format_str,
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler()
        ]
    )
