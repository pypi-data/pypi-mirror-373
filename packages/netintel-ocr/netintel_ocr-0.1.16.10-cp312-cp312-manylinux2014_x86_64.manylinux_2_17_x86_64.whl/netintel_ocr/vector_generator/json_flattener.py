"""
JSON Flattener for Vector Database Integration

Flattens nested JSON structures (tables, network diagrams) for 
efficient vector database ingestion, especially optimized for LanceDB.
"""

from typing import Any, Dict, List, Union
import json


class JSONFlattener:
    """Flatten nested JSON structures for vector database ingestion."""
    
    def __init__(self, array_strategy: str = "separate_rows", 
                 array_delimiter: str = "|",
                 max_depth: int = 10):
        """
        Initialize JSON flattener.
        
        Args:
            array_strategy: How to handle arrays - "separate_rows", "concatenate", "serialize"
            array_delimiter: Delimiter for concatenated arrays
            max_depth: Maximum nesting depth to flatten
        """
        self.array_strategy = array_strategy
        self.array_delimiter = array_delimiter
        self.max_depth = max_depth
    
    def flatten(self, data: Union[Dict, List], parent_key: str = '', sep: str = '_') -> Union[Dict, List[Dict]]:
        """
        Flatten a nested dictionary or list structure.
        
        Args:
            data: Data to flatten
            parent_key: Parent key for nested items
            sep: Separator between parent and child keys
            
        Returns:
            Flattened dictionary or list of dictionaries
        """
        if isinstance(data, list):
            return self._flatten_list(data, parent_key, sep)
        elif isinstance(data, dict):
            return self._flatten_dict(data, parent_key, sep)
        else:
            return {parent_key: data} if parent_key else data
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """Flatten a nested dictionary."""
        items = []
        
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                # Recursively flatten nested dictionaries
                if self._get_depth(v) < self.max_depth:
                    items.extend(self._flatten_dict(v, new_key, sep).items())
                else:
                    # Max depth reached, serialize as string
                    items.append((new_key, json.dumps(v)))
            
            elif isinstance(v, list):
                # Handle arrays based on strategy
                flattened_array = self._flatten_array(v, new_key, sep)
                if isinstance(flattened_array, dict):
                    items.extend(flattened_array.items())
                else:
                    items.append((new_key, flattened_array))
            
            else:
                # Leaf value
                items.append((new_key, v))
        
        return dict(items)
    
    def _flatten_list(self, lst: List, parent_key: str = '', sep: str = '_') -> List[Dict]:
        """Flatten a list into separate rows (for array_strategy='separate_rows')."""
        if self.array_strategy == "separate_rows":
            flattened_rows = []
            for i, item in enumerate(lst):
                if isinstance(item, dict):
                    flattened = self._flatten_dict(item, '', sep)
                    if parent_key:
                        flattened = {f"{parent_key}{sep}{k}": v for k, v in flattened.items()}
                    flattened[f"{parent_key}_index" if parent_key else "index"] = i
                    flattened_rows.append(flattened)
                else:
                    row = {f"{parent_key}_value" if parent_key else "value": item,
                           f"{parent_key}_index" if parent_key else "index": i}
                    flattened_rows.append(row)
            return flattened_rows
        else:
            # For other strategies, return as single flattened structure
            return self._flatten_array(lst, parent_key, sep)
    
    def _flatten_array(self, arr: List, parent_key: str, sep: str) -> Union[Dict, str, List]:
        """
        Flatten an array based on the configured strategy.
        
        Args:
            arr: Array to flatten
            parent_key: Parent key for the array
            sep: Separator for keys
            
        Returns:
            Flattened representation of the array
        """
        if not arr:
            return {parent_key: None} if parent_key else None
        
        if self.array_strategy == "separate_rows":
            # Create separate keys for each array element
            result = {}
            for i, item in enumerate(arr):
                key = f"{parent_key}{sep}{i}"
                if isinstance(item, dict):
                    flattened = self._flatten_dict(item, key, sep)
                    result.update(flattened)
                elif isinstance(item, list):
                    flattened = self._flatten_array(item, key, sep)
                    if isinstance(flattened, dict):
                        result.update(flattened)
                    else:
                        result[key] = flattened
                else:
                    result[key] = item
            return result
        
        elif self.array_strategy == "concatenate":
            # Concatenate array values with delimiter
            if all(isinstance(item, (str, int, float)) for item in arr):
                return self.array_delimiter.join(str(item) for item in arr)
            else:
                # For complex items, serialize
                return json.dumps(arr)
        
        elif self.array_strategy == "serialize":
            # Always serialize arrays as JSON strings
            return json.dumps(arr)
        
        else:
            # Default: keep as list
            return arr
    
    def _get_depth(self, d: Any, current_depth: int = 0) -> int:
        """Calculate the depth of a nested structure."""
        if not isinstance(d, (dict, list)):
            return current_depth
        
        if isinstance(d, dict):
            if not d:
                return current_depth
            return max(self._get_depth(v, current_depth + 1) for v in d.values())
        
        if isinstance(d, list):
            if not d:
                return current_depth
            return max(self._get_depth(item, current_depth + 1) for item in d)
    
    def flatten_table(self, table_data: Dict) -> Dict:
        """
        Flatten table data specifically for vector databases.
        
        Args:
            table_data: Table data with potential nesting
            
        Returns:
            Flattened table structure
        """
        # Handle common table structures
        if 'headers' in table_data and 'rows' in table_data:
            # Standard table with headers and rows
            flattened_rows = []
            headers = table_data['headers']
            
            for row_idx, row in enumerate(table_data['rows']):
                flat_row = {f"row_{row_idx}_{header}": value 
                           for header, value in zip(headers, row)}
                flat_row['row_index'] = row_idx
                flattened_rows.append(flat_row)
            
            if self.array_strategy == "separate_rows":
                return flattened_rows
            else:
                # Merge all rows into single flat structure
                merged = {}
                for row in flattened_rows:
                    merged.update(row)
                return merged
        
        # For other structures, use general flattening
        return self.flatten(table_data)
    
    def flatten_network_diagram(self, diagram_data: Dict) -> Dict:
        """
        Flatten network diagram data for vector databases.
        
        Args:
            diagram_data: Network diagram structure
            
        Returns:
            Flattened diagram data
        """
        flattened = {}
        
        # Flatten components
        if 'components' in diagram_data:
            for i, component in enumerate(diagram_data['components']):
                prefix = f"component_{i}"
                if isinstance(component, dict):
                    for key, value in component.items():
                        flattened[f"{prefix}_{key}"] = value
                else:
                    flattened[prefix] = component
        
        # Flatten connections
        if 'connections' in diagram_data:
            for i, connection in enumerate(diagram_data['connections']):
                prefix = f"connection_{i}"
                if isinstance(connection, dict):
                    for key, value in connection.items():
                        flattened[f"{prefix}_{key}"] = value
                else:
                    flattened[prefix] = connection
        
        # Flatten zones
        if 'zones' in diagram_data:
            for i, zone in enumerate(diagram_data['zones']):
                prefix = f"zone_{i}"
                if isinstance(zone, dict):
                    for key, value in zone.items():
                        flattened[f"{prefix}_{key}"] = value
                else:
                    flattened[prefix] = zone
        
        # Add other top-level fields
        for key, value in diagram_data.items():
            if key not in ['components', 'connections', 'zones']:
                if isinstance(value, (dict, list)):
                    flat_value = self.flatten(value, key)
                    if isinstance(flat_value, dict):
                        flattened.update(flat_value)
                    else:
                        flattened[key] = flat_value
                else:
                    flattened[key] = value
        
        return flattened