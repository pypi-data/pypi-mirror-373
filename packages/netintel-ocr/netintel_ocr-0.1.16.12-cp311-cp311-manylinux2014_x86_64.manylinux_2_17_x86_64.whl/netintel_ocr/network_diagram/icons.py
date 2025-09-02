"""Icon mappings for network components."""

COMPONENT_ICONS = {
    "router": {
        "icon": "fa:fa-route",
        "mermaid_shape": "([{label}])",
        "style_class": "router"
    },
    "switch": {
        "icon": "fa:fa-network-wired",
        "mermaid_shape": "[{label}]",
        "style_class": "switch"
    },
    "firewall": {
        "icon": "fa:fa-shield-alt",
        "mermaid_shape": "{{{label}}}",
        "style_class": "firewall"
    },
    "server": {
        "icon": "fa:fa-server",
        "mermaid_shape": "[({label})]",
        "style_class": "server"
    },
    "database": {
        "icon": "fa:fa-database",
        "mermaid_shape": "[({label})]",
        "style_class": "database"
    },
    "load_balancer": {
        "icon": "fa:fa-balance-scale",
        "mermaid_shape": "[/{label}/]",
        "style_class": "loadbalancer"
    },
    "cloud": {
        "icon": "fa:fa-cloud",
        "mermaid_shape": "(({label}))",
        "style_class": "cloud"
    },
    "workstation": {
        "icon": "fa:fa-desktop",
        "mermaid_shape": "[{label}]",
        "style_class": "workstation"
    },
    "wireless_ap": {
        "icon": "fa:fa-wifi",
        "mermaid_shape": "((( {label} )))",
        "style_class": "wireless"
    }
}

CONNECTION_STYLES = {
    "ethernet": {
        "syntax": "---",
        "label_format": "|{label}|"
    },
    "wireless": {
        "syntax": "-.-",
        "label_format": "|wireless|"
    },
    "vpn": {
        "syntax": "==>",
        "label_format": "|VPN|"
    },
    "data_flow": {
        "syntax": "-->",
        "label_format": "|{label}|"
    },
    "redundant": {
        "syntax": "===",
        "label_format": "|HA|"
    }
}

MERMAID_STYLES = """
    classDef router fill:#ffcc99,stroke:#333,stroke-width:2px
    classDef switch fill:#99ccff,stroke:#333,stroke-width:2px
    classDef firewall fill:#ff9999,stroke:#333,stroke-width:3px
    classDef server fill:#9999ff,stroke:#333,stroke-width:2px
    classDef database fill:#99ff99,stroke:#333,stroke-width:2px
    classDef loadbalancer fill:#ffff99,stroke:#333,stroke-width:2px
    classDef cloud fill:#cccccc,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5
    classDef workstation fill:#cc99ff,stroke:#333,stroke-width:1px
    classDef wireless fill:#99ffcc,stroke:#333,stroke-width:2px
"""