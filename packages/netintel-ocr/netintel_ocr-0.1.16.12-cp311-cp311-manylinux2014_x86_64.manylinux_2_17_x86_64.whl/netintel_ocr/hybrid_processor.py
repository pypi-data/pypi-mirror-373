"""Hybrid processor with automatic network diagram detection."""

import sys
import time
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

from .pdf import pdf_to_images
from .pdf_utils import check_pdf_page_count
from .ollama import check_for_server, transcribe_image
from .utils import (
    setup_output_dirs, 
    resize_image, 
    merge_markdown_files, 
    merge_markdown_files_with_metrics,
    setup_output_dirs_with_checksum,
    update_index_file
)
from .output_utils import debug_print, info_print, always_print, progress_print, error_print
from .logging_utils import ProcessingLogger
from .network_diagram import (
    NetworkDiagramDetector,
    ComponentExtractor,
    MermaidGenerator,
    MermaidValidator
)
from .network_diagram.robust_validator import RobustMermaidValidator
from .timeout_utils import ProgressTracker, TimeoutException, retry_with_timeout
from .checkpoint import CheckpointManager, ProcessingState
from .table_extraction import (
    TableDetector,
    LLMTableExtractor,
    TableValidator,
    TableJSONGenerator
)
from .vector_generator import VectorGenerator
from .diagram_detection import (
    UnifiedDiagramDetector,
    EnhancedFlowProcessor,
    DiagramContextExtractor
)


