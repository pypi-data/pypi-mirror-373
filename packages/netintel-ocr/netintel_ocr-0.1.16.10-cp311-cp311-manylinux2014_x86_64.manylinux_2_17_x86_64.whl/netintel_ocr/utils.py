from pathlib import Path
from PIL import Image
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
import os


def setup_output_dirs(output_base: Path) -> tuple[Path, Path]:
    """
    Create and return paths for image and markdown output directories.

    Args:
        output_base (Path): The base directory for output.
    """
    image_dir = output_base / "images"
    markdown_dir = output_base / "markdown"

    image_dir.mkdir(parents=True, exist_ok=True)
    markdown_dir.mkdir(parents=True, exist_ok=True)

    return image_dir, markdown_dir


def resize_image(image_path: str, output_path: str, width: int) -> None:
    """
    Resize an image to the specified width while maintaining aspect ratio.

    Args:
        image_path (str): Path to the input image file
        output_path (str): Path where the resized image will be saved
        width (int): Desired width of the image
    """
    if width == 0:
        return
    else:
        img = Image.open(image_path)
        w_percent = width / float(img.size[0])
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((width, h_size), Image.Resampling.LANCZOS)
        img.save(output_path)


def calculate_file_checksum(file_path: str, algorithm: str = 'md5') -> str:
    """
    Calculate the checksum of a file.
    
    Args:
        file_path (str): Path to the file
        algorithm (str): Hash algorithm to use (default: md5)
    
    Returns:
        str: Hexadecimal checksum string
    """
    hash_func = hashlib.new(algorithm)
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        return f"Error calculating checksum: {str(e)}"


