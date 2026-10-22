#!/bin/sh
# Sort every Webex caption download in Downloads into per-meeting folders, then exit.
# Extra arguments are passed through (e.g. --dir PATH).
exec python3 "$(dirname "$0")/sort-caption-downloads.py" --once "$@"
