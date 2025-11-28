"""
ROI-DSL Validator v2.1
Validates semantic rules and business logic guardrails
"""

from typing import Dict, List
import re


class ROIValidator:
    """Validates ROI-DSL AST for semantic correctness"""
    
    def __init__(self, ast):
        self.ast = ast
        self.errors = []
        self.warnings = []
    
    def validate(self) -> Dict[str, List[str]]:
        """
        Run all validation checks
        Returns: {'errors': [...], 'warnings': [...]}
        """
        self._validate_mandatory_fields()
        self._validate_persona()
        self._validate_goals()
        self._validate_metrics()
        self._validate_rmetrics()
        self._validate_triggers()
        self._validate_variants()
        self._validate_output()
        self._validate_identifier_references()
        
        return {
            'errors': self.errors,
            'warnings': self.warnings
        }
    
    def _validate_mandatory_fields(self):
        """Ensure mandatory fields are present"""
        if not self.ast.goals:
            self.errors.append("At least 1 GOAL is required")
        
        if not self.ast.metrics:
            self.errors.append("At least 1 METRIC is required")
        
        if not self.ast.output:
            self.errors.append("OUTPUT declaration is required")
        
        if not self.ast.persona:
            self.warnings.append("PERSONA is recommended but not mandatory")
    
    def _validate_persona(self):
        """Validate PERSONA block"""
        if self.ast.persona:
            if not self.ast.persona.value:
                self.errors.append("PERSONA value cannot be empty")
            
            if len(self.ast.persona.value) < 3:
                self.warnings.append("PERSONA value is very short - consider more detail")
    
    def _validate_goals(self):
        """Validate GOAL blocks"""
        goal_names = set()
        
        for goal in self.ast.goals:
            # Check for duplicates
            if goal.name in goal_names:
                self.errors.append(f"Duplicate GOAL name: {goal.name}")
            goal_names.add(goal.name)
            
            # Check naming convention
            if not goal.name[0].isupper():
                self.warnings.append(f"GOAL name '{goal.name}' should start with uppercase (PascalCase)")
            
            # Check value
            if not goal.value:
                self.errors.append(f"GOAL {goal.name} has empty value")
            
            # Recommend quantifiable goals
            if not any(char in goal.value for char in ['$', '%', 'M', 'K']):
                self.warnings.append(f"GOAL {goal.name} lacks quantifiable metric - consider adding dollar/percentage value")
    
    def _validate_metrics(self):
        """Validate METRIC blocks"""
        metric_names = set()
        
        for metric in self.ast.metrics:
            # Check for duplicates
            if metric.name in metric_names:
                self.errors.append(f"Duplicate METRIC name: {metric.name}")
            metric_names.add(metric.name)
            
            # Check naming convention
            if not metric.name[0].isupper():
                self.warnings.append(f"METRIC name '{metric.name}' should start with uppercase (PascalCase)")
            
            # Check value range
            if metric.value < 0:
                self.warnings.append(f"METRIC {metric.name} has negative value: {metric.value}")
            
            if metric.value > 1.0 and 'Risk' in metric.name:
                self.warnings.append(f"METRIC {metric.name} appears to be a risk/drift metric but value > 1.0")
    
    def _validate_rmetrics(self):
        """Validate RMetric blocks"""
        rmetric_names = set()
        metric_names = {m.name for m in self.ast.metrics}
        
        for rmetric in self.ast.rmetrics:
            # Check for duplicates
            if rmetric.name in rmetric_names:
                self.errors.append(f"Duplicate RMetric name: {rmetric.name}")
            rmetric_names.add(rmetric.name)
            
            # Check naming convention
            if not rmetric.name[0].isupper():
                self.warnings.append(f"RMetric name '{rmetric.name}' should start with uppercase (PascalCase)")
            
            # Validate expression references valid metrics
            expr_tokens = re.findall(r'\b[A-Z]\w+\b', rmetric.expr)
            for token in expr_tokens:
                if token not in metric_names and token not in rmetric_names:
                    self.errors.append(f"RMetric {rmetric.name} references undefined METRIC: {token}")
            
            # Check for circular references (basic check)
            if rmetric.name in rmetric.expr:
                self.errors.append(f"RMetric {rmetric.name} contains circular reference to itself")
    
    def _validate_triggers(self):
        """Validate WHEN/THEN trigger blocks"""
        metric_names = {m.name for m in self.ast.metrics}
        
        for trigger in self.ast.triggers:
            # Extract metric name from condition
            condition_match = re.match(r'(\w+)\s*([><=!]+)\s*([\d.]+)', trigger.condition)
            
            if not condition_match:
                self.errors.append(f"Invalid trigger condition syntax: {trigger.condition}")
                continue
            
            metric_name = condition_match.group(1)
            comparator = condition_match.group(2)
            threshold = condition_match.group(3)
            
            # Validate metric exists
            if metric_name not in metric_names:
                self.errors.append(f"Trigger references undefined METRIC: {metric_name}")
            
            # Validate comparator
            valid_comparators = ['>', '<', '>=', '<=', '==', '!=']
            if comparator not in valid_comparators:
                self.errors.append(f"Invalid comparator '{comparator}' in trigger")
            
            # Validate action format
            action_match = re.match(r'(\w+)\(["\']?\w+["\']?\)', trigger.action)
            if not action_match:
                self.warnings.append(f"Action '{trigger.action}' may have invalid syntax")
    
    def _validate_variants(self):
        """Validate VARIANT blocks"""
        # Allow multiple variants - they can be used for different page types/contexts
        for variant in self.ast.variants:
            # Check value
            if not variant.value:
                self.errors.append(f"VARIANT {variant.type} has empty value")
    
    def _validate_output(self):
        """Validate OUTPUT block"""
        if not self.ast.output:
            return
        
        valid_outputs = ['SMS_CAMPAIGN', 'AGENT', 'RMetrics', 'vROI', 'MintSite', 'SK_SKILL']
        
        if self.ast.output not in valid_outputs:
            self.errors.append(f"Invalid OUTPUT type: {self.ast.output}")
        
        # Warn about output-specific requirements
        if self.ast.output == 'MintSite':
            if not self.ast.persona:
                self.warnings.append("MintSite output works best with PERSONA defined")
            
            if not self.ast.variants:
                self.warnings.append("MintSite output can use VARIANTs for page variants")
        
        if self.ast.output == 'SMS_CAMPAIGN':
            if len(self.ast.goals) == 0:
                self.warnings.append("SMS_CAMPAIGN output needs GOALs for message content")
        
        if self.ast.output == 'AGENT':
            if not self.ast.triggers:
                self.warnings.append("AGENT output can use triggers for automation logic")
    
    def _validate_identifier_references(self):
        """Check all identifiers are properly declared before use"""
        metric_names = {m.name for m in self.ast.metrics}
        goal_names = {g.name for g in self.ast.goals}
        
        # Check RMetrics only reference declared metrics
        for rmetric in self.ast.rmetrics:
            tokens = re.findall(r'\b[A-Z]\w+\b', rmetric.expr)
            for token in tokens:
                if token not in metric_names:
                    # Allow some common operators/functions
                    if token not in ['AND', 'OR', 'NOT', 'IF']:
                        self.warnings.append(f"RMetric {rmetric.name} references '{token}' which is not a declared METRIC")
    
    def is_valid(self) -> bool:
        """Returns True if no errors (warnings are OK)"""
        return len(self.errors) == 0
