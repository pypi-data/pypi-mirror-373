"""
Table validation module for ensuring data quality.
"""

import logging
from typing import Dict, Any, List, Optional
import json
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class TableValidator:
    """Validate extracted table data."""
    
    def __init__(self):
        """Initialize the validator."""
        self.validation_rules = {
            'simple': self._validate_simple_table,
            'complex': self._validate_complex_table,
            'multi_row': self._validate_multi_row_table
        }
    
    def validate(self, table_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate table data and return validation results.
        
        Args:
            table_data: Extracted table data
            
        Returns:
            Validation results with corrections
        """
        table_type = table_data.get('type', 'unknown')
        
        # Get appropriate validation function
        validate_func = self.validation_rules.get(
            table_type, 
            self._validate_generic
        )
        
        # Perform validation
        validation_result = validate_func(table_data)
        
        # Add overall validation score
        validation_result['overall_valid'] = validation_result.get('score', 0) >= 0.7
        
        return validation_result
    
    def _validate_simple_table(self, table_data: Dict) -> Dict[str, Any]:
        """Validate a simple table."""
        issues = []
        warnings = []
        score = 1.0
        
        # Check for headers
        headers = table_data.get('headers', [])
        if not headers:
            issues.append("No headers found")
            score -= 0.3
        elif len(headers) != len(set(headers)):
            warnings.append("Duplicate headers detected")
            score -= 0.1
        
        # Check data rows
        data = table_data.get('data', [])
        if not data:
            issues.append("No data rows found")
            score -= 0.5
        else:
            # Check consistency
            expected_cols = len(headers) if headers else 0
            for i, row in enumerate(data):
                if not isinstance(row, dict):
                    issues.append(f"Row {i} is not a dictionary")
                    score -= 0.1
                elif headers and len(row) != expected_cols:
                    warnings.append(f"Row {i} has inconsistent columns")
                    score -= 0.05
        
        # Validate data types
        if data and headers:
            column_types = self._infer_column_types(data, headers)
            table_data['inferred_types'] = column_types
        
        return {
            'score': max(0, score),
            'issues': issues,
            'warnings': warnings,
            'validated_data': table_data
        }
    
    def _validate_complex_table(self, table_data: Dict) -> Dict[str, Any]:
        """Validate a complex table with merged cells."""
        issues = []
        warnings = []
        score = 1.0
        
        structure = table_data.get('structure', {})
        
        # Check structure
        if not structure:
            issues.append("No structure information")
            score -= 0.3
        else:
            # Check merged cells
            merged = structure.get('merged_cells', [])
            for cell in merged:
                if not all(k in cell for k in ['row', 'col']):
                    issues.append("Invalid merged cell definition")
                    score -= 0.1
                    break
            
            # Check header levels
            headers = structure.get('headers', {})
            if not headers:
                warnings.append("No header hierarchy found")
                score -= 0.1
        
        # Check data
        data = table_data.get('data', [])
        if not data:
            issues.append("No data found")
            score -= 0.4
        
        return {
            'score': max(0, score),
            'issues': issues,
            'warnings': warnings,
            'validated_data': table_data
        }
    
    def _validate_multi_row_table(self, table_data: Dict) -> Dict[str, Any]:
        """Validate a multi-row field table."""
        issues = []
        warnings = []
        score = 1.0
        
        fields = table_data.get('fields', {})
        
        if not fields:
            issues.append("No fields found")
            score -= 0.5
        else:
            # Check field groups
            for group_name, group_data in fields.items():
                if not isinstance(group_data, dict):
                    issues.append(f"Field group '{group_name}' is not a dictionary")
                    score -= 0.2
                elif not group_data:
                    warnings.append(f"Field group '{group_name}' is empty")
                    score -= 0.1
        
        return {
            'score': max(0, score),
            'issues': issues,
            'warnings': warnings,
            'validated_data': table_data
        }
    
    def _validate_generic(self, table_data: Dict) -> Dict[str, Any]:
        """Generic validation for unknown table types."""
        issues = []
        score = 0.5  # Start with lower score for unknown types
        
        if not table_data.get('data') and not table_data.get('fields'):
            issues.append("No data or fields found")
            score = 0
        
        return {
            'score': score,
            'issues': issues,
            'warnings': [],
            'validated_data': table_data
        }
    
    def _infer_column_types(self, data: List[Dict], headers: List[str]) -> Dict[str, str]:
        """
        Infer data types for each column.
        
        Args:
            data: List of data rows
            headers: List of column headers
            
        Returns:
            Dictionary mapping headers to inferred types
        """
        column_types = {}
        
        for header in headers:
            values = [row.get(header) for row in data if row.get(header) is not None]
            
            if not values:
                column_types[header] = 'empty'
                continue
            
            # Sample values for type inference
            sample = values[:min(10, len(values))]
            
            # Check types
            types_found = set()
            for val in sample:
                if isinstance(val, bool):
                    types_found.add('boolean')
                elif isinstance(val, int):
                    types_found.add('integer')
                elif isinstance(val, float):
                    types_found.add('float')
                elif isinstance(val, str):
                    # Check for specific string patterns
                    if self._is_date(val):
                        types_found.add('date')
                    elif self._is_currency(val):
                        types_found.add('currency')
                    elif self._is_percentage(val):
                        types_found.add('percentage')
                    else:
                        types_found.add('string')
            
            # Determine predominant type
            if len(types_found) == 1:
                column_types[header] = list(types_found)[0]
            elif 'float' in types_found or 'integer' in types_found:
                column_types[header] = 'numeric'
            else:
                column_types[header] = 'mixed'
        
        return column_types
    
    def _is_date(self, value: str) -> bool:
        """Check if string value is a date."""
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # DD-MM-YYYY
        ]
        
        for pattern in date_patterns:
            if re.match(pattern, value):
                return True
        return False
    
    def _is_currency(self, value: str) -> bool:
        """Check if string value is currency."""
        currency_pattern = r'[$€£¥]\s*[\d,]+\.?\d*'
        return bool(re.match(currency_pattern, value))
    
    def _is_percentage(self, value: str) -> bool:
        """Check if string value is a percentage."""
        percentage_pattern = r'\d+\.?\d*\s*%'
        return bool(re.match(percentage_pattern, value))
    
    def auto_correct(self, table_data: Dict) -> Dict:
        """
        Attempt to auto-correct common issues in table data.
        
        Args:
            table_data: Table data to correct
            
        Returns:
            Corrected table data
        """
        corrected = table_data.copy()
        
        # Fix empty headers
        if 'headers' in corrected:
            headers = corrected['headers']
            for i, header in enumerate(headers):
                if not header or header == "":
                    headers[i] = f"Column_{i+1}"
        
        # Fix data consistency
        if 'data' in corrected and 'headers' in corrected:
            headers = corrected['headers']
            for row in corrected['data']:
                # Ensure all headers are present
                for header in headers:
                    if header not in row:
                        row[header] = None
        
        return corrected