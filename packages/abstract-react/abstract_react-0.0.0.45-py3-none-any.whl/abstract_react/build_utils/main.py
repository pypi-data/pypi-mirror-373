from .imports import *
from .src import *
def run_build(
    path: Optional[str] = None,
    output_path: Optional[str] = None,
    *,
    user_at_host: Optional[str] = None,
    use_tsc: bool = False,
    install_first: bool = False
) -> str:
    """
    Run yarn build (default) or tsc in the given directory.
    If user_at_host is provided (e.g. 'jake@server'), runs remotely via SSH.
    Writes combined stdout+stderr to output_path (local) and also returns it.
    """
    workdir = if_file_get_dir(path=path) or DEFAULT_MAIN_DIR
    outfile = output_path or get_output_path(path=workdir)

    # Compose the command
    parts = []
    if install_first:
        parts.append("yarn install --frozen-lockfile || yarn install")
    parts.append("yarn build" if not use_tsc else f"npx tsc -p {shlex.quote(get_ts_config_path(workdir) or 'tsconfig.json')}")
    cmd = " && ".join(parts)

    if user_at_host:
        return run_remote_cmd(user_at_host, cmd, workdir, outfile)
    else:
        return run_local_cmd(cmd, workdir, outfile)

def run_build_get_errors(
    path: Optional[str] = None,
    *,
    user_at_host: Optional[str] = None,
    use_tsc: bool = True,
    install_first: bool = False
):
    """
    Executes build, then tries to parse TypeScript-like diagnostics if use_tsc=True.
    Otherwise returns the raw build log.
    """
    workdir = if_file_get_dir(path=path) or DEFAULT_MAIN_DIR
    outfile = get_output_path(path=workdir)

    log = run_build(
        path=workdir,
        output_path=outfile,
        user_at_host=user_at_host,
        use_tsc=use_tsc,
        install_first=install_first,
    )

    # If you truly need tsc-style parsing, make sure you ran tsc.
    try:
       
        if use_tsc:
            return parse_tsc_output(log)
    except Exception:
        pass
    return log
