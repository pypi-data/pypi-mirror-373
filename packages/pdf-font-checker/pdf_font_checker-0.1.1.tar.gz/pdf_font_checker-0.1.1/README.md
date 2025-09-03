# PDF Font Checker

A lightweight Python utility that extracts and lists all fonts used in PDF documents using MuPDF's `mutool` command-line tool.

## Features

### Key Features Tested:
- [x] Font extraction from PDF files
- [x] Multiple mutool output format parsing
- [x] Automatic MuPDF installation
- [x] Command-line interface
- [x] Python API
- [x] Error handling
- [x] Cross-platform compatibility
- [x] Package building and distribution

## Installation

### From PyPI (recommended)

```bash
pip install pdf-font-checker
```

### From Source

```bash
git clone https://github.com/genie360s/pdf-font-checker.git
cd pdf-font-checker
pip install -e .
```

## Dependencies

This package requires MuPDF's `mutool` command-line tool. The package will attempt to automatically install it using your system's package manager:

- **macOS**: via Homebrew (`brew install mupdf-tools`)
- **Linux**: via apt, dnf, yum, pacman, or zypper (`mupdf-tools` or `mupdf`)

**Note**: This package currently supports Linux and macOS only. Windows support is not available at this time.

If automatic installation fails, you can install MuPDF manually:

### Manual Installation

#### macOS
```bash
brew install mupdf-tools
```

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install mupdf-tools
```

#### Fedora/CentOS/RHEL
```bash
sudo dnf install mupdf-tools
# or on older systems:
sudo yum install mupdf-tools
```

#### Arch Linux
```bash
sudo pacman -S mupdf-tools
```

## Platform Support

This package is designed to work on:
- [x] **Linux** (all major distributions)
- [x] **macOS** (Intel and Apple Silicon)
- [ ] **Windows** (not supported)

## Usage

### Quick Reference

| Command | Output Format | Description |
|---------|---------------|-------------|
| `pdf-font-checker file.pdf` | Text list | Font names only |
| `pdf-font-checker file.pdf --detailed` | Formatted text | Full PDF analysis |
| `pdf-font-checker file.pdf --dict` | Python dict | Structured data |
| `pdf-font-checker file.pdf --dict --json` | JSON | Structured JSON |

| Python Function | Return Type | Description |
|-----------------|-------------|-------------|
| `get_pdf_info_dict()` | `dict` | **Recommended** - Structured data |
| `get_pdf_terminal_output()` | `str` | Terminal-style formatted output |
| `list_pdf_fonts()` | `list` | Font names only |
| `analyze_pdf()` | `dict` | Complete analysis with all metadata |

### Command Line Interface

#### Basic Usage - Font Names Only
Extract just the font names from a PDF file:

```bash
pdf-font-checker document.pdf
```

Output:
```
Helvetica
AZHGJL+ArialMT
```

#### Detailed Analysis
Get comprehensive PDF metadata including version, pages, and detailed font information:

```bash
pdf-font-checker document.pdf --detailed
```

Output:
```
PDF Version: PDF-1.4
Pages: 2
Info Object (20 0 R): <</ModDate(D:20250207153904+03'00')/Creator(JasperReports Library version 6.6.0)/CreationDate(D:20250207153904+03'00')/Producer(iText 2.1.7 by 1T3XT)>>

Fonts (2):
    1   (2 0 R):        Type1 'Helvetica' WinAnsiEncoding (3 0 R)
    1   (2 0 R):        Type0 'AZHGJL+ArialMT' Identity-H (4 0 R)
```

#### Dictionary Format
Get structured data in dictionary format:

```bash
pdf-font-checker document.pdf --dict
```

Output:
```python
{'pdf_version': 'PDF-1.4', 'total_no_of_fonts': 2, 'font_names': ['Helvetica', 'AZHGJL+ArialMT'], 'info_object': '20 0 R'}
```

#### JSON Output
Get any output in JSON format:

```bash
pdf-font-checker document.pdf --dict --json
```

Output:
```json
{
  "pdf_version": "PDF-1.4",
  "total_no_of_fonts": 2,
  "font_names": [
    "Helvetica",
    "AZHGJL+ArialMT"
  ],
  "info_object": "20 0 R"
}
```

#### Disable Automatic Installation
Disable automatic MuPDF installation:

```bash
pdf-font-checker --no-auto-install document.pdf
```

### Python API

#### 1. Dictionary Format (Recommended)
Get structured PDF information in a simple dictionary format:

```python
from pdf_font_checker import get_pdf_info_dict

