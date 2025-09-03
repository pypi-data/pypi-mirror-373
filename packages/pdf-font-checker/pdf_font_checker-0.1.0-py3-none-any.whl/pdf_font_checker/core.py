\
import platform
import shutil
import subprocess
import sys
import re
from typing import List, Set

def _run(cmd: list) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def _have(cmd_name: str) -> bool:
    return shutil.which(cmd_name) is not None

def _os() -> str:
    return platform.system()  # "Linux", "Darwin", "Windows", etc.

def ensure_mutool(auto_install: bool = True) -> None:
    """
    Ensure MuPDF's 'mutool' is available on PATH. If not, try to install
    using the system package manager (Linux/macOS). On failure, raise RuntimeError.
    """
    if _have("mutool"):
        return

    if not auto_install:
        raise RuntimeError("mutool not found on PATH, and auto_install is disabled.")

    system = _os()
    cmds_tried = []

    if system == "Darwin":
        # macOS via Homebrew
        if _have("brew"):
            cmd = ["brew", "install", "mupdf-tools"]
            cmds_tried.append(" ".join(cmd))
            proc = _run(cmd)
            if proc.returncode == 0 and _have("mutool"):
                return
        raise RuntimeError("Failed to install mupdf-tools via Homebrew.\n"
                           "Try installing Homebrew and then run:\n  brew install mupdf-tools")

    elif system == "Linux":
        # Try common package managers
        pm_commands = [
            (["apt-get", "update"], True),
            (["apt-get", "install", "-y", "mupdf-tools"], False),
            (["dnf", "install", "-y", "mupdf-tools"], False),
            (["yum", "install", "-y", "mupdf-tools"], False),
            (["pacman", "-S", "--noconfirm", "mupdf-tools"], False),
            (["zypper", "--non-interactive", "install", "mupdf-tools"], False),
            # Fallbacks (some distros package as 'mupdf')
            (["dnf", "install", "-y", "mupdf"], False),
            (["yum", "install", "-y", "mupdf"], False),
            (["pacman", "-S", "--noconfirm", "mupdf"], False),
            (["zypper", "--non-interactive", "install", "mupdf"], False),
        ]

        for cmd, ignore_rc in pm_commands:
            if not _have(cmd[0]):
                continue
            cmds_tried.append(" ".join(cmd))
            proc = _run(["sudo"] + cmd) if cmd[0] in ("apt-get","dnf","yum","zypper") else _run(cmd)
            if ignore_rc or proc.returncode == 0:
                if _have("mutool"):
                    return

        raise RuntimeError("Could not install 'mupdf-tools' automatically.\n"
                           "Tried:\n  - " + "\n  - ".join(cmds_tried) +
                           "\nPlease install it manually using your distro's package manager.")

    else:
        raise RuntimeError(f"Unsupported OS for auto-install: {system}. Please install 'mupdf-tools' manually.")

def _parse_mutool_fonts(output: str) -> List[str]:
    """
    Try to parse font names from 'mutool info -F' output.
    We support multiple line styles, e.g.:
      name: 'Helvetica-Bold'
      FontName: /TimesNewRomanPSMT
      basefont Times-Roman
    Returns unique font names (preserving first-seen order).
    """
    names: List[str] = []
    seen: Set[str] = set()

    # Common regex patterns encountered across mutool builds
    patterns = [
        r"name:\s*'([^']+)'",
        r"FontName:\s*/?([A-Za-z0-9_.\-+]+)",
        r"basefont\s+([A-Za-z0-9_.\-+]+)",
        r"/([A-Za-z0-9_.\-+]+)\s+Type0",
        r"/([A-Za-z0-9_.\-+]+)\s+Type1",
        r"/([A-Za-z0-9_.\-+]+)\s+TrueType",
        r"/([A-Za-z0-9_.\-+]+)\s+CIDFontType0",
        r"/([A-Za-z0-9_.\-+]+)\s+CIDFontType2",
    ]

    for line in output.splitlines():
        for pat in patterns:
            m = re.search(pat, line)
            if m:
                candidate = m.group(1)
                if candidate and candidate not in seen:
                    seen.add(candidate)
                    names.append(candidate)
    return names

def list_pdf_fonts(pdf_path: str, ensure=True, auto_install=True) -> List[str]:
    """
    Ensure mutool exists (optionally auto-install), run 'mutool info -F <pdf>',
    parse and return a de-duplicated list of font names.
    """
    if ensure:
        ensure_mutool(auto_install=auto_install)

    # Prefer 'mutool info -F', fallback to 'mutool info'
    cmds = [
        ["mutool", "info", "-F", pdf_path],
        ["mutool", "info", pdf_path],
    ]
    last_err = ""
    for cmd in cmds:
        proc = _run(cmd)
        if proc.returncode == 0 and proc.stdout.strip():
            return _parse_mutool_fonts(proc.stdout)
        last_err = proc.stderr

    raise RuntimeError(f"Failed to extract fonts using mutool.\nLast stderr:\n{last_err}")
