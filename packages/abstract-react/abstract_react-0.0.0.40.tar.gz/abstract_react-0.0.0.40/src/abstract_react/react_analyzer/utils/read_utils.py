from abstract_utilities import *
from .react_analyzer_utils import *
from abstract_apis import *
MAIN_DIR = os.getcwd()
def if_file_get_dir(path=None):
    if path and os.path.isfile(path):
        path = os.path.dirname(path)
    return path
def run_ssh_cmd(user_at_host: str, cmd: str, path: str) -> str:
    """Run on remote via SSH and return stdout+stderr."""
    try:
        full = f"ssh {user_at_host} 'cd {path} &&  {cmd}'"
        proc = subprocess.run(full, shell=True, capture_output=True, text=True)
        return (proc.stdout or "") + (proc.stderr or "")
    except Exception as e:
        return f"❌ run_ssh_cmd error: {e}\n"
def get_abs_path():
    return os.path.abspath(__file__)
def get_abs_dir(path=None):
    
    path = if_file_get_dir(path=path)
    abs_path = path or get_abs_path()
    return os.path.dirname(abs_path)
def get_output_path(path=None):
    path = if_file_get_dir(path=path)
    abs_dir = path or get_abs_dir()
    return os.path.join(abs_dir,'build_output.txt')
def return_if_one(obj):
    if obj and isinstance(obj,list) and len(obj)>0:
        obj = obj[0]
    return obj
def list_main_directory(path=None):
    path = if_file_get_dir(path=path)
    return os.listdir(path or MAIN_DIR)
def list_main_directory_paths(path=None):
    path = if_file_get_dir(path=path) or MAIN_DIR
    return [os.path.join(path ,item) for item in list_main_directory(path-path) if item]
def get_spec_file(string,path=None):
    path = if_file_get_dir(path=path) or MAIN_DIR
    spec_files = [os.path.join(path,item) for item in list_main_directory() if os.path.splitext(item)[0] == string]
    return return_if_one(spec_files)
def get_ts_config_path(path=None):
    return get_spec_file('tsconfig',path=path)
def get_ts_config_data(path=None):
    ts_config_path = get_ts_config_path(path=path)
    return safe_read_from_json(ts_config_path)
def get_ts_paths(path=None):
    ts_config_data = get_ts_config_data(path=path)
    any_value = get_any_value(ts_config_data, "paths")
    return return_if_one(any_value)
def run_build(path=None):
    user_at_host = 'solcatcher'
    path = if_file_get_dir(path=path) or MAIN_DIR
    output = eatAll(get_output_path().split(path)[-1],['/'])
    cmd = f'yarn build > {output}'
    run_ssh_cmd(
        user_at_host=user_at_host,
        cmd=cmd,
        path=path
        )
def run_build_get_errors(path=None):
    error_path = get_output_path(path=path)
    run_build(path=path)
    contents = read_from_file(error_path)
    return parse_tsc_output(contents)
 
