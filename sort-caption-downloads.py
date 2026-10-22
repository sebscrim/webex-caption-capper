#!/usr/bin/env python3
"""Sort Webex caption downloads into a folder per meeting.

Browsers can't save into a subfolder from a page script, so this watches
the Downloads folder and moves each

    webex-captions-<meeting>-<YYYY-MM-DD>-<HHMM>.txt

into

    webex-captions-<meeting>-<YYYY-MM-DD>/<HHMM>.txt

Usage:
    python3 sort-caption-downloads.py            # keep watching (Ctrl+C to stop)
    python3 sort-caption-downloads.py --once     # sort what's there and exit
    python3 sort-caption-downloads.py --dir PATH # use another Downloads folder
"""

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

PATTERN = re.compile(
    r"^webex-captions-(?P<meeting>.+)-(?P<date>\d{4}-\d{2}-\d{2})"
    r"-(?P<time>\d{4})(?P<extra>.*)\.txt$"
)

# Ignore files touched more recently than this, in case they're still
# being written.
SETTLE_SECONDS = 1.0


def downloads_dir():
    try:
        out = subprocess.run(
            ["xdg-user-dir", "DOWNLOAD"], capture_output=True, text=True
        ).stdout.strip()
        if out:
            return Path(out)
    except FileNotFoundError:
        pass
    return Path.home() / "Downloads"


def free_name(path):
    # Don't overwrite an existing file: 1942.txt -> 1942-2.txt, ...
    n = 2
    candidate = path
    while candidate.exists():
        candidate = path.with_name(f"{path.stem}-{n}{path.suffix}")
        n += 1
    return candidate


def sort_once(folder):
    for path in folder.iterdir():
        match = PATTERN.match(path.name)
        if not match or not path.is_file():
            continue

        # Firefox writes into <name>.part next to the final file.
        if path.with_name(path.name + ".part").exists():
            continue

        stat = path.stat()
        if stat.st_size == 0 or time.time() - stat.st_mtime < SETTLE_SECONDS:
            continue

        target_dir = folder / f"webex-captions-{match['meeting']}-{match['date']}"
        target_dir.mkdir(exist_ok=True)
        target = free_name(target_dir / f"{match['time']}{match['extra']}.txt")

        path.rename(target)
        print(f"{path.name} -> {target.relative_to(folder)}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dir", type=Path, default=None,
                        help="Downloads folder (default: your Downloads folder)")
    parser.add_argument("--once", action="store_true",
                        help="sort existing files and exit")
    args = parser.parse_args()

    folder = (args.dir or downloads_dir()).expanduser()
    if not folder.is_dir():
        sys.exit(f"Not a folder: {folder}")

    sort_once(folder)
    if args.once:
        return

    print(f"Watching {folder} for Webex caption downloads (Ctrl+C to stop)...",
          flush=True)
    try:
        while True:
            time.sleep(2)
            sort_once(folder)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
