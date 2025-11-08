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
- `copy_tree` - This is just a wrapper around `shutil.copytree`, yes I know about robocopy - was using this to have more control though.