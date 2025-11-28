"""
ROI-DSL Interpreter v2.1
Analyzes AST and extracts business insights
"""

from typing import Dict, Any, List
import re


class ROIInterpreter:
    """Interprets ROI-DSL AST to extract business value insights"""
    
    def __init__(self, ast):
        self.ast = ast
    
    def analyze(self) -> Dict[str, Any]:
        """
        Perform semantic analysis on the AST
        Returns insights about the value framework
        """
        analysis = {
            'persona': self._get_persona_summary(),
            'primary_goal': self._get_primary_goal(),
            'secondary_goals': self._get_secondary_goals(),
            'risk_score': self._calculate_risk_score(),
            'urgency_level': self._assess_urgency(),
            'value_proposition': self._extract_value_prop(),
            'automation_triggers': self._count_triggers(),
            'output_type': self.ast.output,
            'completeness_score': self._assess_completeness(),
        }
        
        return analysis
    
    def _get_persona_summary(self) -> str:
        """Extract persona information"""
        if self.ast.persona:
            return f"{self.ast.persona.name}: {self.ast.persona.value}"
        return "No persona defined"
    
    def _get_primary_goal(self) -> str:
        """Identify the primary goal (typically first or highest value)"""
        if not self.ast.goals:
            return "No goals defined"
        
        # Look for cost-related goals first (highest urgency)
        for goal in self.ast.goals:
            if any(word in goal.value.lower() for word in ['avoid', 'save', 'reduce', 'prevent']):
                return f"{goal.name}: {goal.value}"
        
        # Otherwise return first goal
        return f"{self.ast.goals[0].name}: {self.ast.goals[0].value}"
    
    def _get_secondary_goals(self) -> List[str]:
        """Get all non-primary goals"""
        if len(self.ast.goals) <= 1:
            return []
        
        primary = self._get_primary_goal().split(':')[0]
        return [f"{g.name}: {g.value}" for g in self.ast.goals if g.name != primary]
    
    def _calculate_risk_score(self) -> float:
        """Calculate overall risk score from metrics"""
        if not self.ast.metrics:
            return 0.0
        
        risk_metrics = []
        
        for metric in self.ast.metrics:
            # Identify risk-related metrics
            if any(word in metric.name.lower() for word in ['risk', 'drift', 'delay', 'variance']):
                risk_metrics.append(metric.value)
        
        if not risk_metrics:
            # Use average of all metrics as fallback
            risk_metrics = [m.value for m in self.ast.metrics]
        
        return round(sum(risk_metrics) / len(risk_metrics), 2)
    
    def _assess_urgency(self) -> str:
        """Assess urgency level based on goals and metrics"""
        risk_score = self._calculate_risk_score()
        
        # Check for high-value cost avoidance
        has_high_cost = any(
            any(marker in goal.value for marker in ['$', 'M/', 'million', 'delay'])
            for goal in self.ast.goals
        )
        
        if risk_score > 0.6 and has_high_cost:
            return "CRITICAL"
        elif risk_score > 0.5 or has_high_cost:
            return "HIGH"
        elif risk_score > 0.3:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _extract_value_prop(self) -> str:
        """Extract the core value proposition"""
        if not self.ast.goals:
            return "No value proposition defined"
        
        # Look for quantified goals
        for goal in self.ast.goals:
            if '$' in goal.value:
                return goal.value
        
        # Return first goal if no quantified goal found
        return self.ast.goals[0].value
    
    def _count_triggers(self) -> int:
        """Count automation triggers"""
        return len(self.ast.triggers)
    
    def _assess_completeness(self) -> float:
        """
        Assess how complete/well-defined the ROI-DSL file is
        Returns 0.0 to 1.0
        """
        score = 0.0
        total_checks = 7
        
        # Has persona (1 point)
        if self.ast.persona:
            score += 1
        
        # Has goals (1 point)
        if len(self.ast.goals) >= 1:
            score += 1
        
        # Has multiple goals (0.5 points)
        if len(self.ast.goals) >= 2:
            score += 0.5
        
        # Has metrics (1 point)
        if len(self.ast.metrics) >= 1:
            score += 1
        
        # Has RMetrics (0.5 points)
        if len(self.ast.rmetrics) >= 1:
            score += 0.5
        
        # Has triggers (1 point)
        if len(self.ast.triggers) >= 1:
            score += 1
        
        # Has variants (0.5 points)
        if len(self.ast.variants) >= 1:
            score += 0.5
        
        # Has output (1 point)
        if self.ast.output:
            score += 1
        
        return round(score / total_checks, 2)
    
    def generate_summary(self) -> str:
        """Generate a human-readable summary"""
        analysis = self.analyze()
        
        summary = []
        summary.append(f"=== ROI-DSL Analysis Summary ===\n")
        summary.append(f"Persona: {analysis['persona']}")
        summary.append(f"Primary Goal: {analysis['primary_goal']}")
        
        if analysis['secondary_goals']:
            summary.append(f"Secondary Goals: {len(analysis['secondary_goals'])}")
        
        summary.append(f"\nRisk Score: {analysis['risk_score']}")
        summary.append(f"Urgency Level: {analysis['urgency_level']}")
        summary.append(f"Value Proposition: {analysis['value_proposition']}")
        
        if analysis['automation_triggers'] > 0:
            summary.append(f"\nAutomation: {analysis['automation_triggers']} trigger(s) defined")
        
        summary.append(f"\nOutput Type: {analysis['output_type']}")
        summary.append(f"Completeness: {int(analysis['completeness_score'] * 100)}%")
        
        return '\n'.join(summary)
    
    def extract_dollar_values(self) -> List[float]:
        """Extract all dollar values from goals"""
        dollar_values = []
        
        for goal in self.ast.goals:
            # Match patterns like $2M, $1.8M, $500K, etc.
            matches = re.findall(r'\$(\d+\.?\d*)\s*([MK])', goal.value)
            for match in matches:
                amount = float(match[0])
                multiplier = 1_000_000 if match[1] == 'M' else 1_000
                dollar_values.append(amount * multiplier)
        
        return dollar_values
    
    def calculate_total_value(self) -> float:
        """Calculate total quantified value across all goals"""
        values = self.extract_dollar_values()
        return sum(values) if values else 0.0
    
    def identify_pain_points(self) -> List[str]:
        """Identify pain points from goals"""
        pain_indicators = [
            'avoid', 'prevent', 'reduce', 'eliminate', 'fix',
            'stop', 'control', 'regain', 'restore', 'recover'
        ]
        
        pain_points = []
        
        for goal in self.ast.goals:
            goal_lower = goal.value.lower()
            if any(indicator in goal_lower for indicator in pain_indicators):
                pain_points.append(goal.value)
        
        return pain_points
    
    def suggest_improvements(self) -> List[str]:
        """Suggest improvements to the ROI-DSL file"""
        suggestions = []
        
        if not self.ast.persona:
            suggestions.append("Add PERSONA to better target messaging")
        
        if len(self.ast.goals) < 2:
            suggestions.append("Add secondary goals for richer value narrative")
        
        if len(self.ast.metrics) < 2:
            suggestions.append("Add more metrics for better risk assessment")
        
        if not self.ast.rmetrics:
            suggestions.append("Add RMetrics to compute composite scores")
        
        if not self.ast.triggers:
            suggestions.append("Add WHEN/THEN triggers for automation")
        
        if not self.ast.variants:
            suggestions.append("Add VARIANTs for A/B testing different messaging")
        
        # Check for quantified goals
        dollar_values = self.extract_dollar_values()
        if not dollar_values:
            suggestions.append("Add quantified dollar values to goals for stronger impact")
        
        return suggestions
