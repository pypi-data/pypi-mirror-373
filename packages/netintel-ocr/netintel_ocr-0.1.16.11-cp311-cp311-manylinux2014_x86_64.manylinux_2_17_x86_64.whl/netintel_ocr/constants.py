import os

# Allow configuring Ollama host via environment variable
# Default to localhost if not set
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_BASE_URL = f"{OLLAMA_HOST}/api"

TRANSCRIPTION_PROMPT = """Task: Transcribe the page from the provided book image.

- Reproduce the text exactly as it appears, without adding or omitting anything.
- Use Markdown syntax to preserve the original formatting (e.g., headings, bold, italics, lists).
- Do not include triple backticks (```) or any other code block markers in your response, unless the page contains code.
- Do not include any headers or footers (for example, page numbers).
- If the page contains an image, or a diagram, describe it in detail. Enclose the description in an <image> tag. For example:

<image>
This is an image of a cat.
</image>

"""

# Unified extraction prompt for text and tables
UNIFIED_EXTRACTION_PROMPT = """Extract all text content and tables from this image.

- Extract all text exactly as it appears
- For tables, format them in markdown table syntax
- Preserve the original structure and layout
- Include headers, rows, and columns accurately
- Do not add interpretation or commentary
"""

# Diagram detection prompt (unified for network/flow/hybrid)
DIAGRAM_DETECTION_PROMPT = """Analyze this image and determine if it contains a diagram.

Classify the diagram into one of these categories:
1. NETWORK: Network topology, security architecture, infrastructure diagrams
2. FLOW: Process flows, workflows, decision trees, sequence diagrams
3. HYBRID: Contains both network and flow elements
4. NONE: Not a diagram

Return JSON with: is_diagram, diagram_category, diagram_type, confidence, description, key_elements
"""

# Network component extraction prompt
NETWORK_COMPONENT_EXTRACTION_PROMPT = """Extract all network components from this diagram.

Identify:
- Network devices (routers, switches, firewalls, servers)
- Connections and relationships
- Security zones and boundaries
- IP addresses and network segments

Return JSON with: components, connections, security_zones, extraction_successful
"""

# Flow element extraction prompt
FLOW_ELEMENT_EXTRACTION_PROMPT = """Extract all flow diagram elements from this image.

Identify:
- Process boxes and steps
- Decision points
- Data stores
- Start/end points
- Flow connections with labels
- Swim lanes or phases

Return JSON with: elements, flows, swim_lanes, start_end_points, extraction_successful
"""

# Network Mermaid generation prompt
NETWORK_MERMAID_GENERATION_PROMPT = """Convert the network components into valid Mermaid.js graph syntax.

Use format: graph TD
Include network device icons where appropriate
Create clear connections between components
"""

# Flow Mermaid generation prompt
FLOW_MERMAID_GENERATION_PROMPT = """Convert the flow elements into valid Mermaid.js flowchart syntax.

Use format: flowchart TD or LR
Element shapes:
- Start/End: circles ([Start])
- Process: rectangles [Process]
- Decision: diamonds {Decision}
- Data: parallelograms [(Database)]

Label all decision outcomes (Yes/No, True/False)
"""

# Network context prompt
NETWORK_CONTEXT_PROMPT = """Analyze this network/security diagram focusing on:
- Architecture purpose
- Security zones and boundaries
- Data flow patterns
- Critical components
- Security recommendations
- How it relates to surrounding documentation
"""

# Flow context prompt
FLOW_CONTEXT_PROMPT = """Analyze this flow diagram focusing on:
- Process purpose and objectives
- Key decision points
- Process efficiency
- Bottlenecks
- Integration points
- Compliance checkpoints
- How it relates to surrounding documentation
"""

# Default models for different tasks
DEFAULT_TEXT_MODEL = "nanonets-ocr-s"
DEFAULT_VISION_MODEL = "NetIntelOCR-7B-0925"

# All prompts dictionary for export/import
ALL_PROMPTS = {
    "unified_extraction": {
        "name": "UNIFIED_EXTRACTION_PROMPT",
        "content": UNIFIED_EXTRACTION_PROMPT,
        "model": DEFAULT_TEXT_MODEL,
        "timeout": 120
    },
    "diagram_detection": {
        "name": "DIAGRAM_DETECTION_PROMPT",
        "content": DIAGRAM_DETECTION_PROMPT,
        "model": DEFAULT_VISION_MODEL,
        "timeout": 60
    },
    "network_component_extraction": {
        "name": "NETWORK_COMPONENT_EXTRACTION_PROMPT",
        "content": NETWORK_COMPONENT_EXTRACTION_PROMPT,
        "model": DEFAULT_VISION_MODEL,
        "timeout": 60
    },
    "flow_element_extraction": {
        "name": "FLOW_ELEMENT_EXTRACTION_PROMPT",
        "content": FLOW_ELEMENT_EXTRACTION_PROMPT,
        "model": DEFAULT_VISION_MODEL,
        "timeout": 60
    },
    "network_mermaid_generation": {
        "name": "NETWORK_MERMAID_GENERATION_PROMPT",
        "content": NETWORK_MERMAID_GENERATION_PROMPT,
        "model": DEFAULT_VISION_MODEL,
        "timeout": 60
    },
    "flow_mermaid_generation": {
        "name": "FLOW_MERMAID_GENERATION_PROMPT",
        "content": FLOW_MERMAID_GENERATION_PROMPT,
        "model": DEFAULT_VISION_MODEL,
        "timeout": 60
    },
    "network_context": {
        "name": "NETWORK_CONTEXT_PROMPT",
        "content": NETWORK_CONTEXT_PROMPT,
        "model": DEFAULT_VISION_MODEL,
        "timeout": 30
    },
    "flow_context": {
        "name": "FLOW_CONTEXT_PROMPT",
        "content": FLOW_CONTEXT_PROMPT,
        "model": DEFAULT_VISION_MODEL,
        "timeout": 30
    }
}
