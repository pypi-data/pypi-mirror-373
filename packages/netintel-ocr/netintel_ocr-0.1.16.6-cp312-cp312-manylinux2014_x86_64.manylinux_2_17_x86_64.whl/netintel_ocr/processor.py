import sys
from pathlib import Path
from tqdm import tqdm

from .pdf import pdf_to_images
from .pdf_utils import check_pdf_page_count
from .ollama import transcribe_image, check_for_server
from .utils import setup_output_dirs, merge_markdown_files, resize_image


def process_pdf(
    pdf_path: str,
    output_dir: str,
    model: str,
    keep_images: bool,
    width: int,
    start: int,
    end: int,
) -> None:
    """
    Process a PDF file, converting pages to images and transcribing them.

    Args:
        pdf_path (str): The path to the PDF file.
        output_dir (str): The directory to save the output.
        model (str): The model to use for transcription.
        keep_images (bool): Whether to keep the images after processing.
        width (int): The width of the resized images.
        start (int): The start page number.
        end (int): The end page number.
    """
    pdf_path = Path(pdf_path)
    output_base = Path(output_dir)

    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    # Check page count before processing
    total_pages, actual_start, actual_end = check_pdf_page_count(str(pdf_path), start, end)
    pages_to_process = actual_end - actual_start + 1
    
    # Estimate processing time (30-60 seconds per page)
    min_time = pages_to_process * 30
    max_time = pages_to_process * 60
    min_minutes = min_time // 60
    min_seconds = min_time % 60
    max_minutes = max_time // 60
    max_seconds = max_time % 60
    
    print(f"\n{'='*60}")
    print(f"📄 PDF Processing Information")
    print(f"{'='*60}")
    print(f"  Document: {pdf_path.name}")
    print(f"  Total pages in PDF: {total_pages}")
    print(f"  Pages to process: {actual_start} to {actual_end} ({pages_to_process} pages)")
    print(f"  Model: {model}")
    print(f"  Estimated time: {min_minutes}:{min_seconds:02d} - {max_minutes}:{max_seconds:02d} (30-60 sec/page)")
    print(f"{'='*60}\n")

    if not check_for_server():
        import os
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        print(
            f"Error: Cannot connect to Ollama server at {host}.\n"
            "Please ensure:\n"
            "1. Ollama server is running\n"
            "2. The OLLAMA_HOST environment variable is set correctly if using a remote server\n"
            "3. The server is accessible from this machine"
        )
        sys.exit(1)

    # Setup output directories
    image_dir, markdown_dir = setup_output_dirs(output_base)

    try:
        # Convert PDF to images
        pdf_to_images(str(pdf_path), image_dir, start, end)

        # Process each page
        image_files = sorted(image_dir.glob("page_*.png"))
        total_pages = len(image_files)

        # Resize images to 500px width
        if width > 0:
            for image_file in tqdm(image_files, desc="Resizing images"):
                resize_image(str(image_file), str(image_file), width)
        else:
            pass  # Skip resizing

        for i, image_file in tqdm(
            enumerate(image_files, 1),
            desc="Transcribing pages",
            total=total_pages,
        ):
            # Transcribe the image
            try:
                text = transcribe_image(str(image_file), model=model)

                # Save transcription as markdown
                page_number = int(image_file.stem.split("_")[1])
                markdown_file = markdown_dir / f"page_{page_number:03d}.md"
                with open(markdown_file, "w", encoding="utf-8") as f:
                    f.write(f"# Page {page_number}\n\n")
                    f.write(text)
            except Exception as e:
                print(f"Error processing page {i}: {str(e)}")

            # Clean up image if not keeping them
            if not keep_images:
                image_file.unlink()

        # Merge markdown files with PDF filename
        merged_file = merge_markdown_files(markdown_dir, pdf_path.name)

        print(f"Processing complete! Output saved to: {output_base}")
        print(f"Merged document: {merged_file}")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
