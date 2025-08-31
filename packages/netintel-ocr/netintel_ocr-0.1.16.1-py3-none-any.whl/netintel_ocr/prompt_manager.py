"""Prompt management for export, import, and customization."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from .constants import ALL_PROMPTS
from .output_utils import info_print, always_print, debug_print


class PromptManager:
    """Manages prompts for NetIntel-OCR including export, import, and customization."""
    
    def __init__(self):
        """Initialize the prompt manager."""
        self.prompts = ALL_PROMPTS.copy()
        self.custom_prompts = {}
        self.version = "0.1.16"
    
    def export_prompts(self, output_file: str = "prompts_export.json") -> bool:
        """
        Export all prompts to a JSON file.
        
        Args:
            output_file: Path to the output JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            export_data = {
                "version": self.version,
                "description": "NetIntel-OCR prompt configuration",
                "prompts": {}
            }
            
            # Export all prompts with full details
            for key, prompt_data in self.prompts.items():
                export_data["prompts"][key] = {
                    "name": prompt_data.get("name", key.upper()),
                    "description": self._get_prompt_description(key),
                    "content": prompt_data.get("content", ""),
                    "model": prompt_data.get("model", ""),
                    "timeout": prompt_data.get("timeout", 60)
                }
            
            # Write to file
            output_path = Path(output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            always_print(f"✅ Prompts exported successfully to: {output_path}")
            return True
            
        except Exception as e:
            always_print(f"❌ Failed to export prompts: {e}")
            return False
    
    def import_prompts(self, input_file: str) -> bool:
        """
        Import prompts from a JSON file.
        
        Args:
            input_file: Path to the input JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            input_path = Path(input_file)
            
            if not input_path.exists():
                always_print(f"❌ File not found: {input_path}")
                return False
            
            with open(input_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Validate format
            if "prompts" not in import_data:
                always_print("❌ Invalid prompt file format (missing 'prompts' key)")
                return False
            
            # Import prompts
            imported_count = 0
            for key, prompt_data in import_data["prompts"].items():
                if key in self.prompts:
                    # Update existing prompt
                    self.prompts[key]["content"] = prompt_data.get("content", "")
                    self.prompts[key]["model"] = prompt_data.get("model", self.prompts[key].get("model", ""))
                    self.prompts[key]["timeout"] = prompt_data.get("timeout", self.prompts[key].get("timeout", 60))
                else:
                    # Add new custom prompt
                    self.custom_prompts[key] = prompt_data
                
                imported_count += 1
            
            always_print(f"✅ Successfully imported {imported_count} prompts from: {input_path}")
            
            # Show version info if available
            if "version" in import_data:
                info_print(f"   Prompt version: {import_data['version']}")
            
            return True
            
        except json.JSONDecodeError as e:
            always_print(f"❌ Invalid JSON format: {e}")
            return False
        except Exception as e:
            always_print(f"❌ Failed to import prompts: {e}")
            return False
    
    def show_prompts(self, prompt_key: Optional[str] = None) -> None:
        """
        Display prompts to the user.
        
        Args:
            prompt_key: Optional specific prompt to show
        """
        if prompt_key:
            # Show specific prompt
            if prompt_key in self.prompts:
                prompt_data = self.prompts[prompt_key]
                self._display_prompt(prompt_key, prompt_data)
            elif prompt_key in self.custom_prompts:
                prompt_data = self.custom_prompts[prompt_key]
                self._display_prompt(prompt_key, prompt_data)
            else:
                always_print(f"❌ Prompt not found: {prompt_key}")
                always_print("\nAvailable prompts:")
                for key in sorted(self.prompts.keys()):
                    always_print(f"  - {key}")
        else:
            # Show all prompts
            always_print("\n=== NetIntel-OCR Prompts ===\n")
            
            always_print("Built-in Prompts:")
            for key in sorted(self.prompts.keys()):
                prompt_data = self.prompts[key]
                always_print(f"\n  📝 {key}")
                always_print(f"     Model: {prompt_data.get('model', 'default')}")
                always_print(f"     Timeout: {prompt_data.get('timeout', 60)}s")
                
            if self.custom_prompts:
                always_print("\nCustom Prompts:")
                for key in sorted(self.custom_prompts.keys()):
                    prompt_data = self.custom_prompts[key]
                    always_print(f"\n  🎨 {key}")
                    always_print(f"     Model: {prompt_data.get('model', 'default')}")
                    always_print(f"     Timeout: {prompt_data.get('timeout', 60)}s")
    
    def override_prompt(self, prompt_key: str, new_content: str) -> bool:
        """
        Override a specific prompt with new content.
        
        Args:
            prompt_key: The prompt to override
            new_content: The new prompt content
            
        Returns:
            True if successful
        """
        if prompt_key in self.prompts:
            self.prompts[prompt_key]["content"] = new_content
            debug_print(f"Overridden prompt: {prompt_key}")
            return True
        else:
            # Add as custom prompt
            self.custom_prompts[prompt_key] = {
                "name": prompt_key.upper(),
                "content": new_content,
                "model": "default",
                "timeout": 60
            }
            debug_print(f"Added custom prompt: {prompt_key}")
            return True
    
    def get_prompt(self, prompt_key: str) -> Optional[str]:
        """
        Get the content of a specific prompt.
        
        Args:
            prompt_key: The prompt to retrieve
            
        Returns:
            Prompt content or None if not found
        """
        if prompt_key in self.prompts:
            return self.prompts[prompt_key].get("content", "")
        elif prompt_key in self.custom_prompts:
            return self.custom_prompts[prompt_key].get("content", "")
        return None
    
    def get_prompt_config(self, prompt_key: str) -> Optional[Dict[str, Any]]:
        """
        Get the full configuration for a prompt.
        
        Args:
            prompt_key: The prompt to retrieve
            
        Returns:
            Prompt configuration or None if not found
        """
        if prompt_key in self.prompts:
            return self.prompts[prompt_key]
        elif prompt_key in self.custom_prompts:
            return self.custom_prompts[prompt_key]
        return None
    
    def list_prompt_templates(self) -> None:
        """List available prompt templates."""
        templates = {
            "security-focused": "Enhanced security analysis for network diagrams",
            "compliance-audit": "Compliance and audit focus for regulatory requirements",
            "cloud-architecture": "Cloud and containerized environment analysis",
            "iot-networks": "IoT and embedded systems network analysis",
            "telecom": "Telecommunications infrastructure analysis",
            "process-optimization": "Process flow optimization and efficiency",
            "workflow-automation": "Workflow automation opportunity detection"
        }
        
        always_print("\n=== Available Prompt Templates ===\n")
        for template_name, description in templates.items():
            always_print(f"  📋 {template_name}")
            always_print(f"     {description}")
        always_print("\nUse: netintel-ocr document.pdf --prompt-template <template-name>")
    
    def load_template(self, template_name: str) -> bool:
        """
        Load a prompt template.
        
        Args:
            template_name: Name of the template to load
            
        Returns:
            True if successful
        """
        # Templates would be predefined sets of prompts
        templates = {
            "security-focused": {
                "diagram_detection": "Focus on identifying security architecture elements...",
                "network_context": "Analyze security implications, vulnerabilities, and compliance..."
            },
            "process-optimization": {
                "flow_element_extraction": "Identify bottlenecks and inefficiencies...",
                "flow_context": "Focus on process optimization opportunities..."
            }
        }
        
        if template_name in templates:
            template_prompts = templates[template_name]
            for key, content in template_prompts.items():
                self.override_prompt(key, content)
            always_print(f"✅ Loaded template: {template_name}")
            return True
        else:
            always_print(f"❌ Template not found: {template_name}")
            self.list_prompt_templates()
            return False
    
    def _display_prompt(self, key: str, prompt_data: Dict[str, Any]) -> None:
        """Display a single prompt."""
        always_print(f"\n=== Prompt: {key} ===")
        always_print(f"Name: {prompt_data.get('name', key)}")
        always_print(f"Model: {prompt_data.get('model', 'default')}")
        always_print(f"Timeout: {prompt_data.get('timeout', 60)}s")
        always_print(f"\nContent:")
        always_print("-" * 40)
        content = prompt_data.get('content', '')
        # Truncate very long prompts for display
        if len(content) > 500:
            always_print(content[:500] + "...\n[Truncated for display]")
        else:
            always_print(content)
        always_print("-" * 40)
    
    def _get_prompt_description(self, key: str) -> str:
        """Get a description for a prompt key."""
        descriptions = {
            "unified_extraction": "Extract text and tables from document images",
            "diagram_detection": "Detect network, flow, and hybrid diagrams",
            "network_component_extraction": "Extract network components from diagrams",
            "flow_element_extraction": "Extract flow diagram elements",
            "network_mermaid_generation": "Generate Mermaid.js network diagrams",
            "flow_mermaid_generation": "Generate Mermaid.js flow diagrams",
            "network_context": "Analyze network diagram context",
            "flow_context": "Analyze flow diagram context"
        }
        return descriptions.get(key, f"Prompt for {key}")


# Global prompt manager instance
prompt_manager = PromptManager()