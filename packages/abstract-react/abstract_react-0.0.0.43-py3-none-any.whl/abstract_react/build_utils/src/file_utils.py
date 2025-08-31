from ..imports import *
from .path_utils import *
def return_if_one(obj):
    if obj and isinstance(obj, list) and len(obj) > 0:
        return obj[0]
    return obj

def list_main_directory(path: Optional[str] = None):
    p = if_file_get_dir(path=path) or DEFAULT_MAIN_DIR
    return os.listdir(p)

def list_main_directory_paths(path: Optional[str] = None):
    p = if_file_get_dir(path=path) or DEFAULT_MAIN_DIR
    return [os.path.join(p, item) for item in list_main_directory(path=p) if item]

def get_spec_file(stem: str, path: Optional[str] = None) -> Optional[str]:
    """
    Finds e.g. tsconfig.json by stem='tsconfig'
    """
    p = if_file_get_dir(path=path) or DEFAULT_MAIN_DIR
    try:
        for item in os.listdir(p):
            base, ext = os.path.splitext(item)
            if base == stem:
                return os.path.join(p, item)
    except FileNotFoundError:
        pass
    return None

def get_ts_config_path(path: Optional[str] = None) -> Optional[str]:
    # prefer exact tsconfig.json if present
    p = if_file_get_dir(path=path) or DEFAULT_MAIN_DIR
    exact = os.path.join(p, "tsconfig.json")
    if os.path.isfile(exact):
        return exact
    return get_spec_file("tsconfig", path=p)

def get_ts_config_data(path: Optional[str] = None):
    ts_config_path = get_ts_config_path(path=path)
    return safe_read_from_json(ts_config_path) if ts_config_path else None

def get_ts_paths(path: Optional[str] = None):
    ts_config_data = get_ts_config_data(path=path)
    any_value = get_any_value(ts_config_data, "paths")
    return return_if_one(any_value)
