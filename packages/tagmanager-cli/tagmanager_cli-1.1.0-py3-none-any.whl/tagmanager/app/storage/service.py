from ...configReader import config
import os


def show_storage_location():
    return config['DEFAULT']['TAG_FILE']


def open_storage_location():
    os.startfile(config['DEFAULT']['TAG_FILE'])