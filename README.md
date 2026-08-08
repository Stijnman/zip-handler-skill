# zip-handler-skill

The repository [Stijnman/zip-handler-skill](https://github.com/Stijnman/zip-handler-skill/tree/main) is a **safe ZIP archive handler skill** designed for the **Grok / xAI agent ecosystem**. It provides the following features:

- List ZIP contents (basic and verbose modes with compressed size and timestamps).
- Safe extraction with **zip-slip protection** to prevent directory traversal attacks.
- Selective extraction via the `--files` argument.
- Optional password support for traditional ZipCrypto reading.
- Create ZIP archives from files and folders, preserving directory structure and empty directories.
- Designed for sandboxed use under `/home/workdir/artifacts`.

### Repository Structure
- **Scripts**:
  - [`list_zip.py`](https://github.com/Stijnman/zip-handler-skill/blob/main/scripts/list_zip.py): Lists contents of a ZIP file.
  - [`safe_extract.py`](https://github.com/Stijnman/zip-handler-skill/blob/main/scripts/safe_extract.py): Safely extracts ZIP files with zip-slip protection.
  - [`create_zip.py`](https://github.com/Stijnman/zip-handler-skill/blob/main/scripts/create_zip.py): Creates ZIP archives from files and folders.

- **Documentation**:
  - [`README.md`](https://github.com/Stijnman/zip-handler-skill/blob/main/README.md): Installation and usage instructions.
  - [`SKILL.md`](https://github.com/Stijnman/zip-handler-skill/blob/main/SKILL.md): Skill definition and trigger phrases (e.g., *unzip, extract zip, open zip, create zip, list zip, pack into zip*).

### Installation
Place the `zip-handler/` directory under the agent skills path (e.g., `~/.grok/skills/`).

### License
Free for use in Grok ecosystems. The repository is written in **Python**.