def process_pdf_hybrid(
    pdf_path: str,
    output_dir: str,
    model: str,
    keep_images: bool,
    width: int,
    start: int,
    end: int,
    auto_detect: bool = True,
    network_model: str = None,
    flow_model: str = None,
    confidence_threshold: float = 0.7,
    use_icons: bool = False,
    fast_mode: bool = False,
    timeout_seconds: int = 60,
    include_text_with_diagrams: bool = True,
    fast_extraction: bool = False,
    force_multi_diagram: bool = False,
    debug: bool = False,
    quiet: bool = False,
    resume: bool = False,
    extract_tables: bool = True,
    table_confidence: float = 0.7,
    table_method: str = 'hybrid',
    save_table_json: bool = False,
    # Vector generation options (v0.1.7)
    generate_vector: bool = True,  # Default: enabled
    vector_format: str = 'lancedb',
    chunk_size: int = 1000,
    chunk_overlap: int = 100,
    chunk_strategy: str = 'semantic',
    array_strategy: str = 'separate_rows',
    embedding_metadata: bool = False,
    embedding_model: str = 'qwen3-embedding:4b',
    embedding_provider: str = 'ollama',
) -> None:
    """
    Process a PDF file with automatic network diagram and table detection.
    
    This hybrid processor automatically detects network diagrams and tables on each page
    and processes them accordingly - network diagrams as Mermaid, tables as JSON, and regular text.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save the output
        model: The model to use for text processing
        keep_images: Whether to keep the images after processing
        width: Width to resize images to
        start: Start page number
        end: End page number
        auto_detect: Enable automatic network diagram detection (default: True)
        network_model: Optional separate model for network diagram and table processing
        flow_model: Optional separate model for flow diagram processing (uses network_model if not specified)
        confidence_threshold: Minimum confidence for network diagram detection
        use_icons: Whether to use icons in Mermaid diagrams
        fast_mode: Skip detection and process as text only (for speed)
        timeout_seconds: Timeout for each LLM operation (default: 60 seconds)
        include_text_with_diagrams: Also transcribe text on pages with network diagrams
        fast_extraction: Use optimized fast extraction mode
        force_multi_diagram: Force multi-diagram extraction
        debug: Enable debug output
        quiet: Minimal output mode
        resume: Resume from checkpoint if available
        extract_tables: Enable table extraction (default: True)
        table_confidence: Minimum confidence for table detection (default: 0.7)
        table_method: Table extraction method ('llm' only supported now)
        save_table_json: Save tables as separate JSON files
        generate_vector: Generate vector database files (default: True in v0.1.7)
        vector_format: Target vector database format (default: 'lancedb')
        chunk_size: Chunk size in tokens (default: 1000)
        chunk_overlap: Overlap between chunks in tokens (default: 100)
        chunk_strategy: Chunking strategy ('semantic', 'fixed', 'sentence')
        array_strategy: Array handling in JSON ('separate_rows', 'concatenate', 'serialize')
        embedding_metadata: Include additional metadata for embeddings
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    # Determine which models to use
    text_model = model
    diagram_model = network_model if network_model else model
    flow_diagram_model = flow_model if flow_model else diagram_model  # Use flow_model if specified, else fallback
    
    # Check model availability before processing
    from .ollama import check_model_availability, check_for_server, get_correct_model_name
    
    # Display current OLLAMA_HOST
    import os
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    debug_print(f"Using OLLAMA_HOST: {ollama_host}")
    
    # First check if Ollama server is running
    if not check_for_server():
        error_print("Error: Ollama server is not running. Please start Ollama first.")
        error_print(f"Attempted connection to: {ollama_host}")
        sys.exit(1)
    
    # Check each required model and get correct names
    models_to_check = [text_model]
    if auto_detect and not fast_mode:
        if diagram_model != text_model:
            models_to_check.append(diagram_model)
        if flow_diagram_model != diagram_model:
            models_to_check.append(flow_diagram_model)
    
    debug_print("Checking model availability...")
    missing_models = []
    corrected_models = {}
    
    for model_name in models_to_check:
        if not check_model_availability(model_name):
            missing_models.append(model_name)
            error_print(f"  ❌ Model not found: {model_name}")
        else:
            # Get the correctly-cased model name
            correct_name = get_correct_model_name(model_name)
            corrected_models[model_name] = correct_name
            if correct_name != model_name:
                debug_print(f"  ✅ Model available: {model_name} (using {correct_name})")
            else:
                debug_print(f"  ✅ Model available: {model_name}")
    
    if missing_models:
        error_print(f"\nError: The following required models are not available:")
        for m in missing_models:
            error_print(f"  - {m}")
        error_print("\nPlease pull the required models using:")
        for m in missing_models:
            error_print(f"  ollama pull {m}")
        sys.exit(1)
    
    # Update model names to use correct case
    text_model = corrected_models.get(text_model, text_model)
    if diagram_model in corrected_models:
        diagram_model = corrected_models[diagram_model]
    if flow_diagram_model in corrected_models:
        flow_diagram_model = corrected_models[flow_diagram_model]
    
    # Check page count before processing
    total_pages, actual_start, actual_end = check_pdf_page_count(str(pdf_path), start, end)
    pages_to_process = actual_end - actual_start + 1
    
    # Estimate processing time (30-60 seconds per page for auto-detect, 15-30 for fast mode)
    if fast_mode:
        min_time = pages_to_process * 15
        max_time = pages_to_process * 30
    else:
        min_time = pages_to_process * 30
        max_time = pages_to_process * 60
    
    min_minutes = min_time // 60
    min_seconds = min_time % 60
    max_minutes = max_time // 60
    max_seconds = max_time % 60
    
    # Show detailed info only in debug mode
    if debug:
        debug_print(f"\n{'='*60}")
        debug_print(f"📄 PDF Processing Information")
        if auto_detect and not fast_mode:
            debug_print(f"    (Hybrid Mode - Auto-detecting network diagrams)")
        elif fast_mode:
            debug_print(f"    (Fast Mode - Text transcription only)")
        debug_print(f"{'='*60}")
        debug_print(f"  Document: {pdf_path.name}")
        debug_print(f"  Total pages in PDF: {total_pages}")
        debug_print(f"  Pages to process: {actual_start} to {actual_end} ({pages_to_process} pages)")
        debug_print(f"  Models Configuration:")
        debug_print(f"    Text Extraction: {text_model}")
        if auto_detect and not fast_mode and diagram_model != text_model:
            debug_print(f"    Network Processing: {diagram_model}")
        if auto_detect and not fast_mode and flow_diagram_model != diagram_model:
            debug_print(f"    Flow Processing: {flow_diagram_model}")
        if auto_detect and not fast_mode:
            debug_print(f"  Auto-detection: Enabled (threshold: {confidence_threshold})")
        debug_print(f"  Estimated time: {min_minutes}:{min_seconds:02d} - {max_minutes}:{max_seconds:02d}")
        debug_print(f"{'='*60}\n")
    elif not quiet:
        # Simple one-liner for default mode
        info_print(f"Processing {pdf_path.name} (pages {actual_start}-{actual_end})...")
    
    if not check_for_server():
        import os
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        always_print(
            f"Error: Cannot connect to Ollama server at {host}.\n"
            "Please ensure:\n"
            "1. Ollama server is running\n"
            "2. The OLLAMA_HOST environment variable is set correctly if using a remote server\n"
            "3. The server is accessible from this machine"
        )
        sys.exit(1)
    
    # Setup output directories based on MD5 checksum
    image_dir, markdown_dir, md5_checksum = setup_output_dirs_with_checksum(output_dir, str(pdf_path))
    output_base = Path(output_dir) / md5_checksum
    
    # Store base output directory for index file
    base_output_dir = Path(output_dir)
    
    # Initialize logger (always with debug level to file, console based on debug flag)
    logger = ProcessingLogger(
        output_dir=str(output_base),
        filename=pdf_path.name,
        verbose=debug  # Console output only if debug flag is set
    )
    logger.log_start()
    
    # Initialize checkpoint manager
    checkpoint_manager = CheckpointManager(Path(output_dir), str(pdf_path), md5_checksum)
    processing_state = ProcessingState(checkpoint_manager)
    
    # Check if resuming from checkpoint
    if resume:
        resume_info = checkpoint_manager.get_resume_info()
        if resume_info["has_checkpoint"]:
            # Load previous state
            if processing_state.load_from_checkpoint():
                # Show resume summary
                if not quiet:
                    always_print(processing_state.get_resume_summary())
                
                # Adjust start page to resume from
                completed_pages = checkpoint_manager.get_completed_pages()
                if completed_pages:
                    # Find the first page we need to process
                    for page_num in range(actual_start, actual_end + 1):
                        if page_num not in completed_pages:
                            actual_start = page_num
                            break
                    else:
                        # All pages already processed
                        always_print(f"All pages already processed. Output: {output_base}")
                        return
                
                # Update statistics from checkpoint
                network_diagrams_found = processing_state.network_diagrams_found
                regular_pages = processing_state.regular_pages
            else:
                if not quiet:
                    always_print("Failed to load checkpoint. Starting fresh.")
        else:
            if not quiet:
                always_print("No checkpoint found. Starting fresh processing.")
    
    # Initialize network diagram processors only if needed
    detector = None
    extractor = None
    generator = None
    validator = None
    
    # Initialize table extraction processors
    table_detector = None
    llm_extractor = None
    table_validator = None
    table_json_generator = None
    
    if auto_detect and not fast_mode:
        # Initialize network diagram components
        detector = NetworkDiagramDetector(model=diagram_model)
        extractor = ComponentExtractor(model=diagram_model)
        generator = MermaidGenerator(model=diagram_model, use_icons=use_icons)
        validator = MermaidValidator()
        
        # Initialize unified diagram detector for flow/network detection
        unified_detector = UnifiedDiagramDetector(model=diagram_model)
        
        # Initialize flow processor with dedicated flow model
        flow_processor = EnhancedFlowProcessor(model=flow_diagram_model)
        
        # Initialize table extraction if enabled (uses text model, not diagram model)
        if extract_tables:
            table_detector = TableDetector(model=model, confidence_threshold=table_confidence)
            llm_extractor = LLMTableExtractor(model=model)
            table_validator = TableValidator()
            table_json_generator = TableJSONGenerator()
    
    try:
        # Track overall processing time
        processing_start_time = time.time()
        
        # Convert PDF to images
        debug_print("Converting PDF to images...")
        pdf_to_images(str(pdf_path), image_dir, start, end)
        
        # Process each page
        # Sort image files numerically by page number
        image_files = sorted(
            image_dir.glob("page_*.png"),
            key=lambda x: int(x.stem.split('_')[1])
        )
        total_pages = len(image_files)
        
        # Resize images if requested
        if width > 0:
            for image_file in tqdm(image_files, desc="Resizing images"):
                resize_image(str(image_file), str(image_file), width)
        
        # Track statistics (initialize only if not resuming)
        if not resume or not processing_state.load_from_checkpoint():
            network_diagrams_found = 0
            regular_pages = 0
            pages_with_mixed_content = 0
            # Collections for vector generation (v0.1.7)
            all_extracted_tables = []
            all_network_diagrams = []
            # Store page texts for context extraction
            all_page_texts = {}
            
            # Initialize processing state
            processing_state.initialize(
                start=actual_start,
                end=actual_end,
                total=total_pages,
                models={'text': text_model, 'network': diagram_model},
                settings={
                    'confidence_threshold': confidence_threshold,
                    'use_icons': use_icons,
                    'fast_extraction': fast_extraction,
                    'timeout_seconds': timeout_seconds
                }
            )
        else:
            # Use values from checkpoint
            pages_with_mixed_content = 0  # Not tracked in checkpoint yet
        
        # Process each image
        for image_file in tqdm(image_files, desc="Processing pages", total=total_pages):
            try:
                # Extract page number
                page_number = int(image_file.stem.split("_")[1])
                markdown_file = markdown_dir / f"page_{page_number:03d}.md"
                
                # Log page start
                logger.log_page_start(page_number, total_pages)
                
                # Skip if page already processed (when resuming)
                if resume and checkpoint_manager.is_page_complete(page_number):
                    debug_print(f"  Page {page_number}: Already processed, skipping")
                    logger.log_step("Page already processed", "Skipping")
                    continue
                
                # Track processing time for this page
                page_start_time = time.time()
                
                # Check if auto-detect is enabled and not in fast mode
                if auto_detect and not fast_mode and detector:
                    # Progress tracking for the page
                    tracker = ProgressTracker()
                    
                    # Step 1: ALWAYS transcribe text first (so we have it even if diagram processing fails)
                    page_text = None
                    try:
                        step_msg = f"Transcribing page text and tables ({text_model})"
                        step_start = tracker.start_step(step_msg)
                        logger.log_step("Text transcription", f"Using model: {text_model}")
                        transcribe_start = time.time()
                        page_text = retry_with_timeout(
                            transcribe_image,
                            args=(str(image_file),),
                            kwargs={"model": text_model},
                            timeout_seconds=timeout_seconds * 2,  # Allow more time for text
                            max_retries=1,
                            fallback=lambda x, **kw: "[Text transcription timed out]"
                        )
                        transcribe_time = time.time() - transcribe_start
                        tracker.end_step(step_start)
                        logger.log_model_call(text_model, "text_transcription", transcribe_time)
                    except Exception as e:
                        debug_print(f"\n    Text transcription failed: {str(e)[:100]}")
                        logger.log_error(f"Text transcription failed", e, page_number)
                        page_text = f"[Error transcribing text: {str(e)[:200]}]"
                    
                    # Store page text for context extraction
                    all_page_texts[page_number] = page_text
                    
                    # Step 2: Detect diagram type (network, flow, or hybrid)
                    try:
                        step_msg = f"Checking for diagrams ({diagram_model})"
                        step_start = tracker.start_step(step_msg)
                        logger.log_step("Diagram detection", f"Using model: {diagram_model}")
                        detect_start = time.time()
                        
                        # Use unified detector to identify diagram type
                        unified_detection = retry_with_timeout(
                            unified_detector.detect,
                            args=(str(image_file),),
                            timeout_seconds=timeout_seconds,
                            max_retries=1,
                            fallback=lambda x: {"has_diagram": False, "diagram_category": None, "confidence": 0.0}
                        )
                        
                        # Map unified detection to existing format for backward compatibility
                        detection = {
                            "is_network_diagram": unified_detection.get("is_diagram", False) and 
                                                 unified_detection.get("diagram_category") in ["network", "hybrid"],
                            "is_flow_diagram": unified_detection.get("is_diagram", False) and 
                                              unified_detection.get("diagram_category") in ["flow", "hybrid"],
                            "diagram_category": unified_detection.get("diagram_category"),
                            "confidence": unified_detection.get("confidence", 0.0),
                            "diagram_type": unified_detection.get("diagram_type", "unknown")
                        }
                        
                        detect_time = time.time() - detect_start
                        tracker.end_step(step_start)
                        logger.log_model_call(diagram_model, "diagram_detection", detect_time)
                        logger.log_detection(
                            f"diagram ({detection.get('diagram_category', 'none')})",
                            detection.get("confidence", 0.0),
                            "detected" if unified_detection.get("is_diagram") else "not detected"
                        )
                    except TimeoutException:
                        debug_print(f"\n    Detection timed out after {timeout_seconds}s, treating as text page")
                        logger.log_warning(f"Detection timeout after {timeout_seconds}s", page_number)
                        detection = {"is_network_diagram": False, "confidence": 0.0}
                    except Exception as e:
                        debug_print(f"\n    Detection failed: {str(e)[:100]}")
                        logger.log_error("Detection failed", e, page_number)
                        detection = {"is_network_diagram": False, "confidence": 0.0}
                    
                    # Check if it's a flow diagram
                    if detection.get("is_flow_diagram") and detection.get("confidence", 0) >= confidence_threshold:
                        # Process as flow diagram using dedicated flow processor
                        network_diagrams_found += 1  # Count as diagram found
                        debug_print(f"\n  Page {page_number}: Flow diagram detected (confidence: {detection.get('confidence', 0):.2f})")
                        debug_print(f"    Type: {detection.get('diagram_type', 'unknown')}")
                        debug_print(f"    Using flow model: {flow_diagram_model}")
                        
                        try:
                            # Process flow diagram with enhanced flow processor
                            step_msg = f"Processing flow diagram ({flow_diagram_model})"
                            step_start = tracker.start_step(step_msg)
                            
                            # Gather surrounding text for flow diagram context
                            before_text = ""
                            after_text = ""
                            
                            # Get text from previous page if available
                            if page_number - 1 in all_page_texts:
                                prev_text = all_page_texts[page_number - 1]
                                before_text = prev_text[-1000:] if prev_text else ""
                            
                            # Add text from current page
                            if page_text:
                                before_text += "\n" + page_text[:500]
                                after_text = page_text[500:1500] if len(page_text) > 500 else page_text
                            
                            flow_result = flow_processor.process_complete(
                                image_path=str(image_file),
                                surrounding_text={
                                    'before': before_text,
                                    'after': after_text
                                }
                            )
                            
                            tracker.end_step(step_start)
                            
                            if flow_result.get('is_flow_diagram'):
                                # Generate markdown content with flow diagram
                                markdown_content = f"# Page {page_number} - Flow Diagram\n\n"
                                markdown_content += f"**Diagram Type**: {flow_result.get('diagram_type', 'flow')}\n"
                                markdown_content += f"**Confidence**: {flow_result.get('confidence', 0):.2f}\n\n"
                                
                                if flow_result.get('formatted_output'):
                                    markdown_content += flow_result['formatted_output']
                                else:
                                    # Fallback formatting
                                    markdown_content += "## Flow Diagram\n\n"
                                    if flow_result.get('mermaid'):
                                        markdown_content += "```mermaid\n"
                                        markdown_content += flow_result['mermaid']
                                        markdown_content += "\n```\n\n"
                                
                                # Add page text if included
                                if include_text_with_diagrams and page_text:
                                    markdown_content += "## Page Text\n\n"
                                    markdown_content += page_text
                                
                                # Save to file
                                with open(markdown_file, "w", encoding="utf-8") as f:
                                    f.write(markdown_content)
                                
                                logger.log_output_created("Flow diagram page", str(markdown_file))
                                logger.log_mermaid_generation(True, None)
                                debug_print(f"    Saved: {markdown_file.name} (flow diagram)")
                            else:
                                # Flow processing failed, save with text
                                with open(markdown_file, "w", encoding="utf-8") as f:
                                    f.write(f"# Page {page_number}\n\n")
                                    f.write("*Flow diagram detected but processing failed*\n\n")
                                    f.write(page_text)
                                logger.log_warning("Flow diagram processing failed", page_number)
                        
                        except Exception as e:
                            debug_print(f"    Flow diagram processing failed: {str(e)}")
                            logger.log_error("Flow diagram processing failed", e, page_number)
                            # Save text with error note
                            with open(markdown_file, "w", encoding="utf-8") as f:
                                f.write(f"# Page {page_number}\n\n")
                                f.write(f"*Flow diagram processing error: {str(e)[:200]}*\n\n")
                                f.write(page_text)
                        
                        # Save checkpoint
                        page_processing_time = time.time() - page_start_time
                        processing_state.mark_page_complete(
                            page_number=page_number,
                            is_network_diagram=True,  # Count as diagram
                            has_errors=False,
                            processing_time=page_processing_time
                        )
                    
                    elif detection.get("is_network_diagram") and detection.get("confidence", 0) >= confidence_threshold:
                        # Process as network diagram (we already have the text)
                        network_diagrams_found += 1
                        debug_print(f"\n  Page {page_number}: Network diagram detected (confidence: {detection.get('confidence', 0):.2f})")
                        debug_print(f"    Type: {detection.get('diagram_type', 'unknown')}")
                        
                        # Check if we should use multi-diagram extraction
                        # This is heuristic based - could be improved with better detection
                        use_multi_diagram = False
                        
                        # Count potential figure references in text
                        import re
                        figure_refs = re.findall(r'Figure \d+', page_text, re.IGNORECASE)
                        unique_figures = set(figure_refs)
                        
                        # Use multi-diagram if:
                        # 1. Force flag is set
                        # 2. Multiple figure references found
                        # 3. Detection mentions multiple diagrams
                        # 4. Page explicitly mentions multiple diagrams/figures
                        if (force_multi_diagram or
                            len(unique_figures) > 1 or 
                            "multiple" in detection.get("description", "").lower() or
                            ("figure" in page_text.lower() and len(unique_figures) >= 2)):
                            use_multi_diagram = True
                            if force_multi_diagram:
                                debug_print(f"    Multi-diagram extraction forced by user")
                            else:
                                debug_print(f"    Multiple diagrams likely ({len(unique_figures)} figure references found)")
                        
                        if use_multi_diagram:
                            # Use multi-diagram processor
                            debug_print("    Using multi-diagram extraction...")
                            from .multi_diagram_processor import MultiDiagramProcessor
                            multi_processor = MultiDiagramProcessor(
                                model=diagram_model, 
                                timeout=timeout_seconds,
                                use_improved=True  # Use improved extraction with better whitespace handling
                            )
                            
                            # Process with multi-diagram approach
                            multi_results = multi_processor.process_page_with_multiple_diagrams(
                                pdf_path,
                                page_number,
                                str(image_file),
                                str(output_dir)
                            )
                            
                            # Generate markdown for multi-diagrams
                            markdown_content = multi_processor.generate_markdown_for_multi_diagrams(
                                multi_results,
                                text_content=page_text
                            )
                            
                            # Save to file
                            with open(markdown_file, "w", encoding="utf-8") as f:
                                f.write(markdown_content)
                            
                            logger.log_output_created("Multi-diagram page", str(markdown_file))
                            logger.log_page_end(page_number, success=True)
                            debug_print(f"    Saved: {markdown_file.name} (multi-diagram page)")
                            continue  # Skip to next page
                        
                        # Step 3: Extract network components with timeout
                        try:
                            step_msg = f"Extracting components ({diagram_model})"
                            step_start = tracker.start_step(step_msg)
                            
                            if fast_extraction:
                                # Use optimized fast extraction with shorter timeout
                                from .network_diagram.fast_extractor import extract_with_optimization
                                extraction = retry_with_timeout(
                                    extract_with_optimization,
                                    args=(str(image_file),),
                                    kwargs={"model": diagram_model, "use_fast": True},
                                    timeout_seconds=min(20, timeout_seconds),  # Much shorter timeout for fast extraction
                                    max_retries=1,
                                    fallback=lambda x, **kw: {"extraction_successful": False, "error": "Timeout"}
                                )
                                tracker.end_step(step_start, f"Fast ({len(extraction.get('components', []))} components)")
                            else:
                                # Use standard extraction
                                extraction = retry_with_timeout(
                                    extractor.extract,
                                    args=(str(image_file),),
                                    timeout_seconds=timeout_seconds,
                                    max_retries=1,
                                    fallback=lambda x: {"extraction_successful": False, "error": "Timeout"}
                                )
                                tracker.end_step(step_start)
                        except TimeoutException:
                            debug_print(f"\n    Component extraction timed out after {timeout_seconds}s")
                            extraction = {"extraction_successful": False, "error": "Timeout"}
                        except Exception as e:
                            debug_print(f"\n    Extraction failed: {str(e)[:100]}")
                            extraction = {"extraction_successful": False, "error": str(e)}
                        
                        if extraction.get("extraction_successful"):
                            debug_print(f"    Components: {len(extraction.get('components', []))}")
                            debug_print(f"    Connections: {len(extraction.get('connections', []))}")
                            
                            # Step 4: Generate Mermaid diagram with timeout
                            try:
                                step_msg = f"Generating Mermaid diagram ({diagram_model})"
                                step_start = tracker.start_step(step_msg)
                                mermaid_code = retry_with_timeout(
                                    generator.generate,
                                    args=(extraction,),
                                    kwargs={"use_llm": True},
                                    timeout_seconds=timeout_seconds,
                                    max_retries=1,
                                    fallback=lambda ext, **kw: generator.generate(ext, use_llm=False)
                                )
                                tracker.end_step(step_start)
                            except TimeoutException:
                                debug_print(f"\n    Mermaid generation timed out, using rule-based generation")
                                mermaid_code = generator.generate(extraction, use_llm=False)
                            except Exception as e:
                                debug_print(f"\n    Generation failed, using rule-based: {str(e)[:100]}")
                                mermaid_code = generator.generate(extraction, use_llm=False)
                            
                            # Step 5: Validate and fix Mermaid code using robust validator
                            step_start = tracker.start_step("Validating Mermaid syntax")
                            
                            # Use robust validator for comprehensive fixing
                            robust_validator = RobustMermaidValidator()
                            is_valid, fixed_mermaid, fix_errors = robust_validator.validate_and_fix(mermaid_code)
                            
                            # Initialize validation dict for later use
                            validation = {"valid": is_valid, "warnings": [], "errors": fix_errors}
                            
                            if is_valid:
                                mermaid_code = fixed_mermaid
                                tracker.end_step(step_start, "Valid")
                            else:
                                # Try the old validator as fallback
                                mermaid_code = validator.fix_common_issues(mermaid_code)
                                validation = validator.validate(mermaid_code)
                                if validation["valid"]:
                                    tracker.end_step(step_start, "Fixed")
                                else:
                                    # Use the robust fix even if not perfect
                                    mermaid_code = fixed_mermaid
                                    tracker.end_step(step_start, "Best effort fix")
                            
                            # Add metadata to mermaid code
                            timestamp = datetime.now().isoformat()
                            mermaid_lines = mermaid_code.split('\n')
                            if mermaid_lines and mermaid_lines[0].startswith('graph'):
                                mermaid_lines.insert(1, f"    %% Network Diagram: Page {page_number}")
                                mermaid_lines.insert(2, f"    %% Generated: {timestamp}")
                                mermaid_lines.insert(3, f"    %% Confidence: {detection.get('confidence', 0):.2f}")
                                mermaid_code = '\n'.join(mermaid_lines)
                            
                            # Step 6: Extract context from surrounding text
                            context_step = tracker.start_step(f"Extracting context ({diagram_model})")
                            context_result = None
                            try:
                                # Gather surrounding text (2 paragraphs before and after)
                                before_text = ""
                                after_text = ""
                                
                                # Get text from previous page if available
                                if page_number - 1 in all_page_texts:
                                    prev_text = all_page_texts[page_number - 1]
                                    # Extract last 2 paragraphs (approximately last 1000 chars)
                                    before_text = prev_text[-1000:] if prev_text else ""
                                
                                # Get text from current page (before diagram)
                                if page_text:
                                    # Take first part of current page text
                                    before_text += "\n" + page_text[:500]
                                    # Take latter part for after context
                                    after_text = page_text[500:1500] if len(page_text) > 500 else page_text
                                
                                # Initialize context extractor
                                context_extractor = DiagramContextExtractor(model=diagram_model)
                                
                                # Extract context based on diagram type
                                context_result = context_extractor.extract_context(
                                    image_path=str(image_file),
                                    mermaid_code=mermaid_code,
                                    surrounding_text={'before': before_text, 'after': after_text},
                                    diagram_category='network'
                                )
                                tracker.end_step(context_step)
                            except Exception as e:
                                tracker.end_step(context_step)
                                debug_print(f"    Context extraction failed: {str(e)[:100]}")
                                # Continue without context - not critical
                            
                            # Step 7: Save to file (with both diagram and text)
                            step_start = tracker.start_step("Writing to file")
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
                                
                                # Write context interpretation if available
                                if context_result and not context_result.get('error'):
                                    f.write("## Context for Diagram\n\n")
                                    
                                    if context_result.get('architecture_summary'):
                                        f.write(f"**Summary**: {context_result['architecture_summary']}\n\n")
                                    
                                    if context_result.get('document_context'):
                                        f.write(f"**Document Context**: {context_result['document_context']}\n\n")
                                    
                                    if context_result.get('security_analysis'):
                                        sec = context_result['security_analysis']
                                        if sec.get('zones') or sec.get('boundaries'):
                                            f.write("### Security Analysis\n")
                                            if sec.get('zones'):
                                                f.write(f"- **Security Zones**: {', '.join(sec['zones'])}\n")
                                            if sec.get('boundaries'):
                                                f.write(f"- **Trust Boundaries**: {', '.join(sec['boundaries'])}\n")
                                            if sec.get('risks'):
                                                f.write(f"- **Potential Risks**: {', '.join(sec['risks'])}\n")
                                            f.write("\n")
                                    
                                    if context_result.get('data_flows'):
                                        f.write("### Data Flows\n")
                                        for flow in context_result['data_flows']:
                                            f.write(f"- {flow}\n")
                                        f.write("\n")
                                    
                                    if context_result.get('critical_components'):
                                        f.write("### Critical Components\n")
                                        for comp in context_result['critical_components']:
                                            f.write(f"- {comp}\n")
                                        f.write("\n")
                                    
                                    if context_result.get('recommendations'):
                                        f.write("### Recommendations\n")
                                        for rec in context_result['recommendations']:
                                            f.write(f"- {rec}\n")
                                        f.write("\n")
                                
                                # Add validation warnings if any
                                if validation.get("warnings"):
                                    f.write("## Notes\n\n")
                                    for warning in validation["warnings"]:
                                        f.write(f"- {warning}\n")
                                    f.write("\n")
                                
                                # Add the page text content (already transcribed at the beginning)
                                if include_text_with_diagrams and page_text:
                                    if page_text != "[Text transcription timed out]" and page_text != "[Error transcribing text:":
                                        f.write("## Page Text Content\n\n")
                                        f.write(page_text)
                                        f.write("\n")
                            tracker.end_step(step_start)
                            
                            total_time = tracker.get_total_time()
                            debug_print(f"    Total processing time: {total_time:.1f}s")
                            
                            # Collect diagram data for vector generation (v0.1.7)
                            if 'all_network_diagrams' in locals():
                                all_network_diagrams.append({
                                    'page': page_number,
                                    'type': detection.get('diagram_type', 'unknown'),
                                    'mermaid_code': mermaid_code,
                                    'data': extraction,
                                    'component_count': len(extraction.get('components', [])),
                                    'connection_count': len(extraction.get('connections', []))
                                })
                            
                            # Save checkpoint for successful network diagram page
                            page_processing_time = time.time() - page_start_time
                            processing_state.mark_page_complete(
                                page_number=page_number,
                                is_network_diagram=True,
                                has_errors=False,
                                processing_time=page_processing_time
                            )
                        else:
                            # Failed to extract components, but still detected as network diagram
                            # We already have the text, just save it with a note about the diagram
                            debug_print(f"    Network diagram detected but extraction failed, saving text with note")
                            pages_with_mixed_content += 1
                            with open(markdown_file, "w", encoding="utf-8") as f:
                                f.write(f"# Page {page_number}\n\n")
                                f.write(f"*Note: Network diagram detected (confidence: {detection.get('confidence', 0):.2f}, type: {detection.get('diagram_type', 'unknown')}) but components could not be extracted for Mermaid conversion.*\n\n")
                                f.write("## Page Content\n\n")
                                if page_text:
                                    f.write(page_text)
                                else:
                                    f.write("[No text content available]")
                            
                            # Save checkpoint for failed extraction page
                            page_processing_time = time.time() - page_start_time
                            processing_state.mark_page_complete(
                                page_number=page_number,
                                is_network_diagram=False,
                                has_errors=True,
                                processing_time=page_processing_time
                            )
                    else:
                        # Not a network diagram
                        # Note: Tables are already extracted in the unified text extraction above
                        tables_extracted = []
                        
                        # Skip separate table extraction since it's done with text
                        if False and extract_tables and table_detector:
                            # Step 3: Detect tables
                            try:
                                step_msg = f"Checking for tables ({model})"
                                step_start = tracker.start_step(step_msg)
                                table_detection = retry_with_timeout(
                                    table_detector.detect,
                                    args=(str(image_file),),
                                    timeout_seconds=timeout_seconds // 2,
                                    max_retries=1,
                                    fallback=lambda x: {"has_tables": False, "confidence": 0.0}
                                )
                                tracker.end_step(step_start)
                                
                                if table_detection.get("has_tables"):
                                    debug_print(f"    Tables detected (confidence: {table_detection.get('confidence', 0):.2f})")
                                    debug_print(f"    Table count: {table_detection.get('table_count', 0)}")
                                    
                                    # Step 4: Extract tables
                                    # Library extraction removed - tables are extracted with text
                                    tables_extracted = []
                                    
                                    # Check if we should skip LLM processing (for ToC)
                                    skip_llm_processing = table_detection.get('skip_llm', False)
                                    
                                    if skip_llm_processing:
                                        debug_print(f"    Skipping LLM processing for Table of Contents")
                                    
                                    # Enhance with LLM if needed (but skip for ToC)
                                    if table_method in ['hybrid', 'llm'] and not skip_llm_processing:
                                        if not tables_extracted:
                                            try:
                                                step_msg = f"Enhancing tables with LLM ({diagram_model})"
                                                step_start = tracker.start_step(step_msg)
                                                
                                                if tables_extracted:
                                                    # Enhance existing tables
                                                    tables_extracted = llm_extractor.enhance_library_results(
                                                        str(image_file),
                                                        tables_extracted,
                                                        timeout=timeout_seconds
                                                    )
                                                else:
                                                    # Extract directly with LLM
                                                    table_type = table_detection.get('table_types', ['simple'])[0] if table_detection.get('table_types') else 'simple'
                                                    llm_table = llm_extractor.extract_from_image(
                                                        str(image_file),
                                                        table_type=table_type,
                                                        fast_mode=fast_extraction,
                                                        timeout=timeout_seconds
                                                    )
                                                    if not llm_table.get('error'):
                                                        tables_extracted = [llm_table]
                                                
                                                tracker.end_step(step_start)
                                            except Exception as e:
                                                debug_print(f"    LLM enhancement failed: {str(e)[:100]}")
                                    
                                    # Validate tables
                                    if tables_extracted:
                                        for table in tables_extracted:
                                            validation = table_validator.validate(table)
                                            table['validation'] = validation
                                            if not validation['overall_valid']:
                                                table = table_validator.auto_correct(table)
                                    
                                    debug_print(f"    Successfully extracted {len(tables_extracted)} tables")
                                    
                            except Exception as e:
                                debug_print(f"    Table detection/extraction failed: {str(e)[:100]}")
                                tables_extracted = []
                        
                        # Generate markdown with tables if found
                        if tables_extracted:
                            # Combine text and tables in markdown
                            markdown_content = table_json_generator.combine_with_page_content(
                                page_text if page_text else "",
                                tables_extracted,
                                page_number
                            )
                            
                            with open(markdown_file, "w", encoding="utf-8") as f:
                                f.write(markdown_content)
                            
                            # Collect table data for vector generation (v0.1.7)
                            if tables_extracted and 'all_extracted_tables' in locals():
                                for table in tables_extracted:
                                    all_extracted_tables.append({
                                        'page': page_number,
                                        'data': table,
                                        'metadata': {
                                            'extraction_method': table_method,
                                            'page_number': page_number
                                        }
                                    })
                            
                            # Save tables as JSON if requested
                            if save_table_json and tables_extracted:
                                json_dir = output_base / "tables"
                                json_dir.mkdir(exist_ok=True)
                                json_data = table_json_generator.generate_json(
                                    tables_extracted, 
                                    page_number,
                                    include_metadata=True
                                )
                                table_json_generator.save_to_file(
                                    json_data,
                                    json_dir,
                                    f"table_page_{page_number:03d}.json"
                                )
                            
                            debug_print(f"    Saved: {markdown_file.name} (with tables)")
                        else:
                            # Regular text page (we already have the text from step 1)
                            regular_pages += 1
                            
                            with open(markdown_file, "w", encoding="utf-8") as f:
                                f.write(f"# Page {page_number}\n\n")
                                if page_text:
                                    f.write(page_text)
                                else:
                                    f.write("[No text content available]")
                        
                        # Save checkpoint for page with or without tables
                        page_processing_time = time.time() - page_start_time
                        processing_state.mark_page_complete(
                            page_number=page_number,
                            is_network_diagram=False,
                            has_errors=False,
                            processing_time=page_processing_time,
                            has_tables=bool(tables_extracted)  # Add table tracking
                        )
                else:
                    # Fast mode or auto-detect disabled - just transcribe
                    regular_pages += 1
                    try:
                        text = retry_with_timeout(
                            transcribe_image,
                            args=(str(image_file),),
                            kwargs={"model": text_model},
                            timeout_seconds=timeout_seconds * 2,
                            max_retries=1,
                            fallback=lambda x, **kw: "[Transcription timed out]"
                        )
                    except Exception as e:
                        debug_print(f"\n    Page {page_number}: Transcription error: {str(e)[:100]}")
                        text = f"[Error transcribing page: {str(e)[:200]}]"
                    
                    # Store page text for context extraction
                    all_page_texts[page_number] = text
                    
                    with open(markdown_file, "w", encoding="utf-8") as f:
                        f.write(f"# Page {page_number}\n\n")
                        f.write(text)
                    
                    # Save checkpoint for text-only page
                    page_processing_time = time.time() - page_start_time
                    processing_state.mark_page_complete(
                        page_number=page_number,
                        is_network_diagram=False,
                        has_errors=False,
                        processing_time=page_processing_time
                    )
                
            except Exception as e:
                debug_print(f"  Error processing page {page_number}: {str(e)}")
                # Create error page
                markdown_file = markdown_dir / f"page_{page_number:03d}.md"
                with open(markdown_file, "w", encoding="utf-8") as f:
                    f.write(f"# Page {page_number}\n\n")
                    f.write(f"*Error processing this page: {str(e)}*\n")
                regular_pages += 1
            
            # Clean up image if not keeping them
            if not keep_images:
                image_file.unlink()
        
        # Calculate processing time
        processing_end_time = time.time()
        processing_duration = processing_end_time - processing_start_time
        processing_minutes = int(processing_duration // 60)
        processing_seconds = int(processing_duration % 60)
        processing_time_str = f"{processing_minutes}m {processing_seconds}s"
        
        # Prepare metrics for the footer
        processing_metrics = {
            'text_model': text_model,
            'network_model': diagram_model,
            'processing_time': processing_time_str,
            'mode': 'Hybrid (Auto-detect)' if auto_detect and not fast_mode else 'Fast (Text only)',
            'network_diagrams_processed': network_diagrams_found,
            'regular_pages': regular_pages,
            'confidence_threshold': confidence_threshold,
            'auto_detect': auto_detect,
            'use_icons': use_icons,
            'fast_extraction': fast_extraction,
            'timeout_seconds': timeout_seconds,
        }
        
        # Log summary
        logger.log_summary(
            total_pages=total_pages,
            successful_pages=total_pages,  # TODO: Track failed pages
            diagrams_found=network_diagrams_found,
            tables_found=len(all_extracted_tables)  # Fix: use count of tables, not the list itself
        )
        
        # Merge markdown files with PDF filename and metrics
        logger.log_step("Merging markdown files", f"Creating {pdf_path.name}.md")
        merged_file = merge_markdown_files_with_metrics(
            markdown_dir, 
            pdf_path.name,
            str(pdf_path),
            processing_metrics
        )
        logger.log_output_created("Merged markdown", str(merged_file))
        
        # Generate vector files if enabled (v0.1.7 - DEFAULT: enabled)
        vector_files_created = False
        if generate_vector:
            try:
                # Initialize vector generator
                vector_gen = VectorGenerator(
                    output_dir=str(output_base),
                    vector_format=vector_format,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    chunk_strategy=chunk_strategy,
                    array_strategy=array_strategy,
                    create_chunks=True,
                    include_extended_metadata=embedding_metadata,
                    embedding_model=embedding_model,
                    embedding_provider=embedding_provider
                )
                
                # Process the merged document to create vector files
                vector_result = vector_gen.process_merged_document(
                    merged_markdown_path=str(merged_file),
                    source_file=pdf_path.name,
                    page_count=total_pages,
                    tables=all_extracted_tables if 'all_extracted_tables' in locals() else None,
                    diagrams=all_network_diagrams if 'all_network_diagrams' in locals() else None
                )
                
                vector_files_created = True
                info_print(f"✅ Vector files generated: document-vector.md, chunks.jsonl")
                
            except Exception as e:
                debug_print(f"Warning: Vector generation failed: {str(e)}")
                # Continue without vector files - not critical
        
        # Generate summary report
        summary_file = output_base / "summary.md"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write("# Processing Summary\n\n")
            f.write(f"**Document**: {pdf_path.name}\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Processing Mode**: {'Hybrid (Auto-detect)' if auto_detect and not fast_mode else 'Fast (Text only)'}\n\n")
            f.write("## Statistics\n\n")
            f.write(f"- **Total Pages**: {total_pages}\n")
            f.write(f"- **Network Diagrams**: {network_diagrams_found}\n")
            f.write(f"- **Regular Text Pages**: {regular_pages}\n")
            if pages_with_mixed_content > 0:
                f.write(f"- **Mixed Content Pages**: {pages_with_mixed_content}\n")
            f.write(f"- **Model Used**: {model}\n")
            if auto_detect and not fast_mode:
                f.write(f"- **Detection Threshold**: {confidence_threshold}\n")
                f.write(f"- **Icons Enabled**: {use_icons}\n")
            f.write("\n")
            
            f.write("## Output Files\n\n")
            f.write(f"- [Merged Document](markdown/{merged_file.name}) - Complete document with all pages\n")
            f.write(f"- Individual pages in `markdown/` directory\n")
            
            # Add vector files information if generated (v0.1.7)
            if vector_files_created:
                f.write("\n### Vector Database Files (v0.1.7)\n\n")
                f.write("- [Vector-Optimized Document](markdown/document-vector.md) - Filtered content for embeddings\n")
                f.write("- [LanceDB Chunks](lancedb/chunks.jsonl) - Pre-chunked content ready for vector database\n")
                f.write("- [Schema](lancedb/schema.json) - LanceDB table schema\n")
                f.write("- [Metadata](lancedb/metadata.json) - Document and extraction metadata\n")
            
            if network_diagrams_found > 0:
                f.write("\n## Network Diagrams\n\n")
                f.write("The following pages contain network diagrams:\n\n")
                for md_file in sorted(markdown_dir.glob("page_*.md"), 
                                    key=lambda x: int(x.stem.split('_')[1])):
                    with open(md_file, 'r') as md_f:
                        first_line = md_f.readline().strip()
                        if "Network Diagram" in first_line:
                            page_num = md_file.stem.replace("page_", "").lstrip("0")
                            f.write(f"- [Page {page_num}](markdown/{md_file.name})\n")
        
        # Update the index file
        update_index_file(base_output_dir, pdf_path.name, md5_checksum, processing_time_str)
        
        # Clear checkpoint on successful completion
        checkpoint_manager.clear_checkpoint()
        
        # Show final output path (always shown)
        if quiet:
            # Ultra-minimal output for quiet mode
            always_print(f"{output_base}")
            always_print(f"{merged_file}")
        elif debug:
            # Detailed output for debug mode
            debug_print(f"\nProcessing complete!")
            debug_print(f"  Total pages processed: {total_pages}")
            if auto_detect and not fast_mode:
                debug_print(f"  Network diagrams found: {network_diagrams_found}")
                debug_print(f"  Regular text pages: {regular_pages}")
                if pages_with_mixed_content > 0:
                    debug_print(f"  Mixed content pages: {pages_with_mixed_content}")
            debug_print(f"  Output saved to: {output_base}")
            debug_print(f"  Merged document: {merged_file}")
        else:
            # Default mode - simple output
            always_print(f"\nOutput: {output_base}")
            always_print(f"Merged: {merged_file}")
        
    except Exception as e:
        logger.log_error(f"Fatal error during processing: {str(e)}", e)
        always_print(f"Error: {str(e)}")
        sys.exit(1)
    finally:
        # Always close the logger to ensure files are written
        if 'logger' in locals():
            logger.close()