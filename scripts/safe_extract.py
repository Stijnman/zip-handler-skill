#!/usr/bin/env python3
"""Safe ZIP extraction that blocks path traversal (zip-slip). Supports optional password."""

import argparse
import os
import sys
import zipfile
from pathlib import Path


def is_safe_member(member: str, target_dir: Path) -> bool:
    """Return True only if the member path stays inside target_dir."""
    member_path = Path(member)
    if member_path.is_absolute():
        return False
    # Resolve against target to catch .. traversal
    full = (target_dir / member_path).resolve()
    try:
        full.relative_to(target_dir.resolve())
        return True
    except ValueError:
        return False


def main():
    parser = argparse.ArgumentParser(description="Safely extract a ZIP archive")
    parser.add_argument("zip_path", help="Path to the .zip file")
    parser.add_argument("target_dir", help="Directory to extract into")
    parser.add_argument(
        "--files",
        nargs="*",
        default=None,
        help="Optional list of specific members to extract (default: all)",
    )
    parser.add_argument(
        "--password",
        default=None,
        help="Password for encrypted ZIP (traditional ZipCrypto only)",
    )
    args = parser.parse_args()

    zip_path = Path(args.zip_path)
    target_dir = Path(args.target_dir)

    if not zip_path.is_file():
        print(f"ERROR: ZIP not found: {zip_path}", file=sys.stderr)
        sys.exit(1)

    target_dir.mkdir(parents=True, exist_ok=True)
    target_resolved = target_dir.resolve()

    extracted = []
    skipped = []
    pwd = args.password.encode("utf-8") if args.password else None

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            if pwd:
                zf.setpassword(pwd)
            members = args.files if args.files is not None else zf.namelist()
            for member in members:
                if not is_safe_member(member, target_resolved):
                    skipped.append(member)
                    print(f"SKIP (unsafe path): {member}", file=sys.stderr)
                    continue
                try:
                    zf.extract(member, path=target_dir, pwd=pwd)
                    full_path = target_dir / member
                    extracted.append(str(full_path))
                    print(f"EXTRACTED: {full_path}")
                except RuntimeError as e:
                    if "password" in str(e).lower() or "Bad password" in str(e):
                        print(f"ERROR: bad password or encrypted member: {member}", file=sys.stderr)
                        sys.exit(2)
                    raise
    except zipfile.BadZipFile as e:
        print(f"ERROR: corrupt or invalid ZIP: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if skipped:
        print(f"\nWARNING: {len(skipped)} member(s) skipped due to unsafe paths", file=sys.stderr)
    print(f"\nDone. Extracted {len(extracted)} item(s) into {target_dir}")


if __name__ == "__main__":
    main()