# Get structured PDF info
result = get_pdf_info_dict("document.pdf")
print(result)
# Output: {'pdf_version': 'PDF-1.4', 'total_no_of_fonts': 2, 'font_names': ['Helvetica', 'AZHGJL+ArialMT'], 'info_object': '20 0 R'}

# Access individual fields
print(f"PDF Version: {result['pdf_version']}")
print(f"Number of fonts: {result['total_no_of_fonts']}")
print(f"Font names: {result['font_names']}")
print(f"Info object: {result['info_object']}")
```

#### 2. Terminal-Style Output
Get the exact same output as the command line:

```python
from pdf_font_checker import get_pdf_terminal_output

# Detailed output (same as --detailed)
detailed_output = get_pdf_terminal_output("document.pdf", detailed=True)
print(detailed_output)

# Simple output (just font names)
simple_output = get_pdf_terminal_output("document.pdf", detailed=False)
print(simple_output)
```

#### 3. Font Names Only (Legacy)
Get just the list of font names:

```python
from pdf_font_checker import list_pdf_fonts

fonts = list_pdf_fonts("document.pdf")
print("Fonts found:")
for font in fonts:
    print(f"  - {font}")
```

#### 4. Complete Analysis
Get full detailed analysis with all metadata:

```python
from pdf_font_checker import analyze_pdf

analysis = analyze_pdf("document.pdf")
print(f"PDF Version: {analysis['pdf_version']}")
print(f"Pages: {analysis['pages']}")
print(f"Font count: {analysis['font_count']}")

# Detailed font information
for font in analysis['fonts']:
    print(f"Font: {font['name']} (Type: {font['type']}, Page: {font['page']})")
```

#### 5. JSON Output in Python
Convert any result to JSON:

```python
import json
from pdf_font_checker import get_pdf_info_dict

result = get_pdf_info_dict("document.pdf")
json_output = json.dumps(result, indent=2)
print(json_output)
```

### Advanced Usage

#### Process Multiple PDF Files
```python
from pdf_font_checker import get_pdf_info_dict, ensure_mutool
import json

# Ensure mutool is available before processing multiple files
ensure_mutool()

pdf_files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
results = []

for pdf_file in pdf_files:
    try:
        info = get_pdf_info_dict(pdf_file, ensure=False)  # Skip check after first
        info['filename'] = pdf_file
        results.append(info)
        print(f"[x] Processed {pdf_file}: {info['total_no_of_fonts']} fonts")
    except Exception as e:
        print(f"[ ] Error processing {pdf_file}: {e}")

