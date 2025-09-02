"""databricks_cli_utils.py
Utility helpers for interacting with DBFS through the Databricks CLI.

Key helpers
===========
- **get_code_from_databricks_config** – downloads a text file from DBFS and
  returns its UTF‑8 contents.  It now defaults to *no* directory pre‑check so it
  works even when `databricks fs ls` cannot list Unity‑Catalog Volumes.
- **ls_dbfs** – lightweight JSON‑aware wrapper around `databricks fs ls`.
"""
from __future__ import annotations

import json
import subprocess
import tempfile
import pathlib
from typing import Optional, Sequence

__all__: Sequence[str] = ["get_code_from_databricks_config", "ls_dbfs"]

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _run_cli(cli: str, *args: str) -> subprocess.CompletedProcess:  # noqa: D401 – imperative OK
    """Run *cli* with *args* and return the completed ``subprocess`` object."""
    return subprocess.run(
        [cli, *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def ls_dbfs(path: str, *, cli: str = "databricks") -> list[str]:
    """List *path* (non‑recursive) and return the full DBFS paths of children.

    Notes
    -----
    * `databricks fs ls` cannot currently list the **root** of a Unity‑Catalog
      Volume (e.g. ``dbfs:/Volumes/mycat/myschema/myvol``).  You need the
      trailing slash ::

          dbfs:/Volumes/mycat/myschema/myvol/

      Otherwise the CLI returns *"file does not exist"* even though it is a
      directory.  Callers should add the slash themselves if needed.
    """
    proc = _run_cli(cli, "fs", "ls", path, "--output", "json")
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    return [json.loads(line)["path"] for line in proc.stdout.splitlines() if line.strip()]

def get_code_from_databricks_config(
    remote_uri: str,
    *,
    local_path: Optional[pathlib.Path] = None,
    cli: str = "databricks",
    precheck: bool = False,
) -> str:
    """Download *remote_uri* and return its text contents.

    Parameters
    ----------
    remote_uri
        Fully‑qualified DBFS URI (``dbfs:/...``).
    local_path
        If *None* (default), a secure temp file is used.  If a directory, the
        basename of *remote_uri* is appended.
    cli
        Executable name – override if you alias the Databricks CLI.
    precheck
        If *True*, list the parent directory first (safer but slower and may
        fail for Unity‑Catalog Volume roots). If *False* (default), copy
        directly and surface any CLI error.
    """
    # ------------------------------------------------------------------ 0. optional existence check
    if precheck:
        parent = str(pathlib.PurePosixPath(remote_uri).parent) + "/"  # ensure trailing slash
        try:
            children = ls_dbfs(parent, cli=cli)
        except Exception as e:  # noqa: BLE001
            raise FileNotFoundError(
                f"Unable to list directory '{parent}'. Either the path is wrong or your CLI "
                "profile lacks access. Set *precheck=False* to skip this step if listing "
                "Volumes does not work in your environment."
            ) from e
        if remote_uri.rstrip("/") not in children:
            raise FileNotFoundError(
                f"File not found on DBFS: {remote_uri}. Did you spell the name correctly?"
            )

    # ------------------------------------------------------------------ 1. choose local destination
    if local_path is None:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=pathlib.Path(remote_uri).suffix)
        local_file = pathlib.Path(tmp.name)
        tmp.close()
    else:
        local_path = pathlib.Path(local_path)
        local_file = (
            local_path / pathlib.Path(remote_uri).name if local_path.is_dir() else local_path
        )

    # ------------------------------------------------------------------ 2. copy remote → local
    proc = _run_cli(
        cli,
        "fs",
        "cp",
        remote_uri,
        str(local_file),
        "--overwrite",
        "--output",
        "json",
    )
    if proc.returncode != 0:
        raise RuntimeError(
            "Databricks CLI error while copying file:\n" + (proc.stderr or proc.stdout)
        )

    # ------------------------------------------------------------------ 3. read & return text
    try:
        return local_file.read_text("utf-8")
    except Exception as e:  # noqa: BLE001
        raise IOError(f"Unable to read local file '{local_file}'.") from e


if __name__ == "__main__":
    # Quick smoke‑test – replace with a *real* path that exists for you.
    REMOTE_PATH = "dbfs:/Volumes/workspace/default/volume/my_script.py"

    try:
        print(get_code_from_databricks_config(REMOTE_PATH, precheck=False))
    except Exception as exc:  # noqa: BLE001
        print("ERROR:", exc)
