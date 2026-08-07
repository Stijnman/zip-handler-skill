#!/usr/bin/env python3
"""List contents of a ZIP archive with sizes, compressed size, and date."""

import argparse
import sys
import zipfile
from datetime import datetime
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="List ZIP contents")
    parser.add_argument("zip_path", help="Path to the .zip file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show more details")
    args = parser.parse_args()

    zip_path = Path(args.zip_path)
    if not zip_path.is_file():
        print(f"ERROR: ZIP not found: {zip_path}", file=sys.stderr)
        sys.exit(1)

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            print(f"Archive: {zip_path}")
            if args.verbose:
                print(f"{'Size':>10} {'Comp':>10} {'Date':>19}  Name")
                print("-" * 70)
            else:
                print(f"{'Size':>12}  Name")
                print("-" * 60)
            total = 0
            total_comp = 0
            for info in zf.infolist():
                total += info.file_size
                total_comp += info.compress_size
                if args.verbose:
                    try:
                        dt = datetime(*info.date_time).strftime("%Y-%m-%d %H:%M:%S")
                    except Exception:
                        dt = "????-??-?? ??:??:??"
                    print(f"{info.file_size:>10} {info.compress_size:>10} {dt:>19}  {info.filename}")
                else:
                    print(f"{info.file_size:>12}  {info.filename}")
            if args.verbose:
                print("-" * 70)
                print(f"{total:>10} {total_comp:>10}  TOTAL ({len(zf.infolist())} members)")
            else:
                print("-" * 60)
                print(f"{total:>12}  TOTAL ({len(zf.infolist())} members)")
    except zipfile.BadZipFile as e:
        print(f"ERROR: corrupt or invalid ZIP: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
