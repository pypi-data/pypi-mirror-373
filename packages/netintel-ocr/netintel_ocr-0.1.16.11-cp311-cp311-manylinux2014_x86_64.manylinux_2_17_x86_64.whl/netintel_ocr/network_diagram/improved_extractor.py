"""Improved diagram extraction that handles whitespace and prevents cutoff."""

import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import pymupdf
import io
import base64
import requests
import json
from ..constants import OLLAMA_BASE_URL
from ..output_utils import debug_print


class ImprovedDiagramExtractor:
    """Extract diagram regions with better whitespace handling and no cutoff."""
    
    def __init__(
        self, 
        min_diagram_area: int = 5000,
        padding_percent: float = 0.05,  # 5% padding around detected regions
        edge_threshold_low: int = 30,   # Lower threshold for edge detection
        edge_threshold_high: int = 100, # Higher threshold for edge detection
        min_content_ratio: float = 0.02, # Minimum 2% non-white pixels
        validate_network_diagram: bool = True,  # Validate if content is network diagram
        validation_model: str = "llama3.2-vision",  # Model for validation
        validation_confidence_threshold: float = 0.5  # Minimum confidence to accept
    ):
        """
        Initialize the improved diagram extractor.
        
        Args:
            min_diagram_area: Minimum area in pixels to consider as a diagram
            padding_percent: Percentage of dimension to add as padding (0.05 = 5%)
            edge_threshold_low: Lower threshold for Canny edge detection
            edge_threshold_high: Upper threshold for Canny edge detection
            min_content_ratio: Minimum ratio of non-white pixels to consider region valid
        """
        self.min_diagram_area = min_diagram_area
        self.padding_percent = padding_percent
        self.edge_low = edge_threshold_low
        self.edge_high = edge_threshold_high
        self.min_content_ratio = min_content_ratio
        self.validate_network = validate_network_diagram
        self.validation_model = validation_model
        self.validation_threshold = validation_confidence_threshold
        self.base_url = OLLAMA_BASE_URL
    
    def extract_diagrams_from_pdf(
        self, 
        pdf_path: str, 
        page_num: int, 
        output_dir: str,
        scale_factor: float = 3.0  # Higher scale for better quality
    ) -> List[str]:
        """
        Extract all diagram regions from a specific PDF page with improved handling.
        
        Args:
            pdf_path: Path to PDF file
            page_num: Page number (1-based)
            output_dir: Directory to save extracted diagrams
            scale_factor: Scale factor for PDF rendering (higher = better quality)
            
        Returns:
            List of paths to extracted diagram images
        """
        # Open PDF and get page
        doc = pymupdf.open(pdf_path)
        page = doc[page_num - 1]  # Convert to 0-based
        
        # Get page as high-quality image
        pix = page.get_pixmap(matrix=pymupdf.Matrix(scale_factor, scale_factor))
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        
        # Convert to numpy array for OpenCV
        img_array = np.array(img)
        
        # Detect diagram regions with improved method
        regions = self.detect_diagram_regions_improved(img_array)
        
        # If no regions detected, try to extract the whole content area
        if not regions:
            debug_print("  No distinct regions found, attempting full content extraction...")
            regions = self.extract_content_area(img_array)
        
        # Extract and save each region
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        extracted_paths = []
        for i, (x, y, w, h) in enumerate(regions):
            # Calculate dynamic padding based on region size
            padding_x = int(w * self.padding_percent)
            padding_y = int(h * self.padding_percent)
            
            # Ensure we don't cut off content - expand generously
            x1 = max(0, x - padding_x)
            y1 = max(0, y - padding_y)
            x2 = min(img_array.shape[1], x + w + padding_x)
            y2 = min(img_array.shape[0], y + h + padding_y)
            
            # Extract region
            region_img = img_array[y1:y2, x1:x2]
            
            # Check if region has actual content
            if not self._has_meaningful_content(region_img):
                debug_print(f"  Skipping region {i+1}: insufficient content")
                continue
            
            # Save as temporary image for validation
            temp_path = output_dir / f"temp_region_{i+1}.png"
            Image.fromarray(region_img).save(temp_path, optimize=False, quality=100)
            
            # Validate if this is actually a network diagram
            if self.validate_network:
                is_network, confidence = self._validate_network_diagram(str(temp_path))
                if not is_network or confidence < self.validation_threshold:
                    debug_print(f"  Skipping region {i+1}: not a network diagram (confidence: {confidence:.2f})")
                    temp_path.unlink()  # Delete temp file
                    continue
                debug_print(f"  Region {i+1} validated as network diagram (confidence: {confidence:.2f})")
            
            # Rename to final path
            output_path = output_dir / f"page_{page_num:03d}_diagram_{i+1}.png"
            temp_path.rename(output_path)
            extracted_paths.append(str(output_path))
            
            debug_print(f"  Extracted verified diagram {i+1}: {x2-x1}x{y2-y1} pixels")
        
        doc.close()
        return extracted_paths
    
    def detect_diagram_regions_improved(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Improved detection that better handles whitespace and diagram boundaries.
        
        Args:
            image: Image as numpy array
            
        Returns:
            List of (x, y, width, height) tuples for detected regions
        """
        debug_print("  Detecting diagram regions (improved method)...")
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image.copy()
        
        image_height, image_width = gray.shape
        debug_print(f"  Image size: {image_width}x{image_height}")
        
        # Method 1: Find content boundaries first
        content_mask = self._create_content_mask(gray)
        
        # Method 2: Use morphological operations to connect nearby components
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 50))
        connected = cv2.morphologyEx(content_mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours on the connected components
        contours, _ = cv2.findContours(connected, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        debug_print(f"  Found {len(contours)} potential regions")
        
        regions = []
        for contour in contours:
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Calculate area
            area = w * h
            
            # More lenient filtering to avoid cutting off content
            if (area > self.min_diagram_area and 
                w > image_width * 0.1 and  # At least 10% of page width
                h > 30):  # Minimum height of 30 pixels
                
                # Expand region to include surrounding whitespace
                x, y, w, h = self._expand_to_whitespace(gray, x, y, w, h)
                
                regions.append((x, y, w, h))
                debug_print(f"    Region: {w}x{h} at ({x},{y})")
        
        # If we found regions, return them
        if regions:
            # Merge overlapping regions
            regions = self._merge_overlapping_regions(regions)
            debug_print(f"  {len(regions)} regions after merging")
            return sorted(regions, key=lambda r: r[1])  # Sort by y-coordinate
        
        # Fallback: Try edge-based detection
        debug_print("  Trying edge-based detection...")
        return self._edge_based_detection(gray)
    
    def _create_content_mask(self, gray: np.ndarray) -> np.ndarray:
        """Create a binary mask of content (non-white) areas."""
        # Threshold to find non-white pixels
        _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
        
        # Remove noise
        kernel_small = np.ones((3, 3), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_small)
        
        return cleaned
    
    def _expand_to_whitespace(
        self, 
        gray: np.ndarray, 
        x: int, 
        y: int, 
        w: int, 
        h: int,
        expansion_step: int = 10
    ) -> Tuple[int, int, int, int]:
        """
        Expand region boundaries until hitting significant whitespace.
        This ensures we don't cut off diagram edges.
        """
        height, width = gray.shape
        
        # Expand left
        new_x = x
        while new_x > 0:
            # Check if column has content
            col = gray[y:y+h, max(0, new_x-expansion_step):new_x]
            if col.size > 0 and np.mean(col) > 250:  # Mostly white
                break
            new_x = max(0, new_x - expansion_step)
        
        # Expand right
        new_right = x + w
        while new_right < width:
            # Check if column has content
            col = gray[y:y+h, new_right:min(width, new_right+expansion_step)]
            if col.size > 0 and np.mean(col) > 250:  # Mostly white
                break
            new_right = min(width, new_right + expansion_step)
        
        # Expand top
        new_y = y
        while new_y > 0:
            # Check if row has content
            row = gray[max(0, new_y-expansion_step):new_y, new_x:new_right]
            if row.size > 0 and np.mean(row) > 250:  # Mostly white
                break
            new_y = max(0, new_y - expansion_step)
        
        # Expand bottom
        new_bottom = y + h
        while new_bottom < height:
            # Check if row has content
            row = gray[new_bottom:min(height, new_bottom+expansion_step), new_x:new_right]
            if row.size > 0 and np.mean(row) > 250:  # Mostly white
                break
            new_bottom = min(height, new_bottom + expansion_step)
        
        return new_x, new_y, new_right - new_x, new_bottom - new_y
    
    def _edge_based_detection(self, gray: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Fallback edge-based detection method."""
        # Apply bilateral filter to reduce noise while keeping edges
        filtered = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Apply adaptive edge detection
        edges = cv2.Canny(filtered, self.edge_low, self.edge_high)
        
        # Dilate edges to connect components
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dilated = cv2.dilate(edges, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        regions = []
        image_height, image_width = gray.shape
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            
            if (area > self.min_diagram_area and 
                w > image_width * 0.15 and
                h > 40):
                regions.append((x, y, w, h))
        
        return regions
    
    def extract_content_area(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Extract the main content area of the page, removing only extreme whitespace.
        Used when no distinct regions are found.
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image.copy()
        
        # Find non-white pixels
        _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
        
        # Find overall content bounding box
        coords = cv2.findNonZero(binary)
        if coords is not None:
            x, y, w, h = cv2.boundingRect(coords)
            
            # Add generous padding
            padding = int(min(w, h) * 0.1)  # 10% padding
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(gray.shape[1] - x, w + 2 * padding)
            h = min(gray.shape[0] - y, h + 2 * padding)
            
            debug_print(f"  Extracting main content area: {w}x{h} at ({x},{y})")
            return [(x, y, w, h)]
        
        return []
    
    def _has_meaningful_content(self, region: np.ndarray) -> bool:
        """
        Check if a region has meaningful content (not just whitespace).
        """
        if len(region.shape) == 3:
            gray = cv2.cvtColor(region, cv2.COLOR_RGB2GRAY)
        else:
            gray = region.copy()
        
        # Calculate percentage of non-white pixels
        _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
        non_white_ratio = np.sum(binary > 0) / binary.size
        
        return non_white_ratio > self.min_content_ratio
    
    def _merge_overlapping_regions(
        self, 
        regions: List[Tuple[int, int, int, int]]
    ) -> List[Tuple[int, int, int, int]]:
        """
        Merge overlapping or nearby regions to avoid splitting diagrams.
        """
        if not regions:
            return regions
        
        merged = []
        regions = sorted(regions, key=lambda r: (r[1], r[0]))  # Sort by y, then x
        
        current = list(regions[0])
        for next_region in regions[1:]:
            x1, y1, w1, h1 = current
            x2, y2, w2, h2 = next_region
            
            # Check for overlap or proximity (within 50 pixels)
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
    
    def _validate_network_diagram(self, image_path: str) -> Tuple[bool, float]:
        """
        Validate if an extracted region is actually a network diagram.
        
        Args:
            image_path: Path to the extracted region image
            
        Returns:
            Tuple of (is_network_diagram, confidence_score)
        """
        try:
            # Read and encode the image
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")
            
            # Quick validation prompt
            validation_prompt = """Look at this image and determine if it's a network diagram.

A network diagram should have:
- Network components (routers, switches, servers, firewalls, etc.)
- Connections between components (lines, arrows)
- Network topology structure

NOT a network diagram:
- Text blocks or paragraphs
- Tables or spreadsheets
- Code snippets
- Regular flowcharts without network components
- UI mockups or screenshots
- Graphs or charts (bar, line, pie)

Respond with JSON:
{
  "is_network_diagram": true/false,
  "confidence": 0.0-1.0,
  "reason": "brief explanation"
}"""
            
            payload = {
                "model": self.validation_model,
                "prompt": validation_prompt,
                "stream": False,
                "images": [image_data],
                "options": {
                    "temperature": 0.1,
                    "num_predict": 200
                }
            }
            
            # Make quick validation call
            response = requests.post(
                f"{self.base_url}/generate",
                json=payload,
                timeout=10  # Quick timeout for validation
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                
                # Parse JSON response
                try:
                    # Try to extract JSON
                    if "{" in response_text and "}" in response_text:
                        start = response_text.find("{")
                        end = response_text.rfind("}") + 1
                        json_str = response_text[start:end]
                        parsed = json.loads(json_str)
                        
                        is_network = parsed.get("is_network_diagram", False)
                        confidence = float(parsed.get("confidence", 0.0))
                        reason = parsed.get("reason", "")
                        
                        if reason:
                            debug_print(f"    Validation: {reason}")
                        
                        return is_network, confidence
                except:
                    # Fallback: look for keywords
                    response_lower = response_text.lower()
                    if "not a network" in response_lower or "text" in response_lower or "table" in response_lower:
                        return False, 0.0
                    elif "network diagram" in response_lower or "topology" in response_lower:
                        return True, 0.7
            
            # If validation fails, be conservative
            return False, 0.0
            
        except Exception as e:
            debug_print(f"    Validation error: {str(e)[:100]}")
            # If we can't validate, assume it might be valid
            return True, 0.5  # Medium confidence as fallback