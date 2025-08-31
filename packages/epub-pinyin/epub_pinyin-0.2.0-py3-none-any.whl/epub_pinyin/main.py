"""Main entry point for the EPUB Pinyin Adder application."""

import argparse
import os
import sys
import tempfile
from typing import Optional
from enum import Enum

from . import epub_parser
from . import text_processor
try:
    from . import pdf_converter
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


class OutputFormat(Enum):
    """Output format options."""
    EPUB = "epub"
    PDF = "pdf"
    BOTH = "both"


def process_epub(input_path: str, output_path: Optional[str] = None, 
                output_format: OutputFormat = OutputFormat.EPUB, 
                add_pinyin: bool = True) -> None:
    """Process an EPUB file to add pinyin annotations and/or convert to PDF.
    
    Args:
        input_path: Path to the input EPUB file
        output_path: Path where the output will be saved (optional)
        output_format: Output format (epub, pdf, or both)
        add_pinyin: Whether to add pinyin annotations
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' does not exist")
        sys.exit(1)

    # Determine output paths based on format
    if not output_path:
        base, ext = os.path.splitext(input_path)
        if add_pinyin:
            output_base = f"{base}_annotated"
        else:
            output_base = f"{base}_converted"
        
        if output_format == OutputFormat.EPUB:
            output_path = f"{output_base}.epub"
        elif output_format == OutputFormat.PDF:
            output_path = f"{output_base}.pdf"
        else:  # BOTH
            epub_output = f"{output_base}.epub"
            pdf_output = f"{output_base}.pdf"
    else:
        if output_format == OutputFormat.BOTH:
            # For both format, use provided path as base
            base, _ = os.path.splitext(output_path)
            epub_output = f"{base}.epub"
            pdf_output = f"{base}.pdf"
        # else use output_path as-is

    # Create a temporary directory for extraction
    with tempfile.TemporaryDirectory() as extract_dir:
        try:
            # Initialize EPUB parser
            epub = epub_parser.EpubParser(extract_dir)

            print(f"Extracting {input_path}...")
            try:
                epub.extract_epub(input_path)
            except ValueError as e:
                print(f"Error: {str(e)}")
                sys.exit(1)

            print("Finding HTML files...")
            html_files = epub.get_html_files()

            html_files = epub.get_html_files()
            
            if not html_files:
                print("Warning: No HTML files found in EPUB")
            elif add_pinyin:
                print(f"Processing {len(html_files)} HTML files...")
                for html_file in html_files:
                    print(f"  Annotating {os.path.basename(html_file)}...")
                    text_processor.annotate_file_with_pinyin(html_file)

            # Generate outputs based on format
            if output_format in [OutputFormat.EPUB, OutputFormat.BOTH]:
                epub_path = epub_output if output_format == OutputFormat.BOTH else output_path
                print(f"Creating EPUB: {epub_path}")
                epub.package_epub(epub_path)
            
            if output_format in [OutputFormat.PDF, OutputFormat.BOTH]:
                if not PDF_AVAILABLE or (PDF_AVAILABLE and not pdf_converter.PdfConverter.is_available()):
                    print("Error: WeasyPrint is required for PDF conversion.")
                    print("Install it with: pip install epub-pinyin[pdf]")
                    if output_format == OutputFormat.PDF:
                        sys.exit(1)
                    else:
                        print("Skipping PDF generation...")
                else:
                    pdf_path = pdf_output if output_format == OutputFormat.BOTH else output_path
                    print(f"Converting to PDF: {pdf_path}")
                    converter = pdf_converter.PdfConverter(epub)
                    converter.convert_to_pdf(pdf_path)
            
            print("Done!")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)


def main() -> None:
    """Main entry point for command-line interface."""
    parser = argparse.ArgumentParser(
        description="Add pinyin annotations to Chinese text in EPUB files and/or convert to PDF"
    )
    parser.add_argument(
        "input_epub",
        help="Path to the input EPUB file"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file name (extension will be added based on format)",
        default=None
    )
    parser.add_argument(
        "-f", "--format",
        choices=["epub", "pdf", "both"],
        default="epub",
        help="Output format: epub (default), pdf, or both"
    )
    parser.add_argument(
        "--no-pinyin",
        action="store_true",
        help="Convert without adding pinyin annotations"
    )

    args = parser.parse_args()
    
    # Convert format string to enum
    format_map = {
        "epub": OutputFormat.EPUB,
        "pdf": OutputFormat.PDF,
        "both": OutputFormat.BOTH
    }
    output_format = format_map[args.format]
    
    # Determine if pinyin should be added
    add_pinyin = not args.no_pinyin
    
    process_epub(args.input_epub, args.output, output_format, add_pinyin)


if __name__ == "__main__":

    main()
