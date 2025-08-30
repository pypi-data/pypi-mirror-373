import os
import subprocess
from pathlib import Path
from .. import unidbg_server
from ..utils import init_logger

def run(core, projects, host="127.0.0.1", port=8888, workers=1, log_level="DEBUG", log_file=None, with_stream=True):
    """
    Start the unidbg_server.

    Behavior differs based on OS:
    - Windows: uses Uvicorn single-process mode
    - Linux/macOS: uses Gunicorn with UvicornWorker (multi-process)
    - Logs can be written to file or console (single or multi-process)
    """
    base_dir = Path.cwd()

    # ------------------ Handle log file path ------------------
    if log_file:
        if not os.path.isabs(log_file):
            log_file = base_dir / "logs" / log_file
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # ------------------ Set server directories ------------------
    unidbg_server.BASE_DIR = base_dir
    unidbg_server.CORE_DIR = Path(core)
    unidbg_server.PROJECTS_DIR = Path(projects)

    # ------------------ Initialize logging ------------------
    logger = init_logger(
        log_level=log_level,
        log_file=log_file,
        with_stream=with_stream,
    )

    if os.name == "nt":
        # ------------------ Windows single-process start ------------------
        print("⚠ Windows detected: running single-process Gunicorn")
        workers = 1
        import uvicorn
        uvicorn.run("py_unidbg_server.unidbg_server:create_app", host=host, port=port, workers=1, factory=True)
    else:
        # ------------------ Linux/macOS Gunicorn start ------------------
        gunicorn_cmd = [
            "gunicorn",
            "-k", "uvicorn.workers.UvicornWorker",
            "-w", str(workers),
            "-b", f"{host}:{port}",
            "--log-level", log_level.lower(),
            "--access-logfile", log_file if log_file else "-", # stdout if no log file
            "--error-logfile", log_file if log_file else "-",  # error log file or stdout
            "py_unidbg_server.unidbg_server:create_app"
        ]
        subprocess.run(gunicorn_cmd)
