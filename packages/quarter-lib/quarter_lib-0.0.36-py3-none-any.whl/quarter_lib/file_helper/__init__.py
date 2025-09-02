import json
import os

from ..logging import setup_logging

logger = setup_logging(__file__)

def delete_files(files):
    for file in files:
        try:
            os.remove(file)
        except OSError as e:
            logger.error(e)

def get_config(file_path):
    with open(os.path.join(os.getcwd() + "/config/", file_path), encoding="utf-8") as f:
        data = json.load(f)
    return data

def get_value(value, row, config):
    return next(i for i in config if i[row] == value)
