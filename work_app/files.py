
__author__ = "an.luzgarev"

import os

import my_site.settings as settings_set

"""
Module for working with files
"""


def get_list_of_files():
	path = get_files_path()
	list_of_files = os.listdir(path)
	return list_of_files


def get_files_path():
	return os.path.join(settings_set.BASE_DIR, r"my_site/files")