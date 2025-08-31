"""Enhanced processor that handles multiple diagrams per page."""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import time
import concurrent.futures
from functools import partial
from .output_utils import debug_print

from .network_diagram.diagram_extractor import DiagramRegionExtractor
try:
    from .network_diagram.improved_extractor import ImprovedDiagramExtractor
    USE_IMPROVED_EXTRACTOR = True
except ImportError:
    USE_IMPROVED_EXTRACTOR = False
from .network_diagram.fast_extractor import FastExtractor
from .network_diagram.mermaid_generator import MermaidGenerator
from .network_diagram.robust_validator import RobustMermaidValidator


class MultiDiagramProcessor:
    """Process pages with multiple network diagrams."""
    
    def __init__(self, model: str = "llama3.2-vision", timeout: int = 60, use_improved: bool = True):
        """Initialize the multi-diagram processor."""
        self.model = model
        self.timeout = timeout
        
        # Use improved extractor if available and requested
        if use_improved and USE_IMPROVED_EXTRACTOR:
            self.extractor = ImprovedDiagramExtractor(
                min_diagram_area=5000,
                padding_percent=0.08,  # 8% padding to avoid cutoff
                edge_threshold_low=30,
                edge_threshold_high=100,
                min_content_ratio=0.02,
                validate_network_diagram=True,  # Enable validation
                validation_model=model,
                validation_confidence_threshold=0.4  # 40% confidence minimum
            )
            print("  Using ImprovedDiagramExtractor with validation and whitespace handling")
        else:
            self.extractor = DiagramRegionExtractor(min_diagram_area=5000, padding=20)
        
        self.component_extractor = FastExtractor(model, timeout=timeout, use_improved_prompts=True)
        self.mermaid_generator = MermaidGenerator(model)
        self.validator = RobustMermaidValidator()
    
    def process_page_with_multiple_diagrams(
        self, 
        pdf_path: str, 
        page_num: int, 
        image_path: str,
        output_dir: str
    ) -> Dict[str, Any]:
        """
        Process a page that may contain multiple network diagrams.
        
        Args:
            pdf_path: Path to PDF file
            page_num: Page number (1-based)
            image_path: Path to page image
            output_dir: Directory for outputs
            
        Returns:
            Processing results with multiple diagrams
        """
        print(f"\nPage {page_num}: Extracting individual diagram regions...")
        
        # Create directory for extracted diagrams
        diagram_dir = Path(output_dir) / "extracted_diagrams" / f"page_{page_num:03d}"
        diagram_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract diagram regions with appropriate method
        try:
            if hasattr(self.extractor, 'extract_diagrams_from_pdf'):
                # Call with scale_factor if using improved extractor
                if USE_IMPROVED_EXTRACTOR and isinstance(self.extractor, ImprovedDiagramExtractor):
                    extracted_paths = self.extractor.extract_diagrams_from_pdf(
                        pdf_path,
                        page_num,
                        str(diagram_dir),
                        scale_factor=3.0  # Higher quality extraction
                    )
                else:
                    extracted_paths = self.extractor.extract_diagrams_from_pdf(
                        pdf_path,
                        page_num,
                        str(diagram_dir)
                    )
            else:
                print("  Error: Extractor missing extract_diagrams_from_pdf method")
                extracted_paths = []
        except Exception as e:
            print(f"  Error extracting diagrams: {e}")
            return {
                "page": page_num,
                "error": str(e),
                "diagrams": []
            }
        
        if not extracted_paths:
            debug_print(f"  No diagram regions detected")
            return {
                "page": page_num,
                "diagrams": [],
                "message": "No diagram regions detected"
            }
        
        debug_print(f"  Found {len(extracted_paths)} diagram region(s)")
        
        # Process each extracted diagram
        diagrams = []
        successful = 0
        
        for i, diagram_path in enumerate(extracted_paths, 1):
            debug_print(f"\n  Processing diagram {i}/{len(extracted_paths)}...")
            
            result = self._process_single_diagram(diagram_path, i)
            
            if result.get("extraction_successful"):
                successful += 1
                debug_print(f"    ✓ Successfully extracted {len(result.get('components', []))} components")
            else:
                debug_print(f"    ✗ Extraction failed: {result.get('error', 'Unknown error')}")
            
            diagrams.append(result)
        
        debug_print(f"\nPage {page_num}: Processed {successful}/{len(extracted_paths)} diagrams successfully")
        
        return {
            "page": page_num,
            "total_diagrams": len(extracted_paths),
            "successful_extractions": successful,
            "diagrams": diagrams
        }
    
    def _process_single_diagram(self, diagram_path: str, diagram_num: int) -> Dict[str, Any]:
        """Process a single extracted diagram with timeout enforcement."""
        try:
            # Use ThreadPoolExecutor for timeout enforcement
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                # Submit extraction task
                future = executor.submit(self._extract_with_timeout, diagram_path)
                
                try:
                    # Wait for result with timeout
                    extraction = future.result(timeout=self.timeout)
                except concurrent.futures.TimeoutError:
                    debug_print(f"    ✗ Extraction timed out after {self.timeout}s")
                    return {
                        "diagram_number": diagram_num,
                        "diagram_path": diagram_path,
                        "extraction_successful": False,
                        "error": f"Timeout after {self.timeout} seconds"
                    }
            
            if not extraction.get("extraction_successful"):
                return {
                    "diagram_number": diagram_num,
                    "diagram_path": diagram_path,
                    "extraction_successful": False,
                    "error": extraction.get("error", "Extraction failed")
                }
            
            # Generate Mermaid (with timeout)
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self.mermaid_generator.generate, extraction)
                try:
                    mermaid_code = future.result(timeout=min(10, self.timeout // 2))
                except concurrent.futures.TimeoutError:
                    debug_print(f"    Mermaid generation timed out, using fallback")
                    mermaid_code = self._generate_fallback_mermaid(extraction)
            
            # Validate and fix Mermaid
            if mermaid_code:
                is_valid, fixed_code, errors = self.validator.validate_and_fix(mermaid_code)
                if not is_valid and fixed_code:
                    debug_print(f"    Fixed {len(errors)} Mermaid syntax issues")
                    mermaid_code = fixed_code
            
            return {
                "diagram_number": diagram_num,
                "diagram_path": diagram_path,
                "extraction_successful": True,
                "components": extraction.get("components", []),
                "connections": extraction.get("connections", []),
                "mermaid": mermaid_code
            }
            
        except Exception as e:
            return {
                "diagram_number": diagram_num,
                "diagram_path": diagram_path,
                "extraction_successful": False,
                "error": str(e)
            }
    
    def _extract_with_timeout(self, diagram_path: str) -> Dict[str, Any]:
        """Wrapper for extraction to use with executor."""
        return self.component_extractor.extract(diagram_path)
    
    def _generate_fallback_mermaid(self, extraction: Dict[str, Any]) -> str:
        """Generate simple Mermaid without LLM."""
        components = extraction.get("components", [])
        connections = extraction.get("connections", [])
        
        if not components:
            return "graph TB\n    %% No components detected"
        
        lines = ["graph TB"]
        lines.append("    %% Network Components")
        
        # Add components
        for comp in components:
            comp_id = comp.get("id", "comp")
            comp_label = comp.get("label", comp_id)
            comp_type = comp.get("type", "unknown")
            
            if comp_type == "router":
                lines.append(f"    {comp_id}([{comp_label}])")
            elif comp_type == "database":
                lines.append(f"    {comp_id}[({comp_label})]")
            else:
                lines.append(f"    {comp_id}[{comp_label}]")
        
        # Add connections
        if connections:
            lines.append("    %% Connections")
            for conn in connections:
                from_id = conn.get("from", "")
                to_id = conn.get("to", "")
                if from_id and to_id:
                    lines.append(f"    {from_id} --> {to_id}")
        
        return "\n".join(lines)
    
    def generate_markdown_for_multi_diagrams(
        self, 
        page_results: Dict[str, Any],
        text_content: Optional[str] = None
    ) -> str:
        """Generate markdown for a page with multiple diagrams."""
        lines = [f"# Page {page_results['page']}\n"]
        
        if page_results.get("error"):
            lines.append(f"*Error processing page: {page_results['error']}*\n")
            if text_content:
                lines.append("\n## Page Content\n")
                lines.append(text_content)
            return "\n".join(lines)
        
        total = page_results.get("total_diagrams", 0)
        successful = page_results.get("successful_extractions", 0)
        
        if total == 0:
            lines.append("*No network diagrams detected on this page.*\n")
        else:
            lines.append(f"*Found {total} network diagram(s). Successfully processed {successful}.*\n")
        
        # Add each diagram
        for diagram in page_results.get("diagrams", []):
            lines.append(f"\n## Network Diagram {diagram['diagram_number']}\n")
            
            if diagram.get("extraction_successful"):
                # Add statistics
                n_components = len(diagram.get("components", []))
                n_connections = len(diagram.get("connections", []))
                lines.append(f"*Components: {n_components}, Connections: {n_connections}*\n")
                
                # Add Mermaid diagram
                if diagram.get("mermaid"):
                    lines.append("\n```mermaid")
                    lines.append(diagram["mermaid"])
                    lines.append("```\n")
                
                # Add component list
                if diagram.get("components"):
                    lines.append("\n### Components\n")
                    for comp in diagram["components"]:
                        comp_type = comp.get("type", "unknown")
                        label = comp.get("label", comp.get("id", "unnamed"))
                        lines.append(f"- **{label}** ({comp_type})")
                
                # Add connections
                if diagram.get("connections"):
                    lines.append("\n### Connections\n")
                    for conn in diagram["connections"]:
                        from_label = conn.get("from", "?")
                        to_label = conn.get("to", "?")
                        lines.append(f"- {from_label} → {to_label}")
            else:
                lines.append(f"*Failed to extract components: {diagram.get('error', 'Unknown error')}*\n")
        
        # Add text content if available
        if text_content:
            lines.append("\n## Page Text Content\n")
            lines.append(text_content)
        
        return "\n".join(lines)