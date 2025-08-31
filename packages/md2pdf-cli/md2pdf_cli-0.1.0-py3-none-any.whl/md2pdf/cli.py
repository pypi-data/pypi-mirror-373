#!/usr/bin/env python3
import argparse
import markdown2
import pdfkit
from pathlib import Path

def convert_markdown_to_pdf(input_file, output_file, css_file=None):
    """Convert Markdown file to PDF with optional CSS styling"""
    try:
        # Read markdown content
        with open(input_file, 'r', encoding='utf-8') as f:
            markdown_text = f.read()
        
        # Convert to HTML
        html_content = markdown2.markdown(
            markdown_text,
            extras=['fenced-code-blocks', 'tables', 'header-ids']
        )
        
        # Create complete HTML document
        html_document = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{Path(input_file).stem}</title>
            {f'<link rel="stylesheet" href="{css_file}">' if css_file else ''}
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Convert to PDF using pdfkit
        options = {
            'encoding': 'UTF-8',
            'quiet': ''
        }
        pdfkit.from_string(html_document, output_file, options=options)
        
        print(f"Successfully converted {input_file} to {output_file}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        exit(1)
    except Exception as e:
        print(f"Conversion failed: {e}")
        exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Convert Markdown files to PDF",
        epilog="Example: md2pdf input.md output.pdf --style style.css"
    )
    
    parser.add_argument(
        "input",
        help="Input Markdown file"
    )
    
    parser.add_argument(
        "output",
        help="Output PDF file"
    )
    
    parser.add_argument(
        "--style", "-s",
        help="Optional CSS file for styling"
    )
    
    args = parser.parse_args()
    
    convert_markdown_to_pdf(args.input, args.output, args.style)

if __name__ == "__main__":
    main()