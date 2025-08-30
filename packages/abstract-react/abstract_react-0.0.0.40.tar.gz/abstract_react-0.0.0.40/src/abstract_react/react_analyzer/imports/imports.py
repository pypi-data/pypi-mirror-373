import argparse,json,os,re
from pathlib import Path
from typing import *
from abstract_paths.file_filtering import (
    define_defaults,
    collect_filepaths,
    make_allowed_predicate,
    make_list,
    get_media_exts
    )

