#!/usr/bin/env python3
"""Create a ZIP archive from files and/or directories using relative paths.
Preserves top-level directory names and can store empty directories.
"""

import argparse
import os
import sys
import zipfile
from pathlib import Path


def add_path(zf: zipfile.ZipFile, path: Path, arcname: str | None = None, include_empty: bool = True):
    """Recursively add a file or directory. Directory name is preserved by default."""
    path = path.resolve()
    if not path.exists():
        print(f"WARNING: skipping non-existent path: {path}", file=sys.stderr)
        return

    if path.is_file():
        name = arcname or path.name
        zf.write(path, arcname=name)
        print(f"ADDED: {path} -> {name}")
    elif path.is_dir():
        # Preserve the directory name in the archive unless arcname is forced
        prefix = Path(arcname) if arcname else Path(path.name)
        # Ensure the directory entry itself exists (for empty dirs)
        dir_arc = str(prefix) + "/"
        if include_empty:
            # Create a directory entry
            info = zipfile.ZipInfo(dir_arc)
            info.external_attr = 0o40755 << 16  # drwxr-xr-x
            zf.writestr(info, b"")
            print(f"ADDED DIR: {dir_arc}")

        for root, dirs, files in os.walk(path):
            root_path = Path(root)
            # Also add intermediate empty-ish dirs if needed
            rel_root = root_path.relative_to(path)
            if rel_root != Path("."):
                inter_dir = str(prefix / rel_root) + "/"
                if include_empty and inter_dir not in zf.namelist():
                    info = zipfile.ZipInfo(inter_dir)
                    info.external_attr = 0o40755 << 16
                    zf.writestr(info, b"")
            for f in files:
                full = root_path / f
                rel = full.relative_to(path)
                arc = str(prefix / rel)
                zf.write(full, arcname=arc)
                print(f"ADDED: {full} -> {arc}")


def main():
    parser = argparse.ArgumentParser(description="Create a ZIP archive")
    parser.add_argument("output_zip", help="Path for the output .zip file")
    parser.add_argument(
        "paths",
        nargs="+",
        help="Files and/or directories to include",
    )
    parser.add_argument(
        "--no-empty-dirs",
        action="store_true",
        help="Do not explicitly store empty directory entries",
    )
    args = parser.parse_args()

    output = Path(args.output_zip)
    output.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in args.paths:
            add_path(zf, Path(p), include_empty=not args.no_empty_dirs)

    print(f"\nCreated: {output} ({output.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
