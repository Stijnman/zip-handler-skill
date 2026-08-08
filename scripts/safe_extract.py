#!/usr/bin/env python3
"""
Safe ZIP extraction that blocks path traversal (zip-slip), defends against zipbombs,
and exposes extract_zip() for tests/benchmarks.

Usage (CLI):
  python3 scripts/safe_extract.py archive.zip /target/dir [--files file1 file2 ...] [--password SECRET]
"""
from __future__ import annotations

import argparse
import os
import sys
import zipfile
from pathlib import Path
from typing import Iterable, List, Tuple, Dict
import shutil

CHUNK_SIZE = 64 * 1024

DEFAULT_MAX_MEMBERS = 10000
DEFAULT_MAX_MEMBER_SIZE = 200 * 1024 * 1024     # 200 MB per member
DEFAULT_MAX_TOTAL_SIZE = 2 * 1024 * 1024 * 1024  # 2 GB total uncompressed

class ExtractionError(Exception):
    pass

def is_safe_member_name(member: str) -> bool:
    # Reject absolute or traversal components in the member name itself.
    p = Path(member)
    if p.is_absolute():
        return False
    parts = p.parts
    if ".." in parts:
        return False
    return True

def _safe_target_path(member: str, target_dir: Path) -> Path:
    # Build the intended path and ensure it's inside target_dir
    candidate = (target_dir / member)
    # Do not resolve until file is written — resolve parent first to catch symlinked dirs
    parent = candidate.parent
    parent.mkdir(parents=True, exist_ok=True)
    try:
        resolved_parent = parent.resolve()
    except Exception:
        # If resolution fails, be conservative and raise
        raise ExtractionError(f"Unable to resolve parent directory for member: {member}")
    try:
        resolved_parent.relative_to(target_dir.resolve())
    except Exception:
        raise ExtractionError(f"Unsafe extraction path (outside target): {member}")
    return resolved_parent / candidate.name

