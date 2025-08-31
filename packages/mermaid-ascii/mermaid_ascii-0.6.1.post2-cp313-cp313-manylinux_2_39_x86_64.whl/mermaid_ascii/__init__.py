"""Mermaid-ASCII CLI wrapper."""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Optional


def _candidate_basenames() -> list[str]:
    """Return executable basenames to try for this platform."""
    if platform.system() == 'Windows':
        return ['mermaid-ascii.exe', 'mermaid-ascii']
    return ['mermaid-ascii', 'mermaid-ascii.exe']


def _find_packaged_binary() -> Optional[Path]:
    """Look for the packaged binary next to this module."""
    pkg_dir = Path(__file__).parent
    for name in _candidate_basenames():
        p = pkg_dir / name
        if p.exists():
            return p
    return None


def _resolve_binary() -> str:
    """
    Resolve the mermaid-ascii executable.

    Order:
      1) Packaged binary in this wheel (next to this module)
      2) System PATH
    """
    packaged = _find_packaged_binary()
    if packaged is not None:
        return str(packaged)

    exe_name = (
        'mermaid-ascii.exe'
        if platform.system() == 'Windows'
        else 'mermaid-ascii'
    )
    found = shutil.which(exe_name)
    if found:
        return found

    raise FileNotFoundError(
        "Could not find the 'mermaid-ascii' binary. "
        'Ensure the wheel includes it or that it is on PATH.'
    )


def _extract_file_arg(argv: List[str]) -> Tuple[List[str], Optional[str]]:
    """
    Find -f/--file argument in argv.

    If present and not '-', return:
      (argv_with_-f - , file_path)
    Otherwise return (argv, None).
    Supports: -f path, -f=path, --file path, --file=path
    """
    new_args: List[str] = [argv[0]]
    file_path: Optional[str] = None
    i = 1
    while i < len(argv):
        a = argv[i]
        if a in ('-f', '--file'):
            if i + 1 < len(argv):
                file_path = argv[i + 1]
                new_args.extend([a, '-'])  # <- always pipe via stdin
                i += 2
                continue
        elif a.startswith('-f='):
            file_path = a.split('=', 1)[1]
            new_args.extend(['-f', '-'])  # <- fix: use two args
            i += 1
            continue
        elif a.startswith('--file='):
            file_path = a.split('=', 1)[1]
            new_args.extend(['--file', '-'])  # <- fix: two args
            i += 1
            continue

        new_args.append(a)
        i += 1

    if file_path == '-':
        file_path = None
    return new_args, file_path


def run(args: List[str]) -> int:
    """
    Run the underlying mermaid-ascii binary, forwarding CLI args.

    If -f/--file points to a file, normalize newlines and pipe via stdin.
    """
    bin_path = _resolve_binary()
    forwarded, file_path = _extract_file_arg(args)

    input_text: Optional[str] = None
    if file_path:
        p = Path(file_path)
        # Strip UTF-8 BOM if present and normalize line endings
        txt = p.read_text(encoding='utf-8-sig')
        txt = txt.lstrip('\ufeff').replace('\r\n', '\n').replace('\r', '\n')
        input_text = txt

    if input_text is None:
        completed = subprocess.run([bin_path] + forwarded[1:])
    else:
        completed = subprocess.run(
            [bin_path] + forwarded[1:], input=input_text, text=True
        )
    return completed.returncode


def mermaid_ascii() -> None:
    """Console entry point."""
    sys.exit(run(sys.argv))


if __name__ == '__main__':
    mermaid_ascii()
