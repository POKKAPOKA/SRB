# TAiKOTYPiNG ranking test sender

A small Python script for sending test ranking records to the TAiKOTYPiNG site.
It uses only the Python standard library and fetches the current song list and
public RPC settings from the site when run.

## Requirements

- Python 3.9 or newer
- Internet access

## Run

```powershell
python -X utf8 test_submit_score.py
```

Choose a song number from the terminal list, enter a player name and score, then
review the payload. Enter `y` to send it. Choose `0` to send the same test result
to every listed song. Each run uses a new device ID by default. Use
`--reuse-device` to keep a local device ID and update the corresponding best
record for each song.

Use `--dry-run` to print the requests without sending them.

This tool writes records to the site's ranking database. Only use it against an
environment you own or are authorized to test.
