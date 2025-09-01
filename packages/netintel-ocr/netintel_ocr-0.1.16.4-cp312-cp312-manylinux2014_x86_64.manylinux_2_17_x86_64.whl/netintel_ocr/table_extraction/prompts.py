"""
Prompt templates for table extraction.
"""

TABLE_DETECTION_PROMPT = """
Analyze this image and determine if it contains any tables.

A table is defined as:
- Data organized in rows and columns
- Has clear cell boundaries (with or without visible borders)
- Contains structured information (not just layout)
- May have headers, merged cells, or multi-row fields

IMPORTANT: The following should NOT be considered tables:
- Table of Contents (ToC)
- Index pages
- Lists of figures or tables
- Navigation menus
- Simple numbered or bulleted lists with page numbers

Response format (JSON only):
{
  "has_tables": boolean,
  "confidence": 0.0-1.0,
  "table_count": integer,
  "table_types": ["simple", "complex", "multi_row", "form"],
  "table_regions": [
    {
      "description": "brief description of table content",
      "has_headers": boolean,
      "has_merged_cells": boolean,
      "approximate_rows": integer,
      "approximate_columns": integer
    }
  ]
}

Return ONLY valid JSON, no additional text or markdown.
"""

SIMPLE_TABLE_EXTRACTION_PROMPT = """
Extract this table as a JSON array. Each row should be an object with column headers as keys.

Requirements:
1. Identify all column headers
2. Extract each data row
3. Preserve data types (numbers as numbers, not strings)
4. Handle empty cells as null

Return only valid JSON without markdown formatting.
Example format:
{
  "headers": ["Col1", "Col2", "Col3"],
  "data": [
    {"Col1": "value1", "Col2": 123, "Col3": null},
    {"Col1": "value2", "Col2": 456, "Col3": "text"}
  ]
}
"""

COMPLEX_TABLE_EXTRACTION_PROMPT = """
Analyze this complex table structure and extract all content:

1. Identify all header levels and hierarchies
2. Map merged cells to their spanning rows/columns
3. Extract content preserving relationships
4. Note any special formatting or groupings

Return as nested JSON maintaining the structure:
{
  "structure": {
    "headers": {
      "level1": [...],
      "level2": {...}
    },
    "merged_cells": [
      {"row": 0, "col": 0, "rowspan": 1, "colspan": 3}
    ]
  },
  "data": [
    {
      "row_headers": {...},
      "values": {...}
    }
  ]
}

Return ONLY valid JSON.
"""

MULTI_ROW_FIELD_EXTRACTION_PROMPT = """
This table contains fields that may span multiple rows. Extract the content by:

1. Identifying field labels (may span rows)
2. Associating values with correct labels
3. Grouping related fields
4. Handling wrapped text in cells

Return as key-value JSON pairs:
{
  "fields": {
    "Field Group 1": {
      "Label1": "Value1",
      "Label2": "Multi-line\\nvalue here",
      "Label3": ["Item1", "Item2"]
    },
    "Field Group 2": {
      ...
    }
  }
}

Return ONLY valid JSON.
"""

FAST_TABLE_EXTRACTION_PROMPT = """
Quickly extract table data from this image.

List rows with values separated by | character.
First row should be headers if present.

Format:
Header1|Header2|Header3
Value1|Value2|Value3
Value4|Value5|Value6

Be concise and accurate.
"""

def get_prompt_for_table_type(table_type: str, fast_mode: bool = False) -> str:
    """
    Get the appropriate prompt based on table type.
    
    Args:
        table_type: Type of table ('simple', 'complex', 'multi_row')
        fast_mode: Whether to use fast extraction prompt
        
    Returns:
        Appropriate prompt string
    """
    if fast_mode:
        return FAST_TABLE_EXTRACTION_PROMPT
    
    prompts = {
        'simple': SIMPLE_TABLE_EXTRACTION_PROMPT,
        'complex': COMPLEX_TABLE_EXTRACTION_PROMPT,
        'multi_row': MULTI_ROW_FIELD_EXTRACTION_PROMPT,
        'form': MULTI_ROW_FIELD_EXTRACTION_PROMPT
    }
    
    return prompts.get(table_type, SIMPLE_TABLE_EXTRACTION_PROMPT)