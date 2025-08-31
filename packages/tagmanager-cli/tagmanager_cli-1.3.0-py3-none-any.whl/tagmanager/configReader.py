import configparser
import os

config = configparser.ConfigParser()
path = os.path.abspath(__file__)
root_dir = os.path.dirname(path)

if os.path.exists(os.path.join(root_dir, "test_config.ini")):
    config_file = os.path.join(root_dir, "test_config.ini")
else:
    config_file = os.path.join(root_dir, "config.ini")

config.read(config_file)