def merge_markdown_files(markdown_dir: Path, pdf_filename: str = None) -> Path:
    """
    Merge all individual markdown files into a single merged file.

    Args:
        markdown_dir (Path): Directory containing individual markdown files.
        pdf_filename (str): Optional original PDF filename to use for merged file.

    Returns:
        Path: Path to the created merged file.
    """
    markdown_files = sorted(markdown_dir.glob("page_*.md"))
    
    # Determine the merged filename
    if pdf_filename:
        # Remove .pdf extension if present and add .md
        base_name = Path(pdf_filename).stem
        merged_filename = f"{base_name}.md"
    else:
        merged_filename = "merged.md"
    
    merged_file = markdown_dir / merged_filename

    if markdown_files:
        with open(merged_file, "w", encoding="utf-8") as merged_f:
            merged_f.write("# Merged Document\n\n")
            merged_f.write(f"*Generated from {len(markdown_files)} pages*\n\n")
            merged_f.write("---\n\n")
            
            for i, md_file in enumerate(markdown_files, 1):
                with open(md_file, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read().strip()
                    if content:  # Only add non-empty content
                        merged_f.write(content)
                        merged_f.write("\n\n")
                        if i < len(markdown_files):  # Add separator between pages
                            merged_f.write("---\n\n")

    return merged_file


def merge_markdown_files_with_metrics(
    markdown_dir: Path, 
    pdf_filename: str = None,
    pdf_path: str = None,
    metrics: Dict = None
) -> Path:
    """
    Merge all individual markdown files into a single merged file with footer metrics.

    Args:
        markdown_dir (Path): Directory containing individual markdown files.
        pdf_filename (str): Optional original PDF filename to use for merged file.
        pdf_path (str): Path to the source PDF file for checksum calculation.
        metrics (Dict): Dictionary containing processing metrics.

    Returns:
        Path: Path to the created merged file.
    """
    markdown_files = sorted(markdown_dir.glob("page_*.md"))
    
    # Determine the merged filename
    if pdf_filename:
        base_name = Path(pdf_filename).stem
        merged_filename = f"{base_name}.md"
    else:
        merged_filename = "merged.md"
    
    merged_file = markdown_dir / merged_filename

    if markdown_files:
        with open(merged_file, "w", encoding="utf-8") as merged_f:
            # Header
            merged_f.write("# Merged Document\n\n")
            merged_f.write(f"*Generated from {len(markdown_files)} pages*\n\n")
            merged_f.write("---\n\n")
            
            # Content from individual pages
            errors_found = []
            warnings_found = []
            network_diagrams_count = 0
            
            for i, md_file in enumerate(markdown_files, 1):
                with open(md_file, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read().strip()
                    if content:
                        merged_f.write(content)
                        merged_f.write("\n\n")
                        
                        # Analyze content for metrics
                        if "Network Diagram" in content:
                            network_diagrams_count += 1
                        if "[Error" in content or "error:" in content.lower():
                            errors_found.append(f"Page {i}")
                        if "[Warning" in content or "timed out" in content.lower():
                            warnings_found.append(f"Page {i}")
                        
                        if i < len(markdown_files):
                            merged_f.write("---\n\n")
            
            # Footer with metrics
            merged_f.write("\n\n---\n\n")
            merged_f.write("## 📊 Processing Metrics\n\n")
            merged_f.write("### Document Information\n")
            merged_f.write(f"- **Source File**: `{pdf_filename or 'Unknown'}`\n")
            
            if pdf_path and Path(pdf_path).exists():
                file_size = Path(pdf_path).stat().st_size / (1024 * 1024)  # MB
                merged_f.write(f"- **File Size**: {file_size:.2f} MB\n")
                checksum = calculate_file_checksum(pdf_path, 'md5')
                merged_f.write(f"- **MD5 Checksum**: `{checksum}`\n")
            
            merged_f.write(f"- **Total Pages Processed**: {len(markdown_files)}\n")
            merged_f.write(f"- **Network Diagrams Detected**: {network_diagrams_count}\n")
            
            merged_f.write("\n### Processing Details\n")
            current_time = datetime.now()
            merged_f.write(f"- **Extraction Date**: {current_time.strftime('%Y-%m-%d')}\n")
            merged_f.write(f"- **Extraction Time**: {current_time.strftime('%H:%M:%S %Z')}\n")
            
            if metrics:
                if 'text_model' in metrics:
                    merged_f.write(f"- **Text Extraction Model**: `{metrics['text_model']}`\n")
                if 'network_model' in metrics:
                    merged_f.write(f"- **Network Processing Model**: `{metrics['network_model']}`\n")
                if 'processing_time' in metrics:
                    merged_f.write(f"- **Total Processing Time**: {metrics['processing_time']}\n")
                if 'mode' in metrics:
                    merged_f.write(f"- **Processing Mode**: {metrics['mode']}\n")
            
            merged_f.write("\n### Quality Report\n")
            
            # Errors and warnings
            if errors_found:
                merged_f.write(f"- **⚠️ Errors Found**: {len(errors_found)} pages\n")
                merged_f.write(f"  - Pages with errors: {', '.join(errors_found)}\n")
            else:
                merged_f.write("- **✅ Errors**: None detected\n")
            
            if warnings_found:
                merged_f.write(f"- **⚠️ Warnings/Timeouts**: {len(warnings_found)} pages\n")
                merged_f.write(f"  - Pages with warnings: {', '.join(warnings_found)}\n")
            else:
                merged_f.write("- **✅ Warnings**: None detected\n")
            
            # Success metrics
            if metrics:
                if 'network_diagrams_processed' in metrics:
                    merged_f.write(f"- **Network Diagrams Successfully Processed**: {metrics['network_diagrams_processed']}\n")
                if 'regular_pages' in metrics:
                    merged_f.write(f"- **Text Pages Processed**: {metrics['regular_pages']}\n")
                if 'confidence_threshold' in metrics:
                    merged_f.write(f"- **Detection Confidence Threshold**: {metrics['confidence_threshold']}\n")
            
            # Additional metrics
            merged_f.write("\n### Processing Configuration\n")
            if metrics:
                if 'auto_detect' in metrics:
                    merged_f.write(f"- **Auto-Detection**: {'Enabled' if metrics['auto_detect'] else 'Disabled'}\n")
                if 'use_icons' in metrics:
                    merged_f.write(f"- **Icons in Diagrams**: {'Enabled' if metrics['use_icons'] else 'Disabled'}\n")
                if 'fast_extraction' in metrics:
                    merged_f.write(f"- **Fast Extraction Mode**: {'Enabled' if metrics['fast_extraction'] else 'Disabled'}\n")
                if 'timeout_seconds' in metrics:
                    merged_f.write(f"- **Timeout per Operation**: {metrics['timeout_seconds']} seconds\n")
            
            merged_f.write("\n---\n")
            merged_f.write("\n*This document was automatically generated by [NetIntel-OCR](https://github.com/netintel-ocr)*\n")

    return merged_file


def update_index_file(base_output_dir: Path, pdf_filename: str, md5_checksum: str, processing_time: str = None) -> None:
    """
    Update or create the index.md file with document processing information.
    
    Args:
        base_output_dir (Path): Base output directory (e.g., 'output')
        pdf_filename (str): Name of the processed PDF file
        md5_checksum (str): MD5 checksum of the PDF (also the folder name)
        processing_time (str): Optional processing time string
    """
    index_file = base_output_dir / "index.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create header if file doesn't exist
    if not index_file.exists():
        with open(index_file, "w", encoding="utf-8") as f:
            f.write("# NetIntel-OCR Processing Index\n\n")
            f.write("This index tracks all documents processed by NetIntel-OCR.\n\n")
            f.write("| Filename | Timestamp | MD5 Checksum | Folder | Processing Time |\n")
            f.write("|----------|-----------|--------------|--------|----------------|\n")
    
    # Append new entry
    with open(index_file, "a", encoding="utf-8") as f:
        folder_link = f"[📁 {md5_checksum[:8]}...](./{md5_checksum}/)"
        processing_time_str = processing_time if processing_time else "N/A"
        f.write(f"| {pdf_filename} | {timestamp} | `{md5_checksum}` | {folder_link} | {processing_time_str} |\n")


def setup_output_dirs_with_checksum(base_output_dir: str, pdf_path: str) -> tuple[Path, Path, str]:
    """
    Create output directories based on MD5 checksum of the PDF file.
    
    Args:
        base_output_dir (str): Base output directory (e.g., 'output')
        pdf_path (str): Path to the PDF file
    
    Returns:
        tuple: (image_dir, markdown_dir, md5_checksum)
    """
    # Calculate MD5 checksum of the PDF
    md5_checksum = calculate_file_checksum(pdf_path, 'md5')
    
    # Create base output directory if it doesn't exist
    base_dir = Path(base_output_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Create checksum-based subdirectory
    output_dir = base_dir / md5_checksum
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create image and markdown directories
    image_dir = output_dir / "images"
    markdown_dir = output_dir / "markdown"
    
    image_dir.mkdir(parents=True, exist_ok=True)
    markdown_dir.mkdir(parents=True, exist_ok=True)
    
    return image_dir, markdown_dir, md5_checksum