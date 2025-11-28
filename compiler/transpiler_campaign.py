"""
SMS Campaign Transpiler
Generates SMS campaign JSON from ROI-DSL AST
"""

import json
from typing import Dict, Any


class SMSCampaignTranspiler:
    """Transpiles ROI-DSL to SMS campaign configuration"""
    
    def compile(self, ast) -> str:
        """Generate SMS campaign JSON"""
        
        campaign = {
            "campaign_type": "value_first_sms",
            "persona": self._extract_persona(ast),
            "messages": self._generate_messages(ast),
            "triggers": self._extract_triggers(ast),
            "metrics": self._extract_metrics(ast),
            "metadata": {
                "goals": [{"name": g.name, "value": g.value} for g in ast.goals],
                "output_type": ast.output
            }
        }
        
        return json.dumps(campaign, indent=2)
    
    def _extract_persona(self, ast) -> Dict[str, str]:
        """Extract persona information"""
        if ast.persona:
            return {
                "role": ast.persona.name,
                "description": ast.persona.value
            }
        return {"role": "Unknown", "description": ""}
    
    def _generate_messages(self, ast) -> list:
        """Generate SMS message sequence"""
        messages = []
        
        # Message 1: Lead with value proposition
        if ast.goals:
            primary_goal = ast.goals[0]
            messages.append({
                "sequence": 1,
                "template": f"Hi {{name}}, {primary_goal.value}. We help with exactly this. Reply LEARN for details.",
                "goal": primary_goal.name
            })
        
        # Message 2: Risk/urgency if metrics present
        if ast.metrics:
            risk_metrics = [m for m in ast.metrics if 'risk' in m.name.lower() or 'drift' in m.name.lower()]
            if risk_metrics:
                metric = risk_metrics[0]
                messages.append({
                    "sequence": 2,
                    "template": f"Your {metric.name} is at {int(metric.value * 100)}%. Most companies see issues at 40%+. Reply SCAN for free assessment.",
                    "trigger_metric": metric.name,
                    "trigger_threshold": 0.4
                })
        
        # Message 3: CTA
        cta_variant = next((v.value for v in ast.variants if v.type == "CTA"), "Get Started")
        messages.append({
            "sequence": 3,
            "template": f"Ready to take action? {cta_variant}: [LINK]",
            "cta": cta_variant
        })
        
        return messages
    
    def _extract_triggers(self, ast) -> list:
        """Extract automation triggers"""
        triggers = []
        
        for trigger in ast.triggers:
            triggers.append({
                "condition": trigger.condition,
                "action": trigger.action,
                "type": "metric_threshold"
            })
        
        return triggers
    
    def _extract_metrics(self, ast) -> Dict[str, float]:
        """Extract metrics as tracking KPIs"""
        return {m.name: m.value for m in ast.metrics}
