\
import platform
import shutil
import subprocess
import sys
import re
from typing import List, Set, Dict, Any, Optional

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

def _parse_mutool_output(output: str) -> Dict[str, Any]:
    """
    Parse the complete mutool info -F output to extract PDF metadata and font information.
    
    Returns a dictionary containing:
    - pdf_version: PDF version (e.g., "PDF-1.4")
    - info_object: Info object content
    - pages: Number of pages
    - fonts: List of font dictionaries with detailed information
    - font_count: Total number of fonts
    - font_names: List of font names (for backward compatibility)
    """
    result = {
        'pdf_version': None,
        'info_object': None,
        'pages': None,
        'fonts': [],
        'font_count': 0,
        'font_names': []
    }
    
    lines = output.splitlines()
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Extract PDF version
        if line.startswith('PDF-'):
            result['pdf_version'] = line
        
        # Extract info object
        elif line.startswith('Info object'):
            # Extract the object reference
            info_match = re.search(r'Info object \(([^)]+)\):', line)
            if info_match:
                info_ref = info_match.group(1)
                i += 1
                # Get the next line which should contain the info object content
                if i < len(lines):
                    info_content = lines[i].strip()
                    result['info_object'] = {
                        'reference': info_ref,
                        'content': info_content
                    }
        
        # Extract pages count
        elif line.startswith('Pages:'):
            pages_match = re.search(r'Pages:\s*(\d+)', line)
            if pages_match:
                result['pages'] = int(pages_match.group(1))
        
        # Extract fonts section
        elif line.startswith('Fonts (') and '):' in line:
            # Extract font count
            font_count_match = re.search(r'Fonts \((\d+)\):', line)
            if font_count_match:
                result['font_count'] = int(font_count_match.group(1))
            
            # Parse font entries
            i += 1
            while i < len(lines):
                line = lines[i]
                # Check if we've reached the end of the fonts section
                if not line.strip() or (line.strip() and not line.startswith('\t') and not line.startswith('        ')):
                    break
                
                # Parse font line format: "        1       (2 0 R):        Type1 'Helvetica' WinAnsiEncoding (3 0 R)"
                # Remove leading whitespace/tabs for easier parsing
                clean_line = line.strip()
                
                # More flexible regex to handle various spacing
                font_match = re.search(
                    r'^(\d+)\s+\(([^)]+)\):\s+(\w+)\s+\'([^\']+)\'\s+([^\(]+?)(?:\s*\(([^)]+)\))?$',
                    clean_line
                )
                
                if font_match:
                    page_num = int(font_match.group(1))
                    obj_ref = font_match.group(2)
                    font_type = font_match.group(3)
                    font_name = font_match.group(4)
                    encoding = font_match.group(5).strip()
                    encoding_ref = font_match.group(6) if font_match.group(6) else None
                    
                    font_info = {
                        'page': page_num,
                        'object_reference': obj_ref,
                        'type': font_type,
                        'name': font_name,
                        'encoding': encoding,
                        'encoding_reference': encoding_ref
                    }
                    
                    result['fonts'].append(font_info)
                    
                    # Add to font names list for backward compatibility
                    if font_name not in result['font_names']:
                        result['font_names'].append(font_name)
                
                i += 1
            continue
        
        i += 1
    
    return result

def _parse_mutool_fonts(output: str) -> List[str]:
    """
    Legacy function for backward compatibility.
    Extract just font names from mutool output.
    """
    parsed = _parse_mutool_output(output)
    return parsed['font_names']

