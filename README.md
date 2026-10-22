simply open firefox, go to the console, and run this spiffy command and it shall capture your captions.

## Files

```
firefox/webex-caption-capper-firefox-watcher.txt   <- use this one
firefox/webex-caption-capper-firefox.txt           (older one-shot version)
chrome/webex-caption-capper-chrome-watcher.txt     <- use this one
chrome/webex-caption-capper-chrome.txt             (older one-shot version)
```

The Firefox and Chrome copies are the same script. The watcher is the version that gets updated from now on; the one-shot version is kept as-is.

## Chrome: pick the meeting frame first

The meeting runs in a cross-origin iframe, and a script pasted into the outer `<yoursite>.webex.com` page isn't allowed to read it. Quickest fix: right-click any caption and choose Inspect. The Console should then switch to the meeting frame, so you can just paste. (Or pick `web.webex.com/meeting` in the Console's context dropdown.) If you paste it in the wrong frame, the script tells you.

## Watcher

Paste it once, with the Captions panel open, and leave the tab open. It:

- Downloads the complete transcript right away.
- Reads new captions every 2 seconds and saves them in the browser (localStorage), so a caption is kept as soon as it appears.
- Downloads the latest transcript every 5 minutes, but only if something changed.
- Downloads immediately when the captions panel disappears (the meeting ended, or you closed the panel). It keeps watching in case the panel comes back.
- Asks "Leave site?" if the meeting page tries to close or navigate away, and downloads first.
- If you scroll the panel up, Webex stops showing new captions, so about once a minute the watcher scrolls back to the bottom to catch up.

Console commands while it runs:

- `webexCaptionCapper.download()`: download the latest transcript now.
- `webexCaptionCapper.stop()`: stop watching (downloads first if anything changed).

Pasting it again restarts it. If the meeting already ended and the captions panel is gone, pasting it offers to download the last saved transcript.

Each download is the complete transcript so far, named `webex-captions-<meetingname>-<YYYY-MM-DD>-<HHMM>.txt` with the time of that download, so older files can be deleted. The meeting name comes from the meeting tab's title, or `meeting` if there isn't one. The intervals are settings at the top of the script.

## Sorting downloads into a folder per meeting

Browsers can't save into a subfolder from a page script, so `sort-caption-downloads.py` does it on your computer. Start it in a terminal before the meeting and leave it running:

```
python3 sort-caption-downloads.py
```

It moves each `webex-captions-<meetingname>-<YYYY-MM-DD>-<HHMM>.txt` in Downloads into `Downloads/webex-captions-<meetingname>-<YYYY-MM-DD>/<HHMM>.txt`. Files that are still downloading are left alone, and nothing is overwritten. To sort everything already in Downloads once and exit, run `./sort-caption-downloads-once.sh` (same as `python3 sort-caption-downloads.py --once`).

## How the transcript is merged

Webex only keeps some captions loaded at a time, and drops them on a reload. The script keeps the full transcript in localStorage, finds where it connects to the captions Webex is currently showing, and adds whatever is new. A caption that was mid-sentence is replaced by its finished version. If no connecting point is found (for example after a reload that cleared the caption list), the new captions are added after a `[... some captions may be missing here ...]` line.

A meeting that hasn't been captured for 6 hours starts a new transcript. To start over sooner, run the `localStorage.removeItem(...)` command the script prints in the console.

## One-shot version

Each paste scans the panel, merges into the saved transcript, and downloads it once. Reruns only scroll back as far as the captions already saved, so they're quick.
