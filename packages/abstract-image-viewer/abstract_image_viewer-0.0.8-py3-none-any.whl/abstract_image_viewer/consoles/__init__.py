import os
from abstract_gui import get_for_all_tabs
CONSOLE_DIR_PATH = os.path.abspath(__file__)
CONSOLE_ABS_DIR = os.path.dirname(CONSOLE_DIR_PATH)
get_for_all_tabs(CONSOLE_ABS_DIR)
from abstract_gui import getInitForAllTabs,startConsole
ABS_PATH = os.path.abspath(__name__)
ABS_DIR = os.path.dirname(ABS_PATH)
getInitForAllTabs(ABS_DIR)
from .imageViewerTab import imageViewerTab,startImageViewerConsole
