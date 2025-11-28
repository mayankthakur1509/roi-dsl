"""
ROI-DSL Parser v2.1
Converts .roi text files into Abstract Syntax Tree (AST)
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


# AST Node Classes
@dataclass
class PersonaNode:
    name: str
    value: str


@dataclass
class GoalNode:
    name: str
    value: str


@dataclass
class MetricNode:
    name: str
    value: float


@dataclass
class RMetricNode:
    name: str
    expr: str


@dataclass
class TriggerNode:
    condition: str
    action: str


@dataclass
class VariantNode:
    type: str  # Hero, Resume, CTA
    value: str


@dataclass
class ROIDSLAST:
    """Root AST node for ROI-DSL file"""
    persona: Optional[PersonaNode] = None
    personas: List[PersonaNode] = field(default_factory=list)  # Multiple personas
    goals: List[GoalNode] = field(default_factory=list)
    metrics: List[MetricNode] = field(default_factory=list)
    rmetrics: List[RMetricNode] = field(default_factory=list)
    triggers: List[TriggerNode] = field(default_factory=list)
    variants: List[VariantNode] = field(default_factory=list)
    credentials: Dict[str, str] = field(default_factory=dict)
    case_studies: Dict[str, str] = field(default_factory=dict)
    services: Dict[str, str] = field(default_factory=dict)
    training: Dict[str, str] = field(default_factory=dict)
    vroi_inputs: Dict[str, str] = field(default_factory=dict)
    vroi_outputs: Dict[str, str] = field(default_factory=dict)
    stats: Dict[str, str] = field(default_factory=dict)
    microtraining: Dict[str, str] = field(default_factory=dict)
    seo: Dict[str, str] = field(default_factory=dict)
    contact: Dict[str, str] = field(default_factory=dict)
    sk_tags: List[str] = field(default_factory=list)
    output: Optional[str] = None


class ROIDSLParser:
    """Parser for ROI-DSL v2"""
    
    def __init__(self, text: str):
        self.text = text
        self.lines = [line.strip() for line in text.split('\n') if line.strip()]
        self.current_line = 0
        self.ast = ROIDSLAST()
    
    def parse(self) -> ROIDSLAST:
        """Parse the entire ROI-DSL file"""
        while self.current_line < len(self.lines):
            line = self.lines[self.current_line]
            
            # Skip comments
            if line.startswith('#') or line.startswith('//'):
                self.current_line += 1
                continue
            
            # Parse each block type
            if line.startswith('PERSONA'):
                self._parse_persona(line)
            elif line.startswith('GOAL'):
                self._parse_goal(line)
            elif line.startswith('METRIC') and not line.startswith('RMetric'):
                self._parse_metric(line)
            elif line.startswith('RMetric'):
                self._parse_rmetric(line)
            elif line.startswith('WHEN'):
                self._parse_trigger(line)
            elif line.startswith('VARIANT'):
                self._parse_variant(line)
            elif line.startswith('CREDENTIAL'):
                self._parse_credential(line)
            elif line.startswith('CASE_STUDY'):
                self._parse_case_study(line)
            elif line.startswith('SERVICE'):
                self._parse_service(line)
            elif line.startswith('TRAINING'):
                self._parse_training(line)
            elif line.startswith('VROI_INPUT'):
                self._parse_vroi_input(line)
            elif line.startswith('VROI_OUTPUT'):
                self._parse_vroi_output(line)
            elif line.startswith('STAT'):
                self._parse_stat(line)
            elif line.startswith('MICROTRAINING'):
                self._parse_microtraining(line)
            elif line.startswith('SEO_'):
                self._parse_seo(line)
            elif line.startswith('CONTACT_'):
                self._parse_contact(line)
            elif line.startswith('SK_TAG'):
                self._parse_sk_tag(line)
            elif line.startswith('OUTPUT'):
                self._parse_output(line)
            else:
                raise SyntaxError(f"Unknown syntax at line {self.current_line + 1}: {line}")
            
            self.current_line += 1
        
        return self.ast
    
    def _parse_persona(self, line: str):
        """Parse PERSONA block - support multiple personas"""
        # PERSONA Sponsor: "CNS Phase III Director"
        pattern = r'PERSONA\s+(\w+)\s*:\s*"([^"]+)"'
        match = re.match(pattern, line)
        
        if not match:
            raise SyntaxError(f"Invalid PERSONA syntax: {line}")
        
        name = match.group(1)
        value = match.group(2)
        
        persona_node = PersonaNode(name=name, value=value)
        
        # Set primary persona if not set
        if not self.ast.persona:
            self.ast.persona = persona_node
        
        # Add to personas list
        self.ast.personas.append(persona_node)
    
    def _parse_credential(self, line: str):
        """Parse CREDENTIAL block"""
        # CREDENTIAL Sites: "536+ Sites Managed"
        pattern = r'CREDENTIAL\s+(\w+)\s*:\s*"([^"]+)"'
        match = re.match(pattern, line)
        
        if not match:
            raise SyntaxError(f"Invalid CREDENTIAL syntax: {line}")
        
        key = match.group(1)
        value = match.group(2)
        self.ast.credentials[key] = value
    
    def _parse_case_study(self, line: str):
        """Parse CASE_STUDY block"""
        # CASE_STUDY Asubio: "COPD Phase IIb – 40 Sites..."
        pattern = r'CASE_STUDY\s+(\w+)\s*:\s*"([^"]+)"'
        match = re.match(pattern, line)
        
        if not match:
            raise SyntaxError(f"Invalid CASE_STUDY syntax: {line}")
        
        key = match.group(1)
        value = match.group(2)
        self.ast.case_studies[key] = value
    
    def _parse_service(self, line: str):
        """Parse SERVICE block"""
        # SERVICE CriticalPath: "Critical-Path Turnaround – Rescue delayed trials"
        pattern = r'SERVICE\s+(\w+)\s*:\s*"([^"]+)"'
        match = re.match(pattern, line)
        
        if not match:
            raise SyntaxError(f"Invalid SERVICE syntax: {line}")
        
        key = match.group(1)
        value = match.group(2)
        self.ast.services[key] = value
    
    def _parse_training(self, line: str):
        """Parse TRAINING block"""
        # TRAINING MonitoringRisk: "Monitoring for Risk – Proactive detection"
        pattern = r'TRAINING\s+(\w+)\s*:\s*"([^"]+)"'
        match = re.match(pattern, line)
        
        if not match:
            raise SyntaxError(f"Invalid TRAINING syntax: {line}")
        
        key = match.group(1)
        value = match.group(2)
        self.ast.training[key] = value
    
    def _parse_vroi_input(self, line: str):
        """Parse VROI_INPUT block"""
        # VROI_INPUT StudyPhase: "Phase (I / II / III / PM)"
        pattern = r'VROI_INPUT\s+(\w+)\s*:\s*"([^"]+)"'
        match = re.match(pattern, line)
        
        if not match:
            raise SyntaxError(f"Invalid VROI_INPUT syntax: {line}")
        
        key = match.group(1)
        value = match.group(2)
        self.ast.vroi_inputs[key] = value
    
    def _parse_vroi_output(self, line: str):
        """Parse VROI_OUTPUT block"""
        # VROI_OUTPUT DelayCost: "Cost of Delay (Monthly)"
        pattern = r'VROI_OUTPUT\s+(\w+)\s*:\s*"([^"]+)"'
        match = re.match(pattern, line)
        
        if not match:
            raise SyntaxError(f"Invalid VROI_OUTPUT syntax: {line}")
        
        key = match.group(1)
        value = match.group(2)
        self.ast.vroi_outputs[key] = value
    
    def _parse_stat(self, line: str):
        """Parse STAT block"""
        # STAT Sites: "536 Sites"
        pattern = r'STAT\s+(\w+)\s*:\s*"([^"]+)"'
        match = re.match(pattern, line)
        
        if not match:
            raise SyntaxError(f"Invalid STAT syntax: {line}")
        
        key = match.group(1)
        value = match.group(2)
        self.ast.stats[key] = value
    
    def _parse_microtraining(self, line: str):
        """Parse MICROTRAINING block"""
        # MICROTRAINING Title: "See the CRO Precision Method"
        pattern = r'MICROTRAINING\s+(\w+)\s*:\s*"([^"]+)"'
        match = re.match(pattern, line)
        
        if not match:
            raise SyntaxError(f"Invalid MICROTRAINING syntax: {line}")
        
        key = match.group(1)
        value = match.group(2)
        self.ast.microtraining[key] = value
    
    def _parse_seo(self, line: str):
        """Parse SEO_* block"""
        # SEO_TITLE: "Rose Maloney - Clinical Operations Expert"
        pattern = r'SEO_(\w+)\s*:\s*"([^"]+)"'
        match = re.match(pattern, line)
        
        if not match:
            raise SyntaxError(f"Invalid SEO syntax: {line}")
        
        key = match.group(1)
        value = match.group(2)
        self.ast.seo[key] = value
    
    def _parse_contact(self, line: str):
        """Parse CONTACT_* block"""
        # CONTACT_NAME: "Rose Maloney"
        pattern = r'CONTACT_(\w+)\s*:\s*"([^"]+)"'
        match = re.match(pattern, line)
        
        if not match:
            raise SyntaxError(f"Invalid CONTACT syntax: {line}")
        
        key = match.group(1)
        value = match.group(2)
        self.ast.contact[key] = value
    
    def _parse_sk_tag(self, line: str):
        """Parse SK_TAG block"""
        # SK_TAG: "clinical_operations_expert"
        pattern = r'SK_TAG\s*:\s*"([^"]+)"'
        match = re.match(pattern, line)
        
        if not match:
            raise SyntaxError(f"Invalid SK_TAG syntax: {line}")
        
        value = match.group(1)
        self.ast.sk_tags.append(value)
    
    def _parse_goal(self, line: str):
        """Parse GOAL block"""
        # GOAL DelayCost: "Avoid $2M/mo burn"
        pattern = r'GOAL\s+(\w+)\s*:\s*"([^"]+)"'
        match = re.match(pattern, line)
        
        if not match:
            raise SyntaxError(f"Invalid GOAL syntax: {line}")
        
        name = match.group(1)
        value = match.group(2)
        
        self.ast.goals.append(GoalNode(name=name, value=value))
    
    def _parse_metric(self, line: str):
        """Parse METRIC block"""
        # METRIC VendorDrift: 0.45
        pattern = r'METRIC\s+(\w+)\s*:\s*([\d.]+)'
        match = re.match(pattern, line)
        
        if not match:
            raise SyntaxError(f"Invalid METRIC syntax: {line}")
        
        name = match.group(1)
        value = float(match.group(2))
        
        self.ast.metrics.append(MetricNode(name=name, value=value))
    
    def _parse_rmetric(self, line: str):
        """Parse RMetric block"""
        # RMetric StudyHealth: "TimelineRisk * 1.2 + VendorDrift"
        pattern = r'RMetric\s+(\w+)\s*:\s*"([^"]+)"'
        match = re.match(pattern, line)
        
        if not match:
            raise SyntaxError(f"Invalid RMetric syntax: {line}")
        
        name = match.group(1)
        expr = match.group(2)
        
        self.ast.rmetrics.append(RMetricNode(name=name, expr=expr))
    
    def _parse_trigger(self, line: str):
        """Parse WHEN/THEN trigger block"""
        # WHEN VendorDrift > 0.40 THEN escalate("vendor")
        pattern = r'WHEN\s+(.+?)\s+THEN\s+(.+)'
        match = re.match(pattern, line)
        
        if not match:
            raise SyntaxError(f"Invalid WHEN/THEN syntax: {line}")
        
        condition = match.group(1).strip()
        action = match.group(2).strip()
        
        self.ast.triggers.append(TriggerNode(condition=condition, action=action))
    
    def _parse_variant(self, line: str):
        """Parse VARIANT block"""
        # VARIANT Hero: "CRO Sponsor"
        pattern = r'VARIANT\s+(\w+)\s*:\s*"([^"]+)"'
        match = re.match(pattern, line)
        
        if not match:
            raise SyntaxError(f"Invalid VARIANT syntax: {line}")
        
        variant_type = match.group(1)
        value = match.group(2)
        
        # Allow any variant type for flexibility
        self.ast.variants.append(VariantNode(type=variant_type, value=value))
    
    def _parse_output(self, line: str):
        """Parse OUTPUT block"""
        # OUTPUT MintSite
        pattern = r'OUTPUT\s+(\w+)'
        match = re.match(pattern, line)
        
        if not match:
            raise SyntaxError(f"Invalid OUTPUT syntax: {line}")
        
        output_type = match.group(1)
        
        valid_outputs = ['SMS_CAMPAIGN', 'AGENT', 'RMetrics', 'vROI', 'MintSite', 'SK_SKILL']
        if output_type not in valid_outputs:
            raise SyntaxError(f"Invalid OUTPUT type '{output_type}'. Must be one of: {', '.join(valid_outputs)}")
        
        self.ast.output = output_type
    
    def get_metrics_map(self) -> Dict[str, float]:
        """Get metrics as a dictionary"""
        return {m.name: m.value for m in self.ast.metrics}
    
    def get_goals_map(self) -> Dict[str, str]:
        """Get goals as a dictionary"""
        return {g.name: g.value for g in self.ast.goals}


# Convenience function
def parse_roi_file(filepath: str) -> ROIDSLAST:
    """Parse a .roi file and return AST"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    parser = ROIDSLParser(content)
    return parser.parse()
