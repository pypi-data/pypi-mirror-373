"""Extract individual network diagrams from PDF pages as separate images."""

import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import pymupdf
import io
from ..output_utils import debug_print


class DiagramRegionExtractor:
    """Extract individual diagram regions from PDF pages."""
    
    def __init__(self, min_diagram_area: int = 10000, padding: int = 10):
        """
        Initialize the diagram extractor.
        
        Args:
            min_diagram_area: Minimum area in pixels to consider as a diagram
            padding: Pixels to add around detected regions
        """
        self.min_diagram_area = min_diagram_area
        self.padding = padding
    
    def extract_diagrams_from_pdf(self, pdf_path: str, page_num: int, output_dir: str) -> List[str]:
        """
        Extract all diagram regions from a specific PDF page.
        
        Args:
            pdf_path: Path to PDF file
            page_num: Page number (1-based)
            output_dir: Directory to save extracted diagrams
            
        Returns:
            List of paths to extracted diagram images
        """
        # Open PDF and get page
        doc = pymupdf.open(pdf_path)
        page = doc[page_num - 1]  # Convert to 0-based
        
        # Get page as image
        pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))  # 2x scale for better quality
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        
        # Convert to numpy array for OpenCV
        img_array = np.array(img)
        
        # Detect diagram regions
        regions = self.detect_diagram_regions(img_array)
        
        # Extract and save each region
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        extracted_paths = []
        for i, (x, y, w, h) in enumerate(regions):
            # Extract region with padding
            x1 = max(0, x - self.padding)
            y1 = max(0, y - self.padding)
            x2 = min(img_array.shape[1], x + w + self.padding)
            y2 = min(img_array.shape[0], y + h + self.padding)
            
            region_img = img_array[y1:y2, x1:x2]
            
            # Save as image
            output_path = output_dir / f"page_{page_num:03d}_diagram_{i+1}.png"
            Image.fromarray(region_img).save(output_path)
            extracted_paths.append(str(output_path))
            
            debug_print(f"  Extracted diagram {i+1}: {w}x{h} pixels at ({x}, {y})")
        
        doc.close()
        return extracted_paths
    
    def detect_diagram_regions(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect potential diagram regions in an image.
        
        Args:
            image: Image as numpy array
            
        Returns:
            List of (x, y, width, height) tuples for detected regions
        """
        debug_print("  Detecting diagram regions...")
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image.copy()
        
        image_height, image_width = gray.shape
        debug_print(f"  Image size: {image_width}x{image_height}")
        
        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        debug_print(f"  Found {len(contours)} contours")
        
        # Filter and identify potential diagram regions
        regions = []
        
        for contour in contours:
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Calculate area
            area = w * h
            
            # Filter criteria for diagrams
            if (area > self.min_diagram_area and 
                w > image_width * 0.2 and  # At least 20% of page width
                h > 50 and  # Minimum height
                w / h > 0.3 and w / h < 5):  # Reasonable aspect ratio
                
                # Check if this region contains enough content
                region = gray[y:y+h, x:x+w]
                if self._has_significant_content(region):
                    regions.append((x, y, w, h))
                    debug_print(f"    Candidate region: {w}x{h} at ({x},{y}), area={area}")
        
        debug_print(f"  {len(regions)} regions before merging")
        
        # Merge overlapping regions
        regions = self._merge_overlapping_regions(regions)
        
        debug_print(f"  {len(regions)} regions after merging")
        
        # Sort by y-coordinate (top to bottom)
        regions.sort(key=lambda r: r[1])
        
        return regions
    
    def _has_significant_content(self, region: np.ndarray, threshold: float = 0.05) -> bool:
        """
        Check if a region has significant content (not mostly white).
        
        Args:
            region: Image region to check
            threshold: Minimum ratio of non-white pixels
            
        Returns:
            True if region has significant content
        """
        # Calculate percentage of non-white pixels
        _, binary = cv2.threshold(region, 240, 255, cv2.THRESH_BINARY_INV)
        non_white_ratio = np.sum(binary > 0) / binary.size
        
        return non_white_ratio > threshold
    
    def _merge_overlapping_regions(self, regions: List[Tuple[int, int, int, int]], 
                                   overlap_threshold: float = 0.1) -> List[Tuple[int, int, int, int]]:
        """
        Merge overlapping or nearby regions.
        
        Args:
            regions: List of (x, y, w, h) tuples
            overlap_threshold: Minimum overlap ratio to merge
            
        Returns:
            Merged regions
        """
        if not regions:
            return regions
        
        merged = []
        regions = sorted(regions, key=lambda r: (r[1], r[0]))  # Sort by y, then x
        
        current = list(regions[0])
        for next_region in regions[1:]:
            x1, y1, w1, h1 = current
            x2, y2, w2, h2 = next_region
            
            # Check for overlap or proximity
            if (self._regions_overlap(current, next_region) or 
                self._regions_nearby(current, next_region, threshold=50)):
                # Merge regions
                x_min = min(x1, x2)
                y_min = min(y1, y2)
                x_max = max(x1 + w1, x2 + w2)
                y_max = max(y1 + h1, y2 + h2)
                current = [x_min, y_min, x_max - x_min, y_max - y_min]
            else:
                merged.append(tuple(current))
                current = list(next_region)
        
        merged.append(tuple(current))
        return merged
    
    def _regions_overlap(self, r1: Tuple[int, int, int, int], 
                        r2: Tuple[int, int, int, int]) -> bool:
        """Check if two regions overlap."""
        x1, y1, w1, h1 = r1
        x2, y2, w2, h2 = r2
        
        return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)
    
    def _regions_nearby(self, r1: Tuple[int, int, int, int], 
                       r2: Tuple[int, int, int, int], 
                       threshold: int = 50) -> bool:
        """Check if two regions are nearby."""
        x1, y1, w1, h1 = r1
        x2, y2, w2, h2 = r2
        
        # Calculate minimum distance between regions
        x_dist = max(0, max(x1, x2) - min(x1 + w1, x2 + w2))
        y_dist = max(0, max(y1, y2) - min(y1 + h1, y2 + h2))
        
        return x_dist < threshold and y_dist < threshold


class DiagramProcessor:
    """Process extracted diagram images with LLM."""
    
    def __init__(self, model: str = "nanonets-ocr-s:latest"):
        self.model = model
    
    def process_extracted_diagrams(self, diagram_paths: List[str], timeout: int = 60) -> List[Dict[str, Any]]:
        """
        Process each extracted diagram individually.
        
        Args:
            diagram_paths: List of paths to diagram images
            timeout: Timeout for each extraction
            
        Returns:
            List of extraction results
        """
        try:
            from .fast_extractor import FastExtractor
            from .mermaid_generator import MermaidGenerator
        except ImportError:
            from .extractor import ComponentExtractor as FastExtractor
            from .mermaid_generator import MermaidGenerator
        
        extractor = FastExtractor(self.model, timeout=timeout)
        generator = MermaidGenerator(self.model)
        
        results = []
        
        for i, diagram_path in enumerate(diagram_paths, 1):
            debug_print(f"\nProcessing diagram {i}/{len(diagram_paths)}: {Path(diagram_path).name}")
            
            # For extracted regions, assume they are network diagrams
            # Skip detection step to save time
            debug_print(f"  Extracting components...")
            
            try:
                # Extract components
                extraction = extractor.extract(diagram_path)
                
                if extraction.get("extraction_successful"):
                    debug_print(f"  Extracted {len(extraction.get('components', []))} components")
                    
                    # Generate Mermaid
                    mermaid_code = generator.generate(extraction)
                    
                    result = {
                        "diagram_path": diagram_path,
                        "diagram_number": i,
                        "extraction": extraction,
                        "mermaid": mermaid_code
                    }
                else:
                    result = {
                        "diagram_path": diagram_path,
                        "diagram_number": i,
                        "extraction": extraction,
                        "mermaid": None,
                        "error": "Extraction failed"
                    }
            except Exception as e:
                debug_print(f"  Error: {e}")
                result = {
                    "diagram_path": diagram_path,
                    "diagram_number": i,
                    "error": str(e)
                }
            
            results.append(result)
        
        return results