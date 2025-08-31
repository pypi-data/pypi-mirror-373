from ..imports import *
def get_rel_path(path: str, parent: str) -> str:
    if path and path.startswith(parent):
        return path[len(parent):] or "."
    return path

def if_file_get_dir(path: Optional[str] = None) -> Optional[str]:
    if path and os.path.isfile(path):
        return os.path.dirname(path)
    return path

def get_abs_path() -> str:
    return os.path.abspath(__file__)

def get_abs_dir(path: Optional[str] = None) -> str:
    p = if_file_get_dir(path=path)
    abs_path = p or get_abs_path()
    return os.path.dirname(abs_path)

def get_output_path(path: Optional[str] = None) -> str:
    p = if_file_get_dir(path=path)
    abs_dir = p or get_abs_dir()
    return os.path.join(abs_dir, "build_output.txt")
