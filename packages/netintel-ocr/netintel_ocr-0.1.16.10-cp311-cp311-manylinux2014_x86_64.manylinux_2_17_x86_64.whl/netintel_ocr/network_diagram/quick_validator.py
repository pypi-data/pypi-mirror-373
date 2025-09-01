"""Quick network diagram validator using visual and structural cues."""

import cv2
import numpy as np
from typing import Tuple, Dict, Any
from PIL import Image


class QuickNetworkValidator:
    """Fast validation of network diagrams using computer vision."""
    
    def __init__(self):
        """Initialize the quick validator."""
        pass
    
    def validate_region(self, image_path: str) -> Tuple[bool, float, str]:
        """
        Quickly validate if an image region contains a network diagram.
        Uses computer vision heuristics for fast checking.
        
        Args:
            image_path: Path to image to validate
            
        Returns:
            Tuple of (is_network_diagram, confidence, reason)
        """
        try:
            # Load image
            img = Image.open(image_path)
            img_array = np.array(img)
            
            # Convert to grayscale
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            height, width = gray.shape
            
            # Run multiple checks
            checks = {}
            
            # 1. Check for lines and connections (network diagrams have many lines)
            checks['has_lines'] = self._check_for_lines(gray)
            
            # 2. Check for shapes (boxes, circles common in network diagrams)
            checks['has_shapes'] = self._check_for_shapes(gray)
            
            # 3. Check text density (network diagrams have moderate text, not dense)
            checks['text_density'] = self._check_text_density(gray)
            
            # 4. Check for network-like structure
            checks['has_structure'] = self._check_network_structure(gray)
            
            # 5. Check aspect ratio (network diagrams usually wider than tall)
            checks['good_aspect'] = self._check_aspect_ratio(width, height)
            
            # 6. Check for table-like patterns (to exclude tables)
            checks['not_table'] = not self._check_if_table(gray)
            
            # 7. Check for code/text blocks (to exclude code snippets)
            checks['not_text_block'] = not self._check_if_text_block(gray)
            
            # Calculate confidence based on checks
            positive_checks = sum([
                checks['has_lines'] * 0.25,
                checks['has_shapes'] * 0.20,
                checks['text_density'] * 0.15,
                checks['has_structure'] * 0.20,
                checks['good_aspect'] * 0.05,
                checks['not_table'] * 0.10,
                checks['not_text_block'] * 0.05
            ])
            
            # Determine if it's a network diagram
            is_network = positive_checks > 0.5
            
            # Generate reason
            if not checks['not_table']:
                reason = "Appears to be a table"
            elif not checks['not_text_block']:
                reason = "Appears to be a text block or code"
            elif not checks['has_lines']:
                reason = "No connection lines detected"
            elif not checks['has_shapes']:
                reason = "No network component shapes detected"
            elif is_network:
                reason = "Has network diagram characteristics"
            else:
                reason = "Insufficient network diagram features"
            
            return is_network, positive_checks, reason
            
        except Exception as e:
            return False, 0.0, f"Validation error: {str(e)[:50]}"
    
    def _check_for_lines(self, gray: np.ndarray) -> bool:
        """Check if image has lines (connections)."""
        edges = cv2.Canny(gray, 50, 150)
        
        # Detect lines using HoughLines
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi/180,
            threshold=50,
            minLineLength=30,
            maxLineGap=10
        )
        
        if lines is not None:
            # Network diagrams typically have 5+ lines
            return len(lines) >= 5
        return False
    
    def _check_for_shapes(self, gray: np.ndarray) -> bool:
        """Check for rectangular and circular shapes."""
        edges = cv2.Canny(gray, 30, 100)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        shape_count = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500:  # Significant size
                # Approximate polygon
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Count as shape if it has 3-8 vertices (triangle to octagon)
                if 3 <= len(approx) <= 8:
                    shape_count += 1
        
        # Network diagrams typically have multiple shapes
        return shape_count >= 3
    
    def _check_text_density(self, gray: np.ndarray) -> bool:
        """Check if text density is appropriate for network diagram."""
        # Binarize
        _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        
        # Calculate text density
        text_pixels = np.sum(binary > 0)
        total_pixels = binary.size
        density = text_pixels / total_pixels
        
        # Network diagrams have moderate text (5-30%)
        return 0.05 <= density <= 0.30
    
    def _check_network_structure(self, gray: np.ndarray) -> bool:
        """Check for network-like structural patterns."""
        # Look for hierarchical or interconnected structure
        edges = cv2.Canny(gray, 50, 150)
        
        # Check for multiple connection points
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        dilated = cv2.dilate(edges, kernel, iterations=2)
        
        # Find connected components
        num_labels, labels = cv2.connectedComponents(dilated)
        
        # Network diagrams have multiple connected components
        return 3 <= num_labels <= 50  # Not too few, not too many
    
    def _check_aspect_ratio(self, width: int, height: int) -> bool:
        """Check if aspect ratio is typical for network diagrams."""
        if height == 0:
            return False
        
        aspect = width / height
        # Network diagrams are often wider than tall (0.8 to 3.0)
        return 0.8 <= aspect <= 3.0
    
    def _check_if_table(self, gray: np.ndarray) -> bool:
        """Check if the image looks like a table."""
        edges = cv2.Canny(gray, 50, 150)
        
        # Detect horizontal and vertical lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        
        horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
        vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)
        
        # Count lines
        h_lines = cv2.HoughLinesP(horizontal_lines, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
        v_lines = cv2.HoughLinesP(vertical_lines, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
        
        h_count = len(h_lines) if h_lines is not None else 0
        v_count = len(v_lines) if v_lines is not None else 0
        
        # Tables have many regular horizontal and vertical lines
        return h_count > 3 and v_count > 3 and abs(h_count - v_count) < 5
    
    def _check_if_text_block(self, gray: np.ndarray) -> bool:
        """Check if the image is primarily a text block or code."""
        # Binarize
        _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        
        # Horizontal projection (sum pixels in each row)
        h_projection = np.sum(binary, axis=1)
        
        # Count text lines (rows with significant content)
        text_lines = np.sum(h_projection > gray.shape[1] * 0.1)
        
        # Calculate line regularity
        if text_lines > 10:
            # Check if lines are evenly spaced (characteristic of text/code)
            non_zero_rows = np.where(h_projection > gray.shape[1] * 0.1)[0]
            if len(non_zero_rows) > 1:
                gaps = np.diff(non_zero_rows)
                gap_std = np.std(gaps)
                gap_mean = np.mean(gaps)
                
                # Text blocks have regular line spacing
                if gap_mean > 0:
                    regularity = gap_std / gap_mean
                    return regularity < 0.5 and text_lines > 15
        
        return False