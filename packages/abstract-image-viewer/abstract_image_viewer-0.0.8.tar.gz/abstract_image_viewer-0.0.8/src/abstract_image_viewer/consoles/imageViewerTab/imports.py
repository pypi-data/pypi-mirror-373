# New Tab: Directory Map
from abstract_gui.QT6.imports import *
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
import json
from pathlib import Path
from abstract_utilities import SingletonMeta,get_logFile,safe_dump_to_json,safe_read_from_json
from abstract_utilities.type_utils import MIME_TYPES
from abstract_paths import *
logger = get_logFile(__name__)
EXTS = set(list(MIME_TYPES.get("image").keys())+list(MIME_TYPES.get("video").keys()))
ABS_PATH = os.path.abspath(__file__)
ABS_DIR = os.path.dirname(ABS_PATH)
DIRS_JS_PATH = os.path.join(ABS_DIR,'DIRS_JS.json')
# loaders.py
from PyQt6 import QtCore
from pathlib import Path
import os

class DirTaskSignals(QtCore.QObject):
    directory_ready = QtCore.pyqtSignal(str, str, list)

class DirTask(QtCore.QRunnable):
    def __init__(self, directory: str, files: list):
        super().__init__()
        self.directory = directory
        self.files = files
        self.s = DirTaskSignals()
        self.setAutoDelete(True)

    @QtCore.pyqtSlot()
    def run(self):
        if not self.directory or not self.files:
            return
        name = os.path.basename(self.directory.rstrip(os.sep))
        # Could do per-dir prep here (sorting, stat checks, etc.)
        self.s.directory_ready.emit(name, self.directory, list(self.files))

class BatchDirEmitter(QtCore.QThread):
    directory_ready = QtCore.pyqtSignal(str, str, list)  # name, directory, files

    def __init__(self, items: list[tuple[str, list]], parent=None, throttle_ms=2):
        """
        items: list of (directory_path, files_list)
               directory_path: str
               files_list: list of str or Path
        """
        super().__init__(parent)
        self._items = items
        self._throttle_ms = int(throttle_ms)

    def run(self):
        for directory, files in self._items:
            if self.isInterruptionRequested():
                return
            if not directory or not files:
                continue
            name = os.path.basename(directory.rstrip(os.sep))
            # Emit immediately; UI handles rendering
            self.directory_ready.emit(name, directory, list(files))
            if self._throttle_ms:
                QtCore.QThread.msleep(self._throttle_ms)
class DIRSDATACLASS(metaclass=SingletonMeta):
    def __init__(self,defaultRoot=None,mapPath=None):
        if not hasattr(self, 'initialized') or defaultRoot and self.defaultRoot != defaultRoot:
            self.initialized = True
            self.defaultRoot = defaultRoot or os.getcwd()
            self.dirs_js_path = mapPath or DIRS_JS_PATH
            self.dirs_js_data = self.get_dirs_js_data()
            self.dirs_js_dirs = self.get_dirs_js_dirs()
            self.default_params = self.get_default_params()
            self.return_all_dub_data(self.defaultRoot)
    def get_dirs_js_dirs(self):
        self.dirs_js_dirs = list(self.dirs_js_data.keys())
        print(f"dirs_js has {len(self.dirs_js_dirs)} directories mapped")
        return self.dirs_js_dirs
    def get_dirs_js_data(self):
        if not os.path.isfile(self.dirs_js_path):
            print(f"no data for {len(self.dirs_js_path)}")
            safe_dump_to_json(data ={},file_path=self.dirs_js_path)
        self.dirs_js_data =  safe_read_from_json(self.dirs_js_path)
        return self.dirs_js_data
    def save_dirs_data(self,data={}):
        pre_dirs = self.get_dirs_js_dirs()
        self.dirs_js_data.update(data)
        post_dirs = self.get_dirs_js_dirs()
        total_dirs = len(post_dirs) - len(pre_dirs)
        print(f"{total_dirs} added to drs_js data")
        if total_dirs != 0:
            print(f"saving drs_js data")
            safe_dump_to_json(data=self.dirs_js_data,file_path=self.dirs_js_path)
    def get_default_params(self):
        self.default_params = define_defaults(allowed_exts=EXTS,exclude_dirs=self.get_dirs_js_dirs())
        print(f"returning default_params")
        return self.default_params
    def map_files(self,directory=None,files=None):
        
        print(directory)
        if (directory and not self.dirs_js_data.get(directory)):
            dirs,files =  self.get_dirs_and_files(directory)
            print(f"mapping {len(files)} files")
            files = self.get_needed_files(files)
        if files:
            for file in files:
                dirname = os.path.dirname(file)
                if dirname not in self.dirs_js_data:
                    self.dirs_js_data[dirname] = []
                self.dirs_js_data[dirname].append(file)
            self.save_dirs_data()
    def get_subdirs(self,directory,directories=None):
        dirs_js_dirs = directories or self.get_dirs_js_dirs()
        
        return [subdir for subdir in dirs_js_dirs if directory and subdir and subdir.startswith(str(directory))]
    def get_needed_files(self,files):
        dirs_js_dirs = self.get_dirs_js_dirs()
        return [file for file in files if os.path.dirname(file) not in dirs_js_dirs]
    def return_all_dub_data(self,directory):
        if not self.dirs_js_data.get(directory) and not self.get_subdirs(directory):
            print("no data in dirs_js_data")
            dirs,files =  self.get_dirs_and_files(directory)
            self.map_files(files=files)
        subdirs = self.get_subdirs(directory)
        new_js = {directory:self.dirs_js_data.get(directory)}
        files_num=0
        for subdir in subdirs:
            new_js[subdir] = self.dirs_js_data.get(subdir)
            files_num+=len(new_js[subdir])
            
        print(f"returning {files_num} files in dub data")
        return new_js
    def get_dirs_and_files(self,directory,include_files=True):
        self.get_default_params()
        print(f"get_files_and_dirs")
        directory = directory or self.defaultRoot
        dirs,files =  get_files_and_dirs(directory=directory,
                                       cfg = self.default_params,
                                       recursive=True,
                                       include_files=include_files)
        print(f"fetched {len(files)} files from {len(dirs)} directories")
        return dirs,files