# Save results to JSON file
with open('pdf_analysis_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nProcessed {len(results)} files successfully")
```

#### Extract Unique Fonts Across Multiple PDFs
```python
from pdf_font_checker import get_pdf_info_dict

pdf_files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
all_fonts = set()
pdf_versions = set()

for pdf_file in pdf_files:
    try:
        info = get_pdf_info_dict(pdf_file)
        all_fonts.update(info['font_names'])
        pdf_versions.add(info['pdf_version'])
        print(f"{pdf_file}: {info['total_no_of_fonts']} fonts")
    except Exception as e:
        print(f"Error processing {pdf_file}: {e}")

print(f"\nSummary:")
print(f"Total unique fonts: {len(all_fonts)}")
print(f"PDF versions found: {sorted(pdf_versions)}")
print(f"Font list: {sorted(all_fonts)}")
```

#### Error Handling
```python
from pdf_font_checker import get_pdf_info_dict

try:
    result = get_pdf_info_dict("document.pdf")
    if result['total_no_of_fonts'] == 0:
        print("No fonts found in PDF")
    else:
        print(f"Found {result['total_no_of_fonts']} fonts")
except FileNotFoundError:
    print("PDF file not found")
except RuntimeError as e:
    print(f"PDF processing error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Output Example

```bash
$ pdf-font-checker sample.pdf
Arial-Bold
Helvetica
TimesNewRomanPSMT
Calibri-Light
Verdana-Italic
```

## Data API Ready Reference

### `get_pdf_info_dict(pdf_path, ensure=True, auto_install=True)`

**[RECOMMENDED]** Extract PDF information in a structured dictionary format.

**Parameters:**
- `pdf_path` (str): Path to the PDF file
- `ensure` (bool, default=True): Check for mutool availability before processing
- `auto_install` (bool, default=True): Attempt to install MuPDF tools automatically

**Returns:**
- `Dict[str, Any]`: Dictionary containing:
  - `pdf_version`: PDF version (e.g., "PDF-1.4")
  - `total_no_of_fonts`: Number of fonts
  - `font_names`: List of font names
  - `info_object`: Info object reference

**Example:**
```python
result = get_pdf_info_dict("document.pdf")
# {'pdf_version': 'PDF-1.4', 'total_no_of_fonts': 2, 'font_names': ['Helvetica', 'Arial'], 'info_object': '20 0 R'}
```

### `get_pdf_terminal_output(pdf_path, detailed=True, ensure=True, auto_install=True)`

Get PDF analysis output formatted exactly like the terminal command.

**Parameters:**
- `pdf_path` (str): Path to the PDF file
- `detailed` (bool, default=True): If True, return detailed output; if False, return just font names
- `ensure` (bool, default=True): Check for mutool availability before processing
- `auto_install` (bool, default=True): Attempt to install MuPDF tools automatically

**Returns:**
- `str`: Formatted output exactly like terminal command

### `analyze_pdf(pdf_path, ensure=True, auto_install=True)`

Extract comprehensive PDF metadata and font information.

**Parameters:**
- `pdf_path` (str): Path to the PDF file
- `ensure` (bool, default=True): Check for mutool availability before processing
- `auto_install` (bool, default=True): Attempt to install MuPDF tools automatically

**Returns:**
- `Dict[str, Any]`: Comprehensive analysis containing:
  - `pdf_version`: PDF version
  - `info_object`: Info object data with reference and content
  - `pages`: Number of pages
  - `fonts`: List of detailed font dictionaries
  - `font_count`: Total number of fonts
  - `font_names`: List of font names

### `list_pdf_fonts(pdf_path, ensure=True, auto_install=True)`

Extract font names from a PDF file (legacy function for backward compatibility).

**Parameters:**
- `pdf_path` (str): Path to the PDF file
- `ensure` (bool, default=True): Check for mutool availability before processing
- `auto_install` (bool, default=True): Attempt to install MuPDF tools automatically

**Returns:**
- `List[str]`: List of unique font names found in the PDF

### `ensure_mutool(auto_install=True)`

Ensure MuPDF's mutool is available on the system.

**Parameters:**
- `auto_install` (bool, default=True): Attempt automatic installation if mutool is missing

**Raises:**
- `RuntimeError`: If mutool cannot be found or installed

## Development

### Setting up Development Environment

```bash
git clone https://github.com/genie360s/pdf-font-checker.git
cd pdf-font-checker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest pytest-cov black flake8
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=pdf_font_checker

# Run specific test file
python -m pytest tests/test_core.py

# Run specific test
python -m pytest tests/test_core.py::TestPdfFontChecker::test_parse_mutool_fonts_various_formats
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking (if mypy is installed)
mypy src/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass (`python -m pytest`)
6. Format your code (`black .`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## Troubleshooting

### Common Issues

**Q: "mutool not found" error**
A: Install MuPDF tools using your system package manager. See the Dependencies section above.

**Q: "Permission denied" when auto-installing**
A: The automatic installation requires admin privileges on some systems. Install MuPDF manually or run with sudo (Linux) or as Administrator (Windows).

**Q: No fonts detected in PDF**
A: Some PDFs may use embedded fonts in formats that mutool doesn't recognize, or the PDF might use images instead of text.

**Q: Does this work on Windows?**
A: No, this package currently only supports Linux and macOS. Windows support may be added in future versions.

### Getting Help

- [x] [Documentation](https://github.com/genie360s/pdf-font-checker)
- [x] [Issue Tracker](https://github.com/genie360s/pdf-font-checker/issues)
- [x] [Discussions](https://github.com/genie360s/pdf-font-checker/discussions)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on top of [MuPDF](https://mupdf.com/) - a lightweight PDF toolkit
- Inspired by the need for simple font analysis in PDF workflows


