"""Improved prompts for more accurate network diagram extraction."""

# Detailed extraction prompt with better instructions
IMPROVED_EXTRACTION_PROMPT = """You are analyzing a network architecture diagram. Your task is to accurately identify EVERY visible component and connection.

CRITICAL INSTRUCTIONS:
1. Read ALL text labels carefully - they contain the actual component names
2. Look for component icons/shapes to determine types:
   - Cylinders/drums = database
   - Cloud shapes = cloud service
   - Rectangle with ports = switch
   - Circle/oval with arrows = router
   - Shield/brick pattern = firewall
   - Multiple rectangles stacked = server/server farm
   - Computer monitor = workstation
   - Antenna symbol = wireless access point
   - Diamond/hexagon = load balancer

3. For EACH component you see:
   - Use the EXACT text label shown (e.g., "WAN1", "WAN2", "Branch FortiGate")
   - Don't make up generic names like "Router1" if specific names are visible
   - Include any IP addresses, port numbers, or VLAN IDs shown

4. For connections:
   - Trace EVERY line between components
   - Note line styles: solid = physical, dashed = logical/VPN, dotted = wireless
   - Include arrow directions if shown
   - Look for connection labels (protocols, bandwidth, etc.)

5. Pay attention to:
   - Groupings/zones (boxes around components)
   - Color coding (often indicates security zones)
   - Hierarchical layout (top = external, bottom = internal)
   - Redundant paths (multiple lines between same components)

ANALYZE THE DIAGRAM SYSTEMATICALLY:
- Start from the top/external side
- Work through each layer/zone
- End at the bottom/internal side

Return ONLY the actual components and connections you can SEE in the diagram.
Do NOT add theoretical or assumed components.

JSON Response Format:
{
  "components": [
    {
      "id": "unique_identifier_based_on_label",
      "type": "component_type",
      "label": "EXACT text label from diagram",
      "details": "any additional info like IP, VLAN, port",
      "zone": "if grouped in a named zone"
    }
  ],
  "connections": [
    {
      "from": "source_component_id",
      "to": "destination_component_id",
      "type": "physical|logical|vpn|wireless",
      "label": "any text on the connection line",
      "bidirectional": true/false
    }
  ],
  "zones": [
    {
      "name": "zone name if labeled",
      "components": ["list of component IDs in this zone"],
      "type": "dmz|internal|external|trusted|untrusted"
    }
  ]
}"""

# Improved fast extraction prompt
IMPROVED_FAST_PROMPT = """Look at this network diagram and list EXACTLY what you see.

READ THE LABELS! Use the actual text shown, not generic names.

For each component:
- Write the EXACT label/text shown on or near it
- Identify what type it is based on its shape/icon

For each connection:
- List what it connects (use the exact labels)
- Note if it's solid, dashed, or dotted line

Example format:
Components:
- WAN1: interface (labeled "WAN1")
- Branch FortiGate: firewall (text says "Branch FortiGate")
- MPLS Network: cloud (cloud shape labeled "MPLS")

Connections:
- WAN1 connects to MPLS Network (solid line)
- Branch FortiGate connects to WAN1 (solid line)

Be precise. Use the ACTUAL text from the diagram."""

# Prompt for verifying extraction accuracy
VERIFICATION_PROMPT = """Compare this extraction with the original diagram:

Extracted components: {components}

Check:
1. Are all visible components listed?
2. Do the labels match EXACTLY what's shown?
3. Are any components missing?
4. Are the connections accurate?

If anything is wrong, provide corrections."""

# Prompt specifically for SD-WAN diagrams
SDWAN_SPECIFIC_PROMPT = """This is an SD-WAN architecture diagram. Focus on:

1. WAN Interfaces (WAN1, WAN2, etc.)
2. Underlay networks (MPLS, Internet, Broadband)
3. Overlay tunnels (IPsec, VPN)
4. FortiGate devices
5. Virtual WAN links
6. Branch vs Data Center components

Key patterns to identify:
- Underlay = physical connections (solid lines)
- Overlay = VPN/tunnel connections (dashed lines)
- Multiple paths between same endpoints = redundancy
- FortiGate devices act as SD-WAN controllers

List each component with its EXACT label from the diagram.
List each connection, noting if it's underlay or overlay.

JSON format:
{
  "components": [
    {"id": "exact_label", "type": "type", "label": "exact text", "role": "branch|datacenter|hub"}
  ],
  "connections": [
    {"from": "label1", "to": "label2", "layer": "underlay|overlay", "type": "mpls|internet|ipsec"}
  ]
}"""

# Prompt for handling Figure references
FIGURE_AWARE_PROMPT = """This page contains Figure {figure_number}: {figure_title}

Focus ONLY on the diagram labeled as Figure {figure_number}.
Extract components and connections from this specific diagram.
Ignore any other diagrams or figures on the page.

Use the EXACT labels shown in Figure {figure_number}."""

def get_improved_prompt(diagram_type: str = "general", **kwargs) -> str:
    """
    Get an improved prompt based on diagram type.
    
    Args:
        diagram_type: Type of diagram (general, sdwan, figure, fast)
        **kwargs: Additional parameters (figure_number, figure_title, etc.)
    
    Returns:
        Appropriate prompt string
    """
    if diagram_type == "sdwan":
        return SDWAN_SPECIFIC_PROMPT
    elif diagram_type == "figure" and "figure_number" in kwargs:
        return FIGURE_AWARE_PROMPT.format(
            figure_number=kwargs.get("figure_number"),
            figure_title=kwargs.get("figure_title", "")
        )
    elif diagram_type == "fast":
        return IMPROVED_FAST_PROMPT
    else:
        return IMPROVED_EXTRACTION_PROMPT