"""Smart network diagram validator combining CV and LLM approaches."""

from typing import Tuple, Optional
from .quick_validator import QuickNetworkValidator
from ..output_utils import debug_print


class SmartNetworkValidator:
    """
    Intelligent validator that uses quick CV checks first,
    then falls back to LLM validation if needed.
    """
    
    def __init__(self, llm_validator=None):
        """
        Initialize smart validator.
        
        Args:
            llm_validator: Optional LLM-based validator for detailed checks
        """
        self.quick_validator = QuickNetworkValidator()
        self.llm_validator = llm_validator
    
    def validate(self, image_path: str, use_llm_if_uncertain: bool = True) -> Tuple[bool, float, str]:
        """
        Validate if image contains a network diagram.
        
        Args:
            image_path: Path to image to validate
            use_llm_if_uncertain: Use LLM for uncertain cases
            
        Returns:
            Tuple of (is_network_diagram, confidence, reason)
        """
        # First, try quick CV-based validation
        is_network_cv, confidence_cv, reason_cv = self.quick_validator.validate_region(image_path)
        
        # If CV is confident (>70% either way), trust it
        if confidence_cv > 0.7:
            debug_print(f"    Quick validation: Network diagram (confidence: {confidence_cv:.2f})")
            return True, confidence_cv, reason_cv
        elif confidence_cv < 0.3:
            debug_print(f"    Quick validation: NOT network diagram ({reason_cv})")
            return False, confidence_cv, reason_cv
        
        # For uncertain cases (30-70% confidence), use LLM if available
        if use_llm_if_uncertain and self.llm_validator:
            debug_print(f"    CV uncertain ({confidence_cv:.2f}), using LLM validation...")
            try:
                is_network_llm, confidence_llm = self.llm_validator(image_path)
                
                # Combine confidences (weighted average)
                combined_confidence = (confidence_cv * 0.3 + confidence_llm * 0.7)
                
                # Use LLM decision but with combined confidence
                reason = f"LLM: {confidence_llm:.2f}, CV: {confidence_cv:.2f}"
                return is_network_llm, combined_confidence, reason
                
            except Exception as e:
                debug_print(f"    LLM validation failed: {str(e)[:50]}")
                # Fall back to CV result
                return is_network_cv, confidence_cv, reason_cv
        
        # If no LLM available, use CV result
        return is_network_cv, confidence_cv, reason_cv
    
    def batch_validate(self, image_paths: list) -> list:
        """
        Validate multiple images efficiently.
        
        Args:
            image_paths: List of image paths to validate
            
        Returns:
            List of validation results
        """
        results = []
        
        for path in image_paths:
            is_network, confidence, reason = self.validate(path)
            results.append({
                "path": path,
                "is_network_diagram": is_network,
                "confidence": confidence,
                "reason": reason
            })
        
        return results
    
    def get_validation_summary(self, results: list) -> dict:
        """
        Generate summary of validation results.
        
        Args:
            results: List of validation results
            
        Returns:
            Summary statistics
        """
        total = len(results)
        network_diagrams = sum(1 for r in results if r["is_network_diagram"])
        avg_confidence = sum(r["confidence"] for r in results) / total if total > 0 else 0
        
        return {
            "total_regions": total,
            "network_diagrams": network_diagrams,
            "non_diagrams": total - network_diagrams,
            "average_confidence": avg_confidence,
            "filtered_out": total - network_diagrams
        }