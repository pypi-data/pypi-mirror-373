from __future__ import annotations
import subprocess,shlex,os
from typing import *
def execute_cmd(*args, outfile=None,**kwargs):
    proc = subprocess.run(*args,**kwargs)
    output = (proc.stdout or "") + (proc.stderr or "")
    if outfile:
        try:
            with open(outfile, "w", encoding="utf-8", errors="ignore") as f:
                f.write(output)
        except Exception:
            pass
    return output
def run_local_cmd(cmd: str, workdir: str, outfile: Optional[str],shell=True, text=True, capture_output=True) -> str:
    """
    Run locally with cwd=workdir. Capture stdout+stderr; optionally tee to outfile.
    """
    return execute_cmd(cmd,outfile=outfile, shell=shell, cwd=workdir, text=text, capture_output=capture_output)

def run_remote_cmd(user_at_host: str, cmd: str, workdir: str, outfile: Optional[str],shell=True, text=True, capture_output=True) -> str:
    """
    Run on remote via SSH; capture stdout+stderr locally; write to local outfile.
    NOTE: we do *not* try to write the file on the remote to avoid later scp.
    """
    remote_cmd = f"cd {shlex.quote(workdir)} && {cmd}"
    full = f"ssh {shlex.quote(user_at_host)} {shlex.quote(remote_cmd)}"
    return execute_cmd(full,outfile=outfile, shell=shell, text=text, capture_output=capture_output)
run_local_cmd = run_local_cmd
run_ssh_cmd = run_remote_cmd
