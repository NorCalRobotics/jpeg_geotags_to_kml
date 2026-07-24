import os
import json
import glob
from pathlib import Path

# Files you want to purge from the browser cache
TARGET_STRINGS = [b'pwa.py']
manifest = json.load(open('conv_pys.json', 'r'))
TARGET_STRINGS += [os.path.basename(k).encode('utf-8') for k in manifest["files"].keys()]

# Path pattern matching Brave Cache directories on Linux
CACHE_PATTERN = os.path.expanduser('~/.cache/BraveSoftware/Brave-Browser/*/Cache/Cache_Data/*')

def clear_cache():
    removed_count = 0
    error_count = 0

    print("Searching for stale Pyodide script references in Brave cache...")

    # Iterate through all files in the cache directories
    for file_path in glob.glob(CACHE_PATTERN):
        path = Path(file_path)

        # Skip directories
        if not path.is_file():
            continue

        try:
            # Read cache file binary content
            content = path.read_bytes()

            # Check if any target string is present in the cache file
            if any(target in content for target in TARGET_STRINGS):
                path.unlink()  # Delete the file
                print(f"Deleted: {path.name}")
                removed_count += 1

        except (PermissionError, FileNotFoundError):
            # Handle locked files or transient browser cache locks
            error_count += 1
            continue
        except Exception as e:
            print(f"Error reading {path.name}: {e}")
            error_count += 1

    print(f"\nDone! Removed {removed_count} stale cache files. ({error_count} skipped/locked)")

if __name__ == "__main__":
    clear_cache()