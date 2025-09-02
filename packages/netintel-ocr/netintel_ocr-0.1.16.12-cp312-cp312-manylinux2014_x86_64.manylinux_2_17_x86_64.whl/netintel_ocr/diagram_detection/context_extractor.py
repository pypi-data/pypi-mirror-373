"""Context extractor for diagrams with surrounding text analysis."""

import json
from typing import Dict, Any, Optional
from ..ollama import transcribe_image
from ..output_utils import debug_print


class DiagramContextExtractor:
    """Extracts context and meaning from diagrams using surrounding text."""
    
    def __init__(self, model: str = "NetIntelOCR-7B-0925"):
        """
        Initialize the context extractor.
        
        Args:
            model: The model to use for context extraction
        """
        self.model = model
    
    def extract_context(self, image_path: str, mermaid_code: str,
                       surrounding_text: Dict[str, str],
                       diagram_category: str,
                       custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract context and meaning from diagram with surrounding text.
        
        Args:
            image_path: Path to the diagram image
            mermaid_code: Generated Mermaid code
            surrounding_text: Dict with 'before' and 'after' text
            diagram_category: 'network', 'flow', or 'hybrid'
            custom_prompt: Optional custom prompt
            
        Returns:
            Context analysis results
        """
        if diagram_category == 'network':
            return self.extract_network_context(
                image_path, mermaid_code,
                surrounding_text.get('before', ''),
                surrounding_text.get('after', ''),
                custom_prompt
            )
        elif diagram_category == 'flow':
            return self.extract_flow_context(
                image_path, mermaid_code,
                surrounding_text.get('before', ''),
                surrounding_text.get('after', ''),
                custom_prompt
            )
        elif diagram_category == 'hybrid':
            return self.extract_hybrid_context(
                image_path, mermaid_code,
                surrounding_text.get('before', ''),
                surrounding_text.get('after', ''),
                custom_prompt
            )
        else:
            return {'error': f'Unknown diagram category: {diagram_category}'}
    
    def extract_network_context(self, image_path: str, mermaid_code: str,
                               before_text: str, after_text: str,
                               custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Extract context for network diagrams."""
        prompt = custom_prompt or f"""
        Analyze this network/security diagram in its document context.
        
        Preceding context: {before_text[:500]}
        
        [NETWORK DIAGRAM - Mermaid representation]:
        {mermaid_code}
        
        Following context: {after_text[:500]}
        
        Provide analysis focusing on:
        1. Overall architecture purpose (informed by surrounding text)
        2. Security zones and boundaries
        3. Data flow patterns
        4. Critical paths and dependencies
        5. Potential security considerations
        6. Compliance/regulatory aspects
        7. How the diagram relates to the surrounding documentation
        
        Return JSON with:
        {{
            "architecture_summary": "brief summary",
            "document_context": "how diagram fits in document",
            "security_analysis": {{
                "zones": ["list of security zones"],
                "boundaries": ["trust boundaries"],
                "risks": ["potential risks"]
            }},
            "data_flows": ["list of data flow patterns"],
            "critical_components": ["critical infrastructure"],
            "recommendations": ["security recommendations"],
            "references": ["references to surrounding text"]
        }}"""
        
        try:
            response = transcribe_image(image_path, self.model, prompt)
            return self._parse_context_response(response, 'network')
        except Exception as e:
            debug_print(f"Network context extraction failed: {e}")
            return {'error': str(e)}
    
    def extract_flow_context(self, image_path: str, mermaid_code: str,
                            before_text: str, after_text: str,
                            custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Extract context for flow diagrams."""
        prompt = custom_prompt or f"""
        Analyze this flow/process diagram in its document context.
        
        Preceding context: {before_text[:500]}
        
        [FLOW DIAGRAM - Mermaid representation]:
        {mermaid_code}
        
        Following context: {after_text[:500]}
        
        Provide analysis focusing on:
        1. Process purpose and objectives
        2. Key decision points and their criteria
        3. Process efficiency and optimization opportunities
        4. Bottlenecks or critical paths
        5. Integration points with other processes
        6. Compliance or regulatory checkpoints
        7. How the process relates to the document narrative
        
        Return JSON with:
        {{
            "process_summary": "brief summary",
            "document_context": "how diagram fits in document",
            "decision_points": [
                {{
                    "point": "decision name",
                    "criteria": "decision criteria",
                    "impact": "business impact"
                }}
            ],
            "process_flow": {{
                "average_time": "estimated process time",
                "automation_level": "percentage automated",
                "manual_touchpoints": ["list of manual steps"]
            }},
            "bottlenecks": ["identified bottlenecks"],
            "optimization_opportunities": ["improvement suggestions"],
            "integration_points": ["systems/processes integrated"],
            "compliance_checkpoints": ["regulatory requirements"],
            "references": ["references to surrounding text"]
        }}"""
        
        try:
            response = transcribe_image(image_path, self.model, prompt)
            return self._parse_context_response(response, 'flow')
        except Exception as e:
            debug_print(f"Flow context extraction failed: {e}")
            return {'error': str(e)}
    
    def extract_hybrid_context(self, image_path: str, mermaid_code: str,
                              before_text: str, after_text: str,
                              custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Extract context for hybrid diagrams."""
        # Combine both network and flow analysis
        network_context = self.extract_network_context(
            image_path, mermaid_code, before_text, after_text
        )
        flow_context = self.extract_flow_context(
            image_path, mermaid_code, before_text, after_text
        )
        
        return {
            'diagram_type': 'hybrid',
            'network_analysis': network_context,
            'flow_analysis': flow_context,
            'document_context': network_context.get('document_context', '') or 
                              flow_context.get('document_context', ''),
            'combined_recommendations': (
                network_context.get('recommendations', []) +
                flow_context.get('optimization_opportunities', [])
            )
        }
    
    def _parse_context_response(self, response: str, context_type: str) -> Dict[str, Any]:
        """Parse the context extraction response."""
        try:
            # Try to extract JSON from response
            if isinstance(response, str):
                if '```json' in response:
                    json_str = response.split('```json')[1].split('```')[0].strip()
                elif '{' in response and '}' in response:
                    start = response.index('{')
                    end = response.rindex('}') + 1
                    json_str = response[start:end]
                else:
                    # Return as description if no JSON
                    return {
                        'summary': response[:500],
                        'document_context': 'Analysis provided in text format',
                        'type': context_type
                    }
                
                result = json.loads(json_str)
                result['type'] = context_type
                return result
            else:
                return response
                
        except Exception as e:
            debug_print(f"Failed to parse context response: {e}")
            return {
                'summary': response[:500] if isinstance(response, str) else str(response),
                'error': str(e),
                'type': context_type
            }
    
    def extract_surrounding_paragraphs(self, full_text: str, diagram_position: int,
                                      num_paragraphs: int = 2) -> Dict[str, str]:
        """
        Extract paragraphs before and after diagram position.
        
        Args:
            full_text: Complete page text
            diagram_position: Approximate position of diagram in text
            num_paragraphs: Number of paragraphs to extract
            
        Returns:
            Dict with 'before' and 'after' text
        """
        # Split into paragraphs
        paragraphs = [p.strip() for p in full_text.split('\n\n') if p.strip()]
        
        if not paragraphs:
            return {'before': '', 'after': ''}
        
        # Find diagram position in paragraphs
        # This is simplified - real implementation would need better position detection
        diagram_para_index = min(diagram_position // 500, len(paragraphs) - 1)
        
        # Extract before paragraphs
        before_start = max(0, diagram_para_index - num_paragraphs)
        before_paragraphs = paragraphs[before_start:diagram_para_index]
        
        # Extract after paragraphs
        after_end = min(len(paragraphs), diagram_para_index + num_paragraphs + 1)
        after_paragraphs = paragraphs[diagram_para_index + 1:after_end]
        
        return {
            'before': '\n\n'.join(before_paragraphs),
            'after': '\n\n'.join(after_paragraphs)
        }