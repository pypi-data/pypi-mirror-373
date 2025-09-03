\
import argparse
import json
from .core import list_pdf_fonts, analyze_pdf, ensure_mutool

def main():
    parser = argparse.ArgumentParser(description="Analyze PDF files and list font information via MuPDF (mutool).")
    parser.add_argument("pdf", help="Path to PDF file")
    parser.add_argument("--no-auto-install", action="store_true",
                        help="Do not attempt to auto-install mupdf-tools")
    parser.add_argument("--detailed", "-d", action="store_true",
                        help="Show detailed PDF analysis including metadata")
    parser.add_argument("--json", action="store_true",
                        help="Output results in JSON format")
    parser.add_argument("--dict", action="store_true",
                        help="Output results in dictionary format with specific fields")
    args = parser.parse_args()

    try:
        if args.dict or args.detailed:
            # Use the new comprehensive analysis
            analysis = analyze_pdf(args.pdf, ensure=True, auto_install=not args.no_auto_install)
            
            if args.dict:
                # Extract info_object reference number only
                info_object_ref = None
                if analysis['info_object'] and analysis['info_object']['reference']:
                    info_object_ref = analysis['info_object']['reference']
                
                # Create the requested dictionary format
                result_dict = {
                    "pdf_version": analysis['pdf_version'],
                    "total_no_of_fonts": analysis['font_count'],
                    "font_names": analysis['font_names'],
                    "info_object": info_object_ref
                }
                
                if args.json:
                    print(json.dumps(result_dict, indent=2))
                else:
                    print(result_dict)
            
            elif args.json:
                print(json.dumps(analysis, indent=2))
            else:
                print(f"PDF Version: {analysis['pdf_version'] or 'Unknown'}")
                print(f"Pages: {analysis['pages'] or 'Unknown'}")
                
                if analysis['info_object']:
                    print(f"Info Object ({analysis['info_object']['reference']}): {analysis['info_object']['content']}")
                
                print(f"\nFonts ({analysis['font_count']}):")
                if analysis['fonts']:
                    for font in analysis['fonts']:
                        encoding_info = f" {font['encoding']}"
                        if font['encoding_reference']:
                            encoding_info += f" ({font['encoding_reference']})"
                        print(f"    {font['page']}\t({font['object_reference']}):\t{font['type']} '{font['name']}'{encoding_info}")
                else:
                    print("    No fonts found or format not recognized.")
        else:
            # Use the legacy font names only
            fonts = list_pdf_fonts(args.pdf, ensure=True, auto_install=not args.no_auto_install)
            
            if args.json:
                print(json.dumps({"fonts": fonts}))
            else:
                if fonts:
                    print("\n".join(fonts))
                else:
                    print("[INFO] No fonts found (or mutool output format not recognized).")
                    
    except Exception as e:
        if args.json or args.dict:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"[ERROR] {e}")
        raise SystemExit(1)
