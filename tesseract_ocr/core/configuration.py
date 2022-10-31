import configparser
import os
from pathlib import Path

# READ CONFIG FILE
lobj_parser = configparser.ConfigParser()
lstr_config_file_path = str(Path(__file__).parent.parent) + os.path.sep + "data" + os.path.sep + "config.ini"
lobj_parser.read(lstr_config_file_path)

# GET CONFIG VALUES
LOGGING_LEVEL = lobj_parser.get('GENERAL', 'LOGGING_LEVEL')
