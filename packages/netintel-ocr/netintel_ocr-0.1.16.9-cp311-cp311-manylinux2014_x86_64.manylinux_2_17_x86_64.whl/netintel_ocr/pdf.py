import io
import sys
import pymupdf
from PIL import Image
from pathlib import Path
from tqdm import tqdm

# Maximum pages limit (optimized for processing time and memory)
MAX_PAGES_LIMIT = 100


def pdf_to_images(
    pdf_path: str, output_dir: Path, start: int = 0, end: int = 0
) -> None:
    """
    Convert PDF pages to images and save them to the specified output directory.

    Args:
        pdf_path (str): Path to the input PDF file
        output_dir (Path): Directory where the images will be saved
        start (int): The start page number (1-based). If 0, starts from first page.
        end (int): The end page number (1-based). If 0, goes until last page.
    """
    doc = pymupdf.open(pdf_path)
    total_pages = len(doc)

    # Validate page numbers
    if start < 0 or (start > total_pages and start != 0):
        raise ValueError(
            f"Start page number {start} is out of range. Document has {total_pages} pages."
        )
    if end < 0 or (end > total_pages and end != 0):
        raise ValueError(
            f"End page number {end} is out of range. Document has {total_pages} pages."
        )

    # Set default values for start and end
    start = 1 if start == 0 else start
    end = total_pages if end == 0 else end
    
    # Check page limit
    pages_to_process = end - start + 1
    if pages_to_process > MAX_PAGES_LIMIT:
        print(f"\nError: Document has {pages_to_process} pages to process, which exceeds the {MAX_PAGES_LIMIT} page limit.")
        print(f"Total pages in PDF: {total_pages}")
        print(f"Requested range: pages {start} to {end} ({pages_to_process} pages)")
        print(f"\nSuggestions:")
        print(f"  1. Use --start and --end flags to process a specific section (max {MAX_PAGES_LIMIT} pages)")
        print(f"  2. Example: --start 1 --end {MAX_PAGES_LIMIT}")
        print(f"  3. Example: --start 101 --end 200")
        sys.exit(1)

    # Convert specified pages
    for page_num in tqdm(
        range(start, end + 1),
        desc="Converting pages to images",
        total=end - start + 1,
    ):
        page = doc[page_num - 1]  # Convert to 0-based index
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        output_path = output_dir / f"page_{page_num}.png"
        img.save(str(output_path))
