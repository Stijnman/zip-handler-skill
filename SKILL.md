---
name: zip-handler
description: Handles ZIP archives including list contents, extract full or selected files to a safe target under artifacts, create new ZIPs from files or folders, and then open or read the extracted contents. Trigger on unzip, extract zip, open zip file, create zip, zip these files, list zip, pack into zip, or any ZIP archive request.
---

# Zip Handler

## Overview
Provides reliable, safe ZIP archive operations inside the sandbox. Prefer the bundled scripts for extraction and creation to avoid path-traversal (zip-slip) and accidental overwrites.

## Core Rules
- Always work under `/home/workdir/artifacts` unless the user explicitly demands otherwise.
- Never extract with absolute paths or `../` traversal. Use the safe scripts.
- After extraction, use normal `read_file`, `bash`, or other tools to inspect the resulting files.
- Report exact paths of every created or extracted item.
- Prefer Python `zipfile` (via scripts) over raw `unzip`/`zip` for safety and control. Fall back to system tools only when needed.

## Operations

### 1. List contents
Use the helper:
```bash
python3 /home/workdir/.grok/skills/zip-handler/scripts/list_zip.py /path/to/archive.zip
```

### 2. Extract (full or selected)
Use the safe extractor (recommended):
```bash
python3 /home/workdir/.grok/skills/zip-handler/scripts/safe_extract.py /path/to/archive.zip /home/workdir/artifacts/extracted-name [--files file1 file2 ...] [--password SECRET]
```
- Creates the target directory if missing.
- Rejects any member with absolute path or `..` components.
- Supports selective extraction via `--files`.
- Optional `--password` for traditional ZipCrypto encrypted members.
- Prints every extracted path.

Fallback (less safe):
```bash
mkdir -p /home/workdir/artifacts/extracted-name
unzip -o /path/to/archive.zip -d /home/workdir/artifacts/extracted-name
```

### 3. Create ZIP
Use the safe creator:
```bash
python3 /home/workdir/.grok/skills/zip-handler/scripts/create_zip.py /home/workdir/artifacts/output.zip file1.txt folder/ [more paths...]
```
- Stores relative paths and preserves top-level directory names.
- Skips non-existent paths with a warning.
- Overwrites the target ZIP if it already exists.

Fallback:
```bash
zip -r /home/workdir/artifacts/output.zip file1.txt folder/
```

### 4. Extract then open/read
1. Run the extract step above.
2. Immediately use `read_file`, `bash cat/head`, or other file tools on the resulting paths under the extract directory.
3. If the user wants a specific internal file, extract only that member first with `--files`.

## Scripts
- `scripts/safe_extract.py` — path-traversal-safe extraction (full or selective)
- `scripts/create_zip.py` — create ZIP from files/folders with relative names
- `scripts/list_zip.py` — clean listing of archive members + sizes

## Known Limitations / Remaining Weaknesses
- Password support is read-only (traditional ZipCrypto). Writing encrypted ZIPs and AES still unsupported (stdlib limitation).
- Empty directories are now stored when possible, but some edge cases remain.
- No progress bar or streaming for very large archives.
- No compression level control or store-only mode flag.
- No support for multi-volume or exotic ZIP variants.
- No recursive exclusion filters (e.g. --exclude .git).
- Unicode filenames work on modern filesystems but encoding can still bite on weird locales.

## Error handling
- Missing ZIP → clear error, do not invent content.
- Corrupt ZIP → report the exception message.
- Permission / disk space → surface the real OS error.
- Always log the exact command that was run and the final paths produced.
