"""Network diagram processing integration."""

import sys
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

from .pdf import pdf_to_images
from .pdf_utils import check_pdf_page_count
from .ollama import check_for_server, transcribe_image
from .utils import setup_output_dirs, resize_image, merge_markdown_files
from .network_diagram import (
    NetworkDiagramDetector,
    ComponentExtractor,
    MermaidGenerator,
    MermaidValidator
)


def process_pdf_network_diagrams(
    pdf_path: str,
    output_dir: str,
    model: str,
    keep_images: bool,
    width: int,
    start: int,
    end: int,
    confidence_threshold: float = 0.7,
    use_icons: bool = False,
) -> None:
    """
    Process a PDF file, detecting network diagrams and converting them to Mermaid format.
    All output is saved as markdown files in a unified markdown directory.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save the output
        model: The model to use for processing
        keep_images: Whether to keep the images after processing
        width: Width to resize images to
        start: Start page number
        end: End page number
        confidence_threshold: Minimum confidence for network diagram detection
        use_icons: Whether to use icons in Mermaid diagrams
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
    print(f"📄 PDF Processing Information (Network Mode)")
    print(f"{'='*60}")
    print(f"  Document: {pdf_path.name}")
    print(f"  Total pages in PDF: {total_pages}")
    print(f"  Pages to process: {actual_start} to {actual_end} ({pages_to_process} pages)")
    print(f"  Model: {model}")
    print(f"  Network detection: Enabled (threshold: {confidence_threshold})")
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
    
    # Initialize processors
    detector = NetworkDiagramDetector(model=model)
    extractor = ComponentExtractor(model=model)
    generator = MermaidGenerator(model=model, use_icons=use_icons)
    validator = MermaidValidator()
    
    try:
        # Convert PDF to images
        print("Converting PDF to images...")
        pdf_to_images(str(pdf_path), image_dir, start, end)
        
        # Process each page
        image_files = sorted(image_dir.glob("page_*.png"))
        total_pages = len(image_files)
        
        # Resize images if requested
        if width > 0:
            for image_file in tqdm(image_files, desc="Resizing images"):
                resize_image(str(image_file), str(image_file), width)
        
        # Track statistics
        network_diagrams_found = 0
        regular_pages = 0
        
        # Process each image
        for image_file in tqdm(image_files, desc="Processing pages", total=total_pages):
            try:
                # Extract page number
                page_number = int(image_file.stem.split("_")[1])
                markdown_file = markdown_dir / f"page_{page_number:03d}.md"
                
                # Debug: Print file path being written
                # print(f"    Writing to: {markdown_file}")
                
                # Detect if it's a network diagram
                detection = detector.detect(str(image_file))
                
                if detection.get("is_network_diagram") and detection.get("confidence", 0) >= confidence_threshold:
                    network_diagrams_found += 1
                    print(f"\n  Page {page_number}: Network diagram detected (confidence: {detection.get('confidence', 0):.2f})")
                    print(f"    Type: {detection.get('diagram_type', 'unknown')}")
                    
                    # Extract components
                    extraction = extractor.extract(str(image_file))
                    
                    if extraction.get("extraction_successful"):
                        print(f"    Components: {len(extraction.get('components', []))}")
                        print(f"    Connections: {len(extraction.get('connections', []))}")
                        
                        # Generate Mermaid diagram
                        mermaid_code = generator.generate(extraction, use_llm=True)
                        
                        # Validate the generated Mermaid code
                        validation = validator.validate(mermaid_code)
                        
                        if not validation["valid"] and validation["errors"]:
                            print(f"    Warning: Mermaid validation issues found")
                            # Try to fix common issues
                            mermaid_code = validator.fix_common_issues(mermaid_code)
                            validation = validator.validate(mermaid_code)
                        
                        # Add timestamp and confidence to mermaid code
                        timestamp = datetime.now().isoformat()
                        mermaid_lines = mermaid_code.split('\n')
                        if mermaid_lines and mermaid_lines[0].startswith('graph'):
                            mermaid_lines.insert(1, f"    %% Network Diagram: Page {page_number}")
                            mermaid_lines.insert(2, f"    %% Generated: {timestamp}")
                            mermaid_lines.insert(3, f"    %% Confidence: {detection.get('confidence', 0):.2f}")
                            mermaid_code = '\n'.join(mermaid_lines)
                        
                        # Save as unified markdown with embedded Mermaid
                        try:
                            markdown_file.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
                        except Exception as e:
                            print(f"    Error creating directory {markdown_file.parent}: {e}")
                            raise
                        
                        try:
                            with open(markdown_file, "w", encoding="utf-8") as f:
                                f.write(f"# Page {page_number} - Network Diagram\n\n")
                                f.write(f"**Type**: {detection.get('diagram_type', 'unknown')}  \n")
                                f.write(f"**Detection Confidence**: {detection.get('confidence', 0):.2f}  \n")
                                f.write(f"**Components**: {len(extraction.get('components', []))} detected  \n")
                                f.write(f"**Connections**: {len(extraction.get('connections', []))} detected  \n\n")
                                
                                f.write("## Diagram\n\n")
                                f.write("```mermaid\n")
                                f.write(mermaid_code)
                                f.write("\n```\n\n")
                                
                                # Add component details if significant
                                if len(extraction.get('components', [])) > 0:
                                    f.write("## Components Detail\n\n")
                                    for comp in extraction.get('components', []):
                                        comp_info = f"- **{comp.get('label', comp.get('id'))}** ({comp.get('type', 'unknown')})"
                                        if comp.get('ip_info'):
                                            comp_info += f" - IP: {comp['ip_info']}"
                                        f.write(comp_info + "\n")
                                    f.write("\n")
                                
                                # Add validation warnings if any
                                if validation["warnings"]:
                                    f.write("## Notes\n\n")
                                    for warning in validation["warnings"]:
                                        f.write(f"- {warning}\n")
                                    f.write("\n")
                        except Exception as e:
                            print(f"    Error writing to file {markdown_file}: {e}")
                            raise
                    else:
                        # Failed to extract components, fall back to regular transcription
                        print(f"    Failed to extract components: {extraction.get('error', 'Unknown error')}")
                        print(f"    Falling back to regular text transcription...")
                        
                        text = transcribe_image(str(image_file), model=model)
                        try:
                            markdown_file.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
                            with open(markdown_file, "w", encoding="utf-8") as f:
                                f.write(f"# Page {page_number}\n\n")
                                f.write(f"*Note: Network diagram detected but extraction failed. Using text transcription.*\n\n")
                                f.write(text)
                        except Exception as e:
                            print(f"    Error writing fallback file {markdown_file}: {e}")
                            raise
                        regular_pages += 1
                else:
                    # Regular page - transcribe as text
                    regular_pages += 1
                    text = transcribe_image(str(image_file), model=model)
                    
                    try:
                        markdown_file.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
                        with open(markdown_file, "w", encoding="utf-8") as f:
                            f.write(f"# Page {page_number}\n\n")
                            f.write(text)
                    except Exception as e:
                        print(f"    Error writing regular page file {markdown_file}: {e}")
                        raise
                
            except Exception as e:
                print(f"  Error processing page {page_number}: {str(e)}")
                # Create error page
                try:
                    page_num = image_file.stem.split("_")[1] if hasattr(e, '__context__') else "unknown"
                    markdown_file = markdown_dir / f"page_{page_num:03d}.md" if page_num != "unknown" else markdown_dir / "page_error.md"
                except:
                    markdown_file = markdown_dir / "page_error.md"
                
                try:
                    markdown_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(markdown_file, "w", encoding="utf-8") as f:
                        f.write(f"# Page {page_number}\n\n")
                        f.write(f"*Error processing this page: {str(e)}*\n")
                except Exception as write_error:
                    print(f"    Failed to write error page: {write_error}")
                regular_pages += 1
            
            # Clean up image if not keeping them
            if not keep_images:
                image_file.unlink()
        
        # Merge markdown files with PDF filename
        merged_file = merge_markdown_files(markdown_dir, pdf_path.name)
        
        # Generate summary report
        summary_file = output_base / "summary.md"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write("# Processing Summary\n\n")
            f.write(f"**Document**: {pdf_path.name}\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Statistics\n\n")
            f.write(f"- **Total Pages**: {total_pages}\n")
            f.write(f"- **Network Diagrams Found**: {network_diagrams_found}\n")
            f.write(f"- **Regular Pages**: {regular_pages}\n")
            f.write(f"- **Model Used**: {model}\n")
            f.write(f"- **Confidence Threshold**: {confidence_threshold}\n")
            f.write(f"- **Icons Enabled**: {use_icons}\n\n")
            
            f.write("## Output Files\n\n")
            f.write(f"- [Merged Document](markdown/{merged_file.name}) - Complete document with all pages\n")
            f.write(f"- Individual pages in `markdown/` directory\n")
            
            if network_diagrams_found > 0:
                f.write("\n## Network Diagrams\n\n")
                f.write("The following pages contain network diagrams:\n\n")
                for md_file in sorted(markdown_dir.glob("page_*.md")):
                    with open(md_file, 'r') as md_f:  # Use different variable name
                        first_line = md_f.readline().strip()
                        if "Network Diagram" in first_line:
                            page_num = md_file.stem.replace("page_", "").lstrip("0")
                            f.write(f"- [Page {page_num}](markdown/{md_file.name})\n")  # Now writes to summary file
        
        print(f"\nProcessing complete!")
        print(f"  Network diagrams found: {network_diagrams_found}")
        print(f"  Regular pages: {regular_pages}")
        print(f"  Output saved to: {output_base}")
        print(f"  Merged document: {merged_file}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)