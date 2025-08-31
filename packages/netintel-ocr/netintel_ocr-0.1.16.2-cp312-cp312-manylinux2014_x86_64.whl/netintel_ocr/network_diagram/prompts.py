"""LLM prompts for network diagram processing."""

DETECTION_PROMPT = """Analyze this image and determine if it contains a network diagram.

Look for these network-specific elements:
- Network devices: routers, switches, firewalls, servers, load balancers
- Connection lines between components
- Network zones: DMZ, internal/external networks, VLANs
- Cloud representations
- Protocol labels: HTTP/HTTPS, TCP/UDP, SSH, VPN
- IP addresses or network notation

Response format (JSON):
{
  "is_network_diagram": true/false,
  "diagram_type": "topology|architecture|data_flow|security|cloud|other",
  "confidence": 0.0-1.0,
  "components_detected": ["router", "switch", "firewall", ...],
  "layout_pattern": "hierarchical|star|mesh|bus|ring|hybrid"
}

If not a network diagram, set is_network_diagram to false."""

EXTRACTION_PROMPT = """Extract all network diagram components and their relationships from this image.

For each network component, identify:
1. Component type - Choose ONLY ONE from: router, switch, firewall, server, database, load_balancer, cloud_service, workstation, wireless_ap
2. Component label/name if visible
3. IP address or network information if shown
4. Position in hierarchy - Choose ONE from: core, distribution, access, edge

For each connection, identify:
1. Source component
2. Destination component  
3. Connection type - Choose ONE from: ethernet, wireless, vpn, data_flow, redundant
4. Protocol or port information if labeled
5. Direction (unidirectional or bidirectional)

For network zones/segments:
1. Zone name (DMZ, Internal, External, etc.)
2. Security level - Choose ONE from: trusted, dmz, untrusted
3. Subnet/VLAN information if visible

IMPORTANT: For the "type" field, select ONLY ONE specific type that best matches the component. Do NOT use pipe characters (|) or list multiple types.

Response format (JSON):
{
  "components": [
    {
      "id": "unique_id",
      "type": "SELECT EXACTLY ONE: router, switch, firewall, server, database, load_balancer, cloud_service, workstation, or wireless_ap",
      "label": "visible text label",
      "ip_info": "IP address or subnet",
      "hierarchy_level": "SELECT ONE: core, distribution, access, or edge",
      "zone": "zone_name"
    }
  ],
  "connections": [
    {
      "from": "component_id",
      "to": "component_id",
      "type": "SELECT ONE: ethernet, wireless, vpn, data_flow, or redundant",
      "label": "protocol/port info",
      "bidirectional": true/false
    }
  ],
  "zones": [
    {
      "name": "zone_name",
      "security_level": "SELECT ONE: trusted, dmz, or untrusted",
      "subnet": "CIDR notation if visible"
    }
  ]
}"""

MERMAID_GENERATION_PROMPT = """Convert the extracted network components into a valid Mermaid diagram.

Components: {components}
Connections: {connections}
Zones: {zones}

IMPORTANT RULES:
1. DO NOT use curly braces {{ }} except for node shapes
2. DO NOT use // for comments - use %% for Mermaid comments
3. DO NOT include any programming language syntax
4. Start with: graph TB or graph LR (no curly braces)

Node Shape Syntax:
- Router: ([Router Name])
- Switch: [Switch Name]
- Firewall: {{{{Firewall Name}}}}
- Server: [(Server Name)]
- Database: [(Database Name)]
- Load Balancer: [/Load Balancer Name/]
- Cloud: ((Cloud Service))
- Workstation: [Workstation]
- Wireless AP: ((( AP Name )))

Connection Syntax:
- Ethernet: NodeA --- NodeB
- Wireless: NodeA -.- NodeB
- VPN: NodeA ==> NodeB
- Data flow: NodeA --> NodeB
- Redundant: NodeA === NodeB
- With label: NodeA ---|Label| NodeB

Example Output:
graph TB
    %% Network Components
    Router1([Main Router])
    Switch1[Core Switch]
    Server1[(Web Server)]
    
    %% Connections
    Router1 --> Switch1
    Switch1 --> Server1

Generate ONLY valid Mermaid syntax. No markdown, no code blocks, no programming comments."""