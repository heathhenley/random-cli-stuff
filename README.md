### Random one-off scripts
Adding some random one-offs or helper / util scripts as they come up


### Running
Use [`uv`](https://docs.astral.sh/uv/) (why would you use anything else at this point? 😀)

Get sync'd with the deps:
```
uv sync
```

Run the cli tool:
```
uv run main.py --help
```

Currently:
- `analyze` - analyze a directory tree, count files that match certain extensions and find duplicates using the SHA-256 hash of the file contents - optionally dump the hashes with a list of files that have that hash to a file (or just the duplicates if you only care about that.)
- `mirror` - mirror a Google Share folder to a local folder - useful when the web UI fails to download large folders, and I don't want to let whole drive sync - this is already mapped to a local drive on my computer via the Drive App
but I want to keep the files on my local drive for easier access and don't want to rely on the Drive App / use offline mode.