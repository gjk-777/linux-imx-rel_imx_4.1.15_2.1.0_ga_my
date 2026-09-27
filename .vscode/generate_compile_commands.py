#!/usr/bin/env python3
"""Generate a compile database from the commands saved by the kernel build."""

import json
import re
import shlex
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = Path(__file__).resolve().parent / "compile_commands.json"
SOURCE_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".C"}
COMMAND_RE = re.compile(r"^cmd_[^ ]+ := (.+)$")


def main():
    entries = {}
    for command_file in ROOT.rglob("*.cmd"):
        for line in command_file.read_text(errors="replace").splitlines():
            match = COMMAND_RE.match(line)
            if not match or " -c -o " not in match.group(1):
                continue

            command = match.group(1).strip()
            try:
                tokens = shlex.split(command)
            except ValueError:
                continue
            if not tokens or "-c" not in tokens:
                continue

            source = Path(tokens[-1])
            if source.suffix not in SOURCE_SUFFIXES:
                continue
            source_path = source if source.is_absolute() else ROOT / source
            if not source_path.is_file():
                continue

            source_path = source_path.resolve()
            entries[str(source_path)] = {
                "directory": str(ROOT),
                "file": str(source_path),
                "command": command,
            }

    database = sorted(entries.values(), key=lambda entry: entry["file"])
    OUTPUT.write_text(json.dumps(database, indent=2) + "\n")
    print(f"wrote {len(database)} compile commands to {OUTPUT}")


if __name__ == "__main__":
    main()
