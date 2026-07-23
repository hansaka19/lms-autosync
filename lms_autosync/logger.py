import logging
import os

def get_logger():
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger("lms_autosync")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        fh = logging.FileHandler("logs/run.log", encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s  %(levelname)-7s  %(message)s"))
        logger.addHandler(fh)
        sh = logging.StreamHandler()
        sh.setFormatter(logging.Formatter("%(levelname)-7s  %(message)s"))
        logger.addHandler(sh)
    return logger