import argparse
from . import start, edit

def main():
    parser = argparse.ArgumentParser(prog="unidbg_server", description="unidbg_server CLI tool")
    subparsers = parser.add_subparsers(dest="command")

    # start command
    start_parser = subparsers.add_parser("start", help="Start the Unidbg server (FastAPI + JVM).")
    start_parser.add_argument("-c", "--core", default="unidbg_core", help="Directory containing core JAR files (default: %(default)s, relative to current directory).")
    start_parser.add_argument("-p", "--projects", default="projects", help="Directory containing project folders (default: %(default)s, relative to current directory).")
    start_parser.add_argument("--host", default="127.0.0.1", help="Service host to bind (default: %(default)s).")
    start_parser.add_argument("--port", type=int, default=8888, help="Service port (default: %(default)s).")
    start_parser.add_argument("-w", "--workers", type=int, default=1, help="Number of worker processes for FastAPI/Uvicorn multi-process mode (Linux/macOS only, default: %(default)s).")

    start_parser.add_argument("--log-level", default="DEBUG", help="Logging level (default: %(default)s).")
    start_parser.add_argument("--log-file", help="Path to log file. If not set, logs only to console.")
    start_parser.add_argument("--no-stream", action="store_false", dest="with_stream", help="Disable console output (enabled by default).")

    # edit command
    subparsers.add_parser("edit", help="Edit server configuration or project settings.")

    args = parser.parse_args()

    if args.command == "start":
        log_level = args.log_level
        log_file = args.log_file
        with_stream = args.with_stream
        workers=args.workers
        start.run(args.core, args.projects, args.host, args.port, workers, log_level, log_file, with_stream)
    elif args.command == "edit":
        edit.run()
    else:
        parser.print_help()