def get_dirMgr(defaultRoot=None,mapPath=None):
    return DIRSDATACLASS(defaultRoot=defaultRoot,mapPath=mapPath)
def get_all_sub_dirs(directory,directories=None,defaultRoot=None,mapPath=None):
    dir_mgr = get_dirMgr(defaultRoot=defaultRoot,mapPath=mapPath)
    return dir_mgr.get_subdirs(directory)
def get_subdir_list(directory,json_obj=None,defaultRoot=None,mapPath=None):
    dir_mgr = get_dirMgr(defaultRoot=defaultRoot,mapPath=mapPath)
    return subdirs


def get_dirs_js(directory,defaultRoot=None,mapPath=None):
    dir_mgr = get_dirMgr(defaultRoot=defaultRoot,mapPath=mapPath)
    return dir_mgr.return_all_dub_data(directory)

class DirScanner(QtCore.QThread):
    dir_processed = QtCore.pyqtSignal(str, str, list)  # name, directory, files
    error = QtCore.pyqtSignal(str)  # Error message

    def __init__(self, folder: Path, defaultRoot: Path = None, files: set = None):
        super().__init__()
        self.folder = str(folder)
        self.files = files
        self.logger = logging.getLogger(__name__)
        self.name = os.path.basename(self.folder)
        self.filename,self.ext = os.path.splitext(self.folder)
    def run(self):
        try:
            
            
            
            # Emit the processed directory
            self.dir_processed.emit(self.filename, self.folder, self.files)
        except Exception as e:
            self.logger.error(f"Error scanning {self.folder}: {e}")
            self.error.emit(f"Failed to scan {self.folder}: {e}")
    
##        import logging
##        from pathlib import Path
##        from PyQt5 import QtCore, QtWidgets  # Adjust for PySide if needed
##        from typing import List, Optional
##
##        logger = logging.getLogger(__name__)
##
##        class DirScanner(QtCore.QThread):
##            """Thread to scan a directory and emit file lists."""
##            dir_processed = QtCore.pyqtSignal(str, str, list)  # name, directory, files
##            error = QtCore.pyqtSignal(str)  # Error message
##
##            def __init__(self, folder: Path, defaultRoot: Path = None):
##                super().__init__()
##                self.folder = folder
##                self.defaultRoot = defaultRoot
##                self.exts = {'.mp4', '.jpg', '.png'}  # Supported extensions
##
##            def run(self):
##                try:
##                    folder_path = self.folder.resolve()
##                    folder_str = str(folder_path)
##                    name = folder_path.name or "Root"
##                    
##                    # Scan files in the directory
##                    files = [
##                        str(p.relative_to(self.defaultRoot)) if self.defaultRoot else str(p)
##                        for p in folder_path.iterdir()
##                        if p.is_file() and p.suffix.lower() in self.exts
##                    ]
##                    
##                    # Emit the processed directory
##                    self.dir_processed.emit(name, folder_str, files)
##                except Exception as e:
##                    logger.error(f"Error scanning {self.folder}: {e}")
##                    self.error.emit(f"Failed to scan {self.folder}: {
