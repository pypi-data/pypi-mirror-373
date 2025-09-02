import json
import os
from datetime import datetime


def load_json_file(json_file_path: str):
    with open(json_file_path) as json_file:
        return json.load(json_file)


def load_file_as_string(file_name: str) -> str:
    cwd = os.getcwd()
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    with open(file_path, encoding='utf-8') as file:
        lines = file.readlines()
        return "".join(lines)


def append_timestamp_to_basepath(base_path):
    now = datetime.now()
    unique_directory = os.path.join(base_path, "{0}{1}{2}_{3}{4}_{5}".format(now.year, now.month, now.day, now.hour,
                                                                             now.minute,
                                                                             now.second))
    return unique_directory
