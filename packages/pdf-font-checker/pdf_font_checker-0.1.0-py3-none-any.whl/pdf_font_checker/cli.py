\
import argparse
from .core import list_pdf_fonts, ensure_mutool

def main():
    parser = argparse.ArgumentParser(description="List font names used in a PDF via MuPDF (mutool).")
    parser.add_argument("pdf", help="Path to PDF file")
    parser.add_argument("--no-auto-install", action="store_true",
                        help="Do not attempt to auto-install mupdf-tools")
    args = parser.parse_args()

    try:
        fonts = list_pdf_fonts(args.pdf, ensure=True, auto_install=not args.no_auto_install)
    except Exception as e:
        print(f"[ERROR] {e}")
        raise SystemExit(1)

    if fonts:
        print("\n".join(fonts))
    else:
        print("[INFO] No fonts found (or mutool output format not recognized).")
