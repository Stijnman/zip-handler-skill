# ZIP Handler Skill

**Description:** Safe ZIP archive handling skill for AI agents, implemented in Python.

**Purpose:** Use this skill when an agent needs to inspect, safely extract, selectively extract, or create ZIP archives.

## Capabilities

- List archive contents and metadata.
- Extract archives with zip-slip/path-traversal protection.
- Selectively extract requested members.
- Read traditional ZipCrypto-protected archives when a password is supplied.
- Create ZIP archives from files and directories while preserving structure.

## Scripts

- `scripts/list_zip.py` — list archive contents.
- `scripts/safe_extract.py` — extract archives with path-safety checks.
- `scripts/create_zip.py` — create ZIP archives.

## Usage

Run the relevant script with `--help` for its supported arguments. Keep archive input and extraction output inside the agent's approved workspace. Validate destination paths before writing files and never disable the traversal protections for untrusted archives.

## Security

ZIP files are untrusted input. Extraction must reject members that escape the destination directory. Review archive contents before extraction when provenance is unknown. Do not commit archive passwords, tokens, or other secrets.

## Requirements

Python 3.11+ is recommended. The core scripts use Python's standard library unless a script documents an additional dependency.

## License

See `LICENSE` for the repository's license terms.
