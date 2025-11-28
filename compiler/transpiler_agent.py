"""
AI Agent Transpiler
Generates AI agent configuration from ROI-DSL AST
"""

import json
from typing import Dict, Any, List


class AgentTranspiler:
    """Transpiles ROI-DSL to AI Agent configuration"""
    
    def compile(self, ast) -> str:
        """Generate AI agent configuration JSON"""
        
        agent_config = {
            "agent_type": "roi_qualification_bot",
            "persona": self._build_persona(ast),
            "goals": self._extract_goals(ast),
            "qualification_logic": self._build_qualification(ast),
            "conversation_flow": self._build_flow(ast),
            "automation_rules": self._extract_triggers(ast),
            "escalation_criteria": self._build_escalation(ast),
            "metrics_tracking": {m.name: m.value for m in ast.metrics}
        }
        
        return json.dumps(agent_config, indent=2)
    
    def _build_persona(self, ast) -> Dict[str, Any]:
        """Build agent persona"""
        persona = {
            "name": "ROI Qualification Assistant",
            "role": "value_discovery",
            "tone": "professional_empathetic"
        }
        
        if ast.persona:
            persona["target_persona"] = {
                "role": ast.persona.name,
                "description": ast.persona.value
            }
        
        return persona
    
    def _extract_goals(self, ast) -> List[Dict[str, str]]:
        """Extract goals for agent context"""
        return [
            {
                "goal_id": g.name,
                "description": g.value,
                "type": "pain_avoidance" if any(word in g.value.lower() for word in ['avoid', 'prevent']) else "value_gain"
            }
            for g in ast.goals
        ]
    
    def _build_qualification(self, ast) -> Dict[str, Any]:
        """Build qualification questions based on metrics"""
        questions = []
        
        for metric in ast.metrics:
            question = {
                "metric": metric.name,
                "question": f"On a scale of 0-100, how would you rate your current {metric.name}?",
                "threshold": metric.value,
                "weight": 1.0
            }
            
            # Higher weight for risk metrics
            if 'risk' in metric.name.lower() or 'drift' in metric.name.lower():
                question["weight"] = 1.5
            
            questions.append(question)
        
        return {
            "questions": questions,
            "scoring": {
                "high_priority_threshold": 0.6,
                "medium_priority_threshold": 0.4,
                "low_priority_threshold": 0.2
            }
        }
    
    def _build_flow(self, ast) -> List[Dict[str, Any]]:
        """Build conversation flow"""
        flow = [
            {
                "step": 1,
                "type": "greeting",
                "message": "Hi! I help companies understand their ROI opportunities. Can I ask you a few quick questions?"
            },
            {
                "step": 2,
                "type": "pain_discovery",
                "message": f"I noticed you're interested in {ast.goals[0].value if ast.goals else 'optimizing your operations'}. What's driving this need?"
            },
            {
                "step": 3,
                "type": "qualification",
                "message": "Let me ask a few diagnostic questions to understand your situation better..."
            }
        ]
        
        # Add metric-specific questions
        for i, metric in enumerate(ast.metrics, start=4):
            flow.append({
                "step": i,
                "type": "metric_question",
                "metric": metric.name,
                "message": f"How would you describe your current {metric.name}?"
            })
        
        # Final step
        flow.append({
            "step": len(flow) + 1,
            "type": "recommendation",
            "message": "Based on your answers, I can see some opportunities. Would you like to schedule a detailed ROI assessment?"
        })
        
        return flow
    
    def _extract_triggers(self, ast) -> List[Dict[str, Any]]:
        """Extract automation triggers"""
        return [
            {
                "trigger_id": f"trigger_{i+1}",
                "condition": t.condition,
                "action": t.action,
                "priority": "high" if "risk" in t.condition.lower() else "medium"
            }
            for i, t in enumerate(ast.triggers)
        ]
    
    def _build_escalation(self, ast) -> Dict[str, Any]:
        """Build escalation rules"""
        escalation = {
            "immediate_escalation": [],
            "scheduled_followup": [],
            "nurture_sequence": []
        }
        
        # Check for high-value triggers
        for trigger in ast.triggers:
            if any(word in trigger.condition.lower() for word in ['risk', 'drift', 'delay']):
                escalation["immediate_escalation"].append({
                    "condition": trigger.condition,
                    "reason": "high_risk_detected"
                })
        
        # Add metric-based escalation
        for metric in ast.metrics:
            if metric.value > 0.6:
                escalation["immediate_escalation"].append({
                    "condition": f"{metric.name} > 0.6",
                    "reason": "metric_threshold_exceeded"
                })
        
        return escalation