def extract_zip(
    zip_path: Path,
    target_dir: Path,
    members: Iterable[str] | None = None,
    password: str | None = None,
    *,
    max_members: int = DEFAULT_MAX_MEMBERS,
    max_member_size: int = DEFAULT_MAX_MEMBER_SIZE,
    max_total_uncompressed: int = DEFAULT_MAX_TOTAL_SIZE,
) -> Dict:
    """
    Extract members from zip_path into target_dir safely.

    Returns a dict summary:
      { "extracted": [paths], "skipped": [members], "errors": [messages], "total_uncompressed": int }
    """
    if not zip_path.is_file():
        raise ExtractionError(f"ZIP not found: {zip_path}")

    target_dir.mkdir(parents=True, exist_ok=True)
    target_resolved = target_dir.resolve()

    pwd = password.encode("utf-8") if password else None
    extracted: List[str] = []
    skipped: List[str] = []
    errors: List[str] = []
    total_uncompressed = 0
    seen = 0

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            if pwd:
                zf.setpassword(pwd)
            all_members = members if members is not None else zf.namelist()

            for member in all_members:
                seen += 1
                if seen > max_members:
                    skipped.append(member)
                    errors.append(f"member-limit-exceeded at {member}")
                    break

                # Basic name checks
                if not is_safe_member_name(member):
                    skipped.append(member)
                    errors.append(f"unsafe-name: {member}")
                    continue

                try:
                    info = zf.getinfo(member)
                except KeyError:
                    skipped.append(member)
                    errors.append(f"missing-member: {member}")
                    continue

                # Directories - ensure directory exists
                is_dir = member.endswith("/")
                uncompressed_size = info.file_size or 0

                if uncompressed_size > max_member_size:
                    skipped.append(member)
                    errors.append(f"member-too-large: {member} ({uncompressed_size} bytes)")
                    continue

                if total_uncompressed + uncompressed_size > max_total_uncompressed:
                    skipped.append(member)
                    errors.append("total-uncompressed-limit-exceeded")
                    break

                try:
                    out_path = _safe_target_path(member, target_resolved)
                except ExtractionError as e:
                    skipped.append(member)
                    errors.append(str(e))
                    continue

                if is_dir:
                    out_path.mkdir(parents=True, exist_ok=True)
                    extracted.append(str(out_path))
                    continue

                # Extract file by streaming to avoid uncontrolled memory usage
                try:
                    with zf.open(info, "r", pwd) as src:
                        # If the member is a symlink encoded in Unix attributes, skip for safety
                        # (zipfile does not expose symlink directly; some archives store symlinks as files with specific attributes)
                        # Safer default: treat as regular file content.
                        tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")
                        with open(tmp_path, "wb") as dst:
                            written = 0
                            while True:
                                chunk = src.read(CHUNK_SIZE)
                                if not chunk:
                                    break
                                dst.write(chunk)
                                written += len(chunk)
                                if written > max_member_size:
                                    dst.close()
                                    tmp_path.unlink(missing_ok=True)
                                    raise ExtractionError(f"member-too-large-during-write: {member}")
                        # Final resolution safety check
                        final_resolved = tmp_path.resolve()
                        try:
                            final_resolved.relative_to(target_resolved)
                        except Exception:
                            tmp_path.unlink(missing_ok=True)
                            raise ExtractionError(f"extracted-path-outside-target: {member}")
                        # Atomic replace
                        tmp_path.replace(out_path)
                        extracted.append(str(out_path))
                        total_uncompressed += written
                except RuntimeError as e:
                    # bad password / encrypted member
                    raise ExtractionError(f"runtime-error extracting {member}: {e}")
                except zipfile.BadZipFile as e:
                    raise ExtractionError(f"bad-zipfile: {e}")
                except ExtractionError:
                    # re-raise to be caught outer
                    raise
                except Exception as e:
                    skipped.append(member)
                    errors.append(f"error-extracting-{member}: {e}")
                    continue

    except zipfile.BadZipFile as e:
        raise ExtractionError(f"corrupt-or-invalid-zip: {e}")

    return {
        "extracted": extracted,
        "skipped": skipped,
        "errors": errors,
        "total_uncompressed": total_uncompressed,
    }

def main():
    parser = argparse.ArgumentParser(description="Safely extract a ZIP archive")
    parser.add_argument("zip_path", help="Path to the .zip file")
    parser.add_argument("target_dir", help="Directory to extract into")
    parser.add_argument("--files", nargs="*", default=None, help="Optional members to extract (default: all)")
    parser.add_argument("--password", default=None, help="Password for encrypted ZIP (ZipCrypto only)")
    parser.add_argument("--max-members", type=int, default=DEFAULT_MAX_MEMBERS, help="Maximum number of members to process")
    parser.add_argument("--max-member-size", type=int, default=DEFAULT_MAX_MEMBER_SIZE, help="Max uncompressed bytes allowed per member")
    parser.add_argument("--max-total-uncompressed", type=int, default=DEFAULT_MAX_TOTAL_SIZE, help="Max total uncompressed bytes allowed")
    args = parser.parse_args()

    zip_path = Path(args.zip_path)
    target_dir = Path(args.target_dir)

    try:
        res = extract_zip(
            zip_path,
            target_dir,
            members=args.files,
            password=args.password,
            max_members=args.max_members,
            max_member_size=args.max_member_size,
            max_total_uncompressed=args.max_total_uncompressed,
        )
    except ExtractionError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if res["errors"]:
        for e in res["errors"]:
            print(f"ERROR: {e}", file=sys.stderr)
    if res["skipped"]:
        for s in res["skipped"]:
            print(f"SKIPPED: {s}", file=sys.stderr)

    for p in res["extracted"]:
        print(f"EXTRACTED: {p}")

    print(f"\nDone. Extracted {len(res['extracted'])} item(s) into {target_dir}")