def get_pdf_info_dict(pdf_path: str, ensure=True, auto_install=True) -> Dict[str, Any]:
    """
    Extract PDF information and return in a simplified dictionary format.
    
    Args:
        pdf_path: Path to the PDF file
        ensure: Check for mutool availability before processing
        auto_install: Attempt to install MuPDF tools automatically
    
    Returns:
        Dictionary containing:
        - pdf_version: PDF version string
        - total_no_of_fonts: Number of fonts
        - font_names: List of font names
        - info_object: Info object reference
    """
    analysis = analyze_pdf(pdf_path, ensure=ensure, auto_install=auto_install)
    
    # Extract info_object reference number only
    info_object_ref = None
    if analysis['info_object'] and analysis['info_object']['reference']:
        info_object_ref = analysis['info_object']['reference']
    
    return {
        "pdf_version": analysis['pdf_version'],
        "total_no_of_fonts": analysis['font_count'],
        "font_names": analysis['font_names'],
        "info_object": info_object_ref
    }

def get_pdf_terminal_output(pdf_path: str, detailed=True, ensure=True, auto_install=True) -> str:
    """
    Get PDF analysis output formatted exactly like the terminal command.
    
    Args:
        pdf_path: Path to the PDF file
        detailed: If True, return detailed output; if False, return just font names
        ensure: Check for mutool availability before processing
        auto_install: Attempt to install MuPDF tools automatically
    
    Returns:
        String formatted exactly like terminal output
    """
    if detailed:
        analysis = analyze_pdf(pdf_path, ensure=ensure, auto_install=auto_install)
        
        output_lines = []
        output_lines.append(f"PDF Version: {analysis['pdf_version'] or 'Unknown'}")
        output_lines.append(f"Pages: {analysis['pages'] or 'Unknown'}")
        
        if analysis['info_object']:
            output_lines.append(f"Info Object ({analysis['info_object']['reference']}): {analysis['info_object']['content']}")
        
        output_lines.append(f"\nFonts ({analysis['font_count']}):")
        if analysis['fonts']:
            for font in analysis['fonts']:
                encoding_info = f" {font['encoding']}"
                if font['encoding_reference']:
                    encoding_info += f" ({font['encoding_reference']})"
                output_lines.append(f"    {font['page']}\t({font['object_reference']}):\t{font['type']} '{font['name']}'{encoding_info}")
        else:
            output_lines.append("    No fonts found or format not recognized.")
        
        return "\n".join(output_lines)
    else:
        # Just return font names like the basic command
        fonts = list_pdf_fonts(pdf_path, ensure=ensure, auto_install=auto_install)
        if fonts:
            return "\n".join(fonts)
        else:
            return "[INFO] No fonts found (or mutool output format not recognized)."

def analyze_pdf(pdf_path: str, ensure=True, auto_install=True) -> Dict[str, Any]:
    """
    Analyze a PDF file and extract comprehensive metadata including PDF version,
    info object, pages count, and detailed font information.
    
    Args:
        pdf_path: Path to the PDF file
        ensure: Check for mutool availability before processing
        auto_install: Attempt to install MuPDF tools automatically
    
    Returns:
        Dictionary containing:
        - pdf_version: PDF version (e.g., "PDF-1.4")
        - info_object: Info object content
        - pages: Number of pages
        - fonts: List of font dictionaries with detailed information
        - font_count: Total number of fonts
        - font_names: List of font names
    """
    if ensure:
        ensure_mutool(auto_install=auto_install)

    # Run mutool info -F command
    cmd = ["mutool", "info", "-F", pdf_path]
    proc = _run(cmd)
    
    if proc.returncode != 0:
        # Fallback to basic info command
        cmd = ["mutool", "info", pdf_path]
        proc = _run(cmd)
        
        if proc.returncode != 0:
            raise RuntimeError(f"Failed to analyze PDF using mutool.\nError: {proc.stderr}")
    
    return _parse_mutool_output(proc.stdout)

def list_pdf_fonts(pdf_path: str, ensure=True, auto_install=True) -> List[str]:
    """
    Ensure mutool exists (optionally auto-install), run 'mutool info -F <pdf>',
    parse and return a de-duplicated list of font names.
    
    This function maintains backward compatibility while using the new parser.
    """
    analysis = analyze_pdf(pdf_path, ensure=ensure, auto_install=auto_install)
    return analysis['font_names']
