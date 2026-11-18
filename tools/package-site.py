#!/usr/bin/env python3
"""Export this website without Git history, machine metadata or old ZIP exports."""

import argparse
from pathlib import Path
import zipfile


EXCLUDED_DIRECTORIES = {
    ".git", "__MACOSX", "__pycache__", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", ".cache", "node_modules",
}
EXCLUDED_FILES = {".DS_Store", ".Rhistory"}


def include(path, root):
    relative = path.relative_to(root)
    return not (
        any(part in EXCLUDED_DIRECTORIES for part in relative.parts)
        or path.name in EXCLUDED_FILES
        or path.name.startswith("._")
        or path.name.lower().endswith(".zip.tmp")
        or path.suffix.lower() in {".zip", ".pyc", ".pyo"}
    )


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "output", nargs="?", type=Path,
        default=root.parent / (root.name + "-clean.zip"),
        help="Destination ZIP (default: beside the website directory).",
    )
    args = parser.parse_args()
    output = args.output.expanduser().resolve()
    if output.suffix.lower() != ".zip":
        parser.error("The output filename must end in .zip.")
    files = sorted(
        path for path in root.rglob("*")
        if path.is_file() and include(path, root) and path.resolve() != output
    )
    links = [path for path in files if path.is_symlink()]
    if links:
        parser.error("Resolve symbolic links before exporting: " + ", ".join(map(str, links)))
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp")
    try:
        with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for path in files:
                archive.write(path, str(Path(root.name) / path.relative_to(root)))
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"Created {output} ({output.stat().st_size:,} bytes; {len(files)} files).")


if __name__ == "__main__":
    main()
