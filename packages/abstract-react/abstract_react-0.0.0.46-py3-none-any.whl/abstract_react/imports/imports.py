import argparse,json,os,re,traceback,shlex,subprocess
from pathlib import Path
from typing import *
from PyQt6.QtWidgets import QStackedWidget, QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QLabel,QTreeWidget, QTreeWidgetItem, QHeaderView, QButtonGroup
from PyQt6.QtCore import QThread, pyqtSignal
from abstract_paths.file_filtering import (
    define_defaults,
    collect_filepaths,
    make_allowed_predicate,
    make_list,
    get_media_exts
    )

from abstract_apis import run_local_cmd,run_remote_cmd
