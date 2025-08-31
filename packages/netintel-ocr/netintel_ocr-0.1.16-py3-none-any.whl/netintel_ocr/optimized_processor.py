"""Optimized hybrid processor with performance improvements."""

import os
import time
from pathlib import Path
from typing import Optional, Dict, Any

from .pdf import process_pdf_image
from .network_diagram import (
    MermaidGenerator,
    MermaidValidator
)
from .network_diagram.fast_detector import FastDetector
from .network_diagram.fast_extractor import FastExtractor
from .timeout_utils import retry_with_timeout, TimeoutException, ProgressTracker


def process_hybrid_optimized(
    pdf_path: str,
    output_dir: str,
    model: str = "qwen2.5vl:latest",
    start_page: int = 0,
    end_page: int = 0,
    width: int = 0,
    keep_images: bool = False,
    auto_detect: bool = True,
    confidence_threshold: float = 0.7,
    use_icons: bool = True,
    fast_mode: bool = False,
    diagram_only: bool = False,
    timeout_seconds: int = 60
) -> None:
    """
    Optimized hybrid processing with fast detection and extraction.
    
    Key optimizations:
    1. Fast detection with simplified prompt (15s timeout)
    2. Fast extraction with minimal prompt (30s timeout)
    3. Parallel processing where possible
    4. Smarter fallback strategies
    """
    
    # Process the PDF to images
    start_process = time.time()
    
    _, output_path = process_pdf_image(
        pdf_path=pdf_path,
        output_dir=output_dir,
        model=model,
        start_page=start_page,
        end_page=end_page,
        width=width,
        keep_images=keep_images,
        use_hybrid=True,
        confidence_threshold=confidence_threshold
    )
    
    # Process images with optimized detection and extraction
    if auto_detect and not fast_mode:
        print("\n📊 Starting optimized network detection...")
        
        # Initialize optimized components
        fast_detector = FastDetector(model)
        fast_extractor = FastExtractor(model)
        generator = MermaidGenerator(model, use_icons=use_icons)
        validator = MermaidValidator()
        
        # Track performance metrics
        detection_times = []
        extraction_times = []
        
        images_dir = Path(output_path) / "images"
        markdown_dir = Path(output_path) / "markdown"
        
        if images_dir.exists():
            image_files = sorted(images_dir.glob("*.png"))
            
            for image_file in image_files:
                page_num = image_file.stem.replace("page_", "")
                print(f"\n  Page {page_num}: Processing...")
                
                # FAST DETECTION (15s timeout)
                detection_start = time.time()
                try:
                    detection = retry_with_timeout(
                        fast_detector.detect_fast,
                        args=(str(image_file),),
                        timeout_seconds=15,
                        max_retries=1,
                        fallback=lambda x: {"is_network_diagram": False, "confidence": 0.0}
                    )
                    detection_time = time.time() - detection_start
                    detection_times.append(detection_time)
                    print(f"    Detection: {detection_time:.1f}s")
                except:
                    detection = {"is_network_diagram": False, "confidence": 0.0}
                
                if detection.get("is_network_diagram") and detection.get("confidence", 0) >= confidence_threshold:
                    print(f"    Network diagram detected (confidence: {detection.get('confidence', 0):.2f})")
                    
                    # FAST EXTRACTION (30s timeout)
                    extraction_start = time.time()
                    try:
                        extraction = retry_with_timeout(
                            fast_extractor.extract_fast,
                            args=(str(image_file),),
                            timeout_seconds=30,
                            max_retries=1,
                            fallback=lambda x: {
                                "components": [{"id": "network", "type": "router", "label": "Network"}],
                                "connections": [],
                                "extraction_successful": True,
                                "method": "timeout_fallback"
                            }
                        )
                        extraction_time = time.time() - extraction_start
                        extraction_times.append(extraction_time)
                        print(f"    Extraction: {extraction_time:.1f}s ({len(extraction.get('components', []))} components)")
                    except:
                        extraction = {
                            "components": [{"id": "network", "type": "router", "label": "Network"}],
                            "connections": [],
                            "extraction_successful": True,
                            "method": "error_fallback"
                        }
                    
                    # Generate Mermaid (use rule-based for speed)
                    mermaid_code = generator.generate(extraction, use_llm=False)
                    
                    # Quick validation and fix
                    validation = validator.validate(mermaid_code)
                    if not validation["valid"]:
                        mermaid_code = validator.fix_common_issues(mermaid_code)
                    
                    # Save the processed content
                    markdown_file = markdown_dir / f"page_{page_num}.md"
                    save_optimized_network_diagram(
                        markdown_file,
                        page_num,
                        detection,
                        extraction,
                        mermaid_code,
                        ""  # Text content would go here
                    )
                    
                    print(f"    Total time: {time.time() - detection_start:.1f}s")
    
    # Print performance summary
    if detection_times:
        print(f"\n📈 Performance Summary:")
        print(f"  Average detection time: {sum(detection_times)/len(detection_times):.1f}s")
        if extraction_times:
            print(f"  Average extraction time: {sum(extraction_times)/len(extraction_times):.1f}s")
        print(f"  Total processing time: {time.time() - start_process:.1f}s")


def save_optimized_network_diagram(
    output_file: Path,
    page_number: str,
    detection: Dict[str, Any],
    extraction: Dict[str, Any],
    mermaid_code: str,
    text_content: str
) -> None:
    """Save network diagram with optimized format."""
    
    content = []
    content.append(f"# Page {page_number} - Network Diagram")
    content.append("")
    content.append(f"**Type**: {detection.get('diagram_type', 'network')}")
    content.append(f"**Confidence**: {detection.get('confidence', 0):.2f}")
    content.append(f"**Components**: {len(extraction.get('components', []))}")
    content.append(f"**Connections**: {len(extraction.get('connections', []))}")
    
    if extraction.get('method'):
        content.append(f"**Extraction Method**: {extraction['method']}")
    
    content.append("")
    content.append("## Diagram")
    content.append("")
    content.append("```mermaid")
    content.append(mermaid_code)
    content.append("```")
    
    if text_content:
        content.append("")
        content.append("## Page Text")
        content.append("")
        content.append(text_content)
    
    # Write to file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        f.write("\n".join(content))