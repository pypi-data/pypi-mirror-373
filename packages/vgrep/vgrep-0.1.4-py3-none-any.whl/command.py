"""Command line interface for vgrep.

This module exposes a ``main`` function so it can be used as an entry point
when the project is installed as a package.  The previous implementation kept
most of the logic at module import time, which made reuse difficult.  The
logic has been wrapped in ``main`` so tools like ``setuptools`` can create a
``console_script`` entry point.
"""

import argparse
import fnmatch
import sys
from pathlib import Path
from typing import List

from vgrep.db import QueryResult
from vgrep.manager import Manager


def org_format_result(result: QueryResult) -> str:
    name_link = f"[[{result['filename']}::{result['line_start']}][{result['filename']}]]"
    body = f"#+begin_quote\n{result['text']}\n#+end_quote"
    
    return f"{name_link}\n{body}"
    
def org_format_results(results: List[QueryResult]) -> str:
    return "\n\n".join(map(org_format_result, results))


def main() -> None:
    """Entry point for the ``vgrep`` command line tool."""
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path, help="Directory to index")
    parser.add_argument(
        "-q", "--query", type=str, help="The search string to use for the query"
    )
    parser.add_argument(
        "-s",
        "--sync",
        action="store_true",
        help="Switch to sync the vector db with the file system",
    )
    parser.add_argument(
        "--match", type=str, help="Glob used to match files for syncing"
    )
    args = parser.parse_args()

    match_fn = None
    if args.match:
        pattern = args.match

        def match_fn(p: Path) -> bool:
            return p.is_file() and fnmatch.fnmatch(p.name, pattern)

    manager = Manager(args.path, file_match=match_fn)

    if args.sync:
        print(f'Syncing directory {manager.directory} to db {manager.db_path}')
        manager.sync()
        print("Done.")

    if args.query:
        print(f'Querying {manager.db_path} for files in directory {manager.directory}')
        print(f"Results for '{args.query}'")
        print(org_format_results(manager.query(args.query)))

    if not args.query and not args.sync:
        parser.print_help(sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
