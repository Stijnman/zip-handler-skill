# zip-handler

Safe ZIP archive handler skill for the Grok / xAI agent ecosystem.

## Features
- List ZIP contents (basic + verbose with compressed size & timestamps)
- Safe extraction with **zip-slip protection**
- Selective extract via `--files`
- Optional password support (traditional ZipCrypto read)
- Create ZIPs from files and folders (preserves structure + empty dirs)
- Designed for sandbox use under `/home/workdir/artifacts`

## Installation / Usage
Place the `zip-handler/` directory under your agent skills path (`~/.grok/skills/` or equivalent).

Trigger phrases: unzip, extract zip, open zip, create zip, list zip, pack into zip, etc.

## Scripts
- `scripts/list_zip.py`
- `scripts/safe_extract.py`
- `scripts/create_zip.py`

## License
Use freely in Grok ecosystems.
