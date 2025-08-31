"""PDF utility functions."""

import pymupdf

# Maximum pages limit (optimized for processing time and memory)
MAX_PAGES_LIMIT = 100


def check_pdf_page_count(pdf_path: str, start: int = 0, end: int = 0) -> tuple[int, int, int]:
    """
    Check PDF page count and validate against limits.
    
    Args:
        pdf_path: Path to the PDF file
        start: Start page (1-based, 0 means first page)
        end: End page (1-based, 0 means last page)
    
    Returns:
        Tuple of (total_pages, actual_start, actual_end)
    
    Raises:
        SystemExit: If page count exceeds limit
    """
    doc = pymupdf.open(pdf_path)
    total_pages = len(doc)
    doc.close()
    
    # Set default values
    actual_start = 1 if start == 0 else start
    actual_end = total_pages if end == 0 else end
    
    # Calculate pages to process
    pages_to_process = actual_end - actual_start + 1
    
    if pages_to_process > MAX_PAGES_LIMIT:
        import sys
        print(f"\n{'='*60}")
        print(f"⚠️  Page Limit Exceeded")
        print(f"{'='*60}")
        print(f"\nDocument processing would exceed the {MAX_PAGES_LIMIT} page limit.")
        print(f"  • Total pages in PDF: {total_pages}")
        print(f"  • Requested range: pages {actual_start} to {actual_end} ({pages_to_process} pages)")
        print(f"  • Maximum allowed: {MAX_PAGES_LIMIT} pages per run")
        
        print(f"\n📋 Suggested Processing Sections:")
        print(f"{'─'*40}")
        
        # Generate optimal suggestions for processing the document
        suggestions = []
        remaining_pages = total_pages
        section_start = 1
        section_num = 1
        
        while remaining_pages > 0 and len(suggestions) < 5:  # Show up to 5 suggestions
            section_end = min(section_start + MAX_PAGES_LIMIT - 1, total_pages)
            pages_in_section = section_end - section_start + 1
            suggestions.append({
                'num': section_num,
                'start': section_start,
                'end': section_end,
                'pages': pages_in_section
            })
            section_start = section_end + 1
            remaining_pages -= pages_in_section
            section_num += 1
        
        for s in suggestions:
            print(f"  Section {s['num']}: Pages {s['start']:3d} - {s['end']:3d} ({s['pages']:3d} pages)")
            print(f"    netintel-ocr document.pdf --start {s['start']} --end {s['end']}")
            print()
        
        if remaining_pages > 0:
            print(f"  ... and {remaining_pages} more pages in additional sections")
        
        print(f"{'─'*40}")
        print(f"\n💡 Tip: Process each section sequentially, then combine the outputs.")
        print(f"{'='*60}\n")
        
        sys.exit(1)
    
    return total_pages, actual_start, actual_end