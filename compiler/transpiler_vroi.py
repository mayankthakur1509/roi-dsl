"""
vROI (Value-of-Avoiding-Delay) Transpiler
Generates vROI calculator configuration from ROI-DSL AST
"""

import json
import re
from typing import Dict, Any, List


class vROITranspiler:
    """Transpiles ROI-DSL to vROI calculator configuration"""
    
    def compile(self, ast) -> str:
        """Generate vROI calculator JSON"""
        
        calculator = {
            "calculator_type": "value_of_avoiding_delay",
            "persona": self._extract_persona(ast),
            "value_drivers": self._extract_value_drivers(ast),
            "cost_avoidance": self._calculate_cost_avoidance(ast),
            "timeline_model": self._build_timeline_model(ast),
            "calculator_inputs": self._define_inputs(ast),
            "output_format": self._define_output_format(ast)
        }
        
        return json.dumps(calculator, indent=2)
    
    def _extract_persona(self, ast) -> Dict[str, str]:
        """Extract persona for calculator targeting"""
        if ast.persona:
            return {
                "role": ast.persona.name,
                "description": ast.persona.value
            }
        return {"role": "Decision Maker", "description": ""}
    
    def _extract_value_drivers(self, ast) -> List[Dict[str, Any]]:
        """Extract value drivers from goals"""
        drivers = []
        
        for goal in ast.goals:
            # Extract dollar values
            dollar_matches = re.findall(r'\$(\d+\.?\d*)\s*([MK])', goal.value)
            
            for match in dollar_matches:
                amount = float(match[0])
                multiplier = 1_000_000 if match[1] == 'M' else 1_000
                total_value = amount * multiplier
                
                drivers.append({
                    "name": goal.name,
                    "description": goal.value,
                    "monthly_value": total_value,
                    "category": self._categorize_value(goal.value)
                })
        
        return drivers
    
    def _calculate_cost_avoidance(self, ast) -> Dict[str, Any]:
        """Calculate cost avoidance metrics"""
        total_monthly = 0
        breakdown = []
        
        for goal in ast.goals:
            dollar_matches = re.findall(r'\$(\d+\.?\d*)\s*([MK])', goal.value)
            for match in dollar_matches:
                amount = float(match[0])
                multiplier = 1_000_000 if match[1] == 'M' else 1_000
                monthly_value = amount * multiplier
                
                # Check if it's monthly
                if '/mo' in goal.value or 'monthly' in goal.value.lower():
                    total_monthly += monthly_value
                    
                    breakdown.append({
                        "source": goal.name,
                        "monthly_cost": monthly_value,
                        "quarterly_cost": monthly_value * 3,
                        "annual_cost": monthly_value * 12
                    })
        
        return {
            "total_monthly_burn": total_monthly,
            "total_quarterly_burn": total_monthly * 3,
            "total_annual_burn": total_monthly * 12,
            "breakdown": breakdown
        }
    
    def _build_timeline_model(self, ast) -> Dict[str, Any]:
        """Build timeline/delay cost model"""
        # Get timeline risk from metrics
        timeline_risk = 0.0
        for metric in ast.metrics:
            if 'timeline' in metric.name.lower() or 'delay' in metric.name.lower():
                timeline_risk = metric.value
                break
        
        cost_avoidance = self._calculate_cost_avoidance(ast)
        monthly_burn = cost_avoidance.get('total_monthly_burn', 0)
        
        return {
            "current_risk": timeline_risk,
            "delay_scenarios": {
                "1_month_delay": {
                    "probability": timeline_risk,
                    "cost": monthly_burn,
                    "cumulative_cost": monthly_burn
                },
                "3_month_delay": {
                    "probability": timeline_risk * 1.5,
                    "cost": monthly_burn * 3,
                    "cumulative_cost": monthly_burn * 3
                },
                "6_month_delay": {
                    "probability": timeline_risk * 2,
                    "cost": monthly_burn * 6,
                    "cumulative_cost": monthly_burn * 6
                }
            },
            "expected_value_of_action": monthly_burn * timeline_risk
        }
    
    def _define_inputs(self, ast) -> List[Dict[str, Any]]:
        """Define calculator input fields"""
        inputs = []
        
        # Add metric-based inputs
        for metric in ast.metrics:
            inputs.append({
                "field_id": metric.name,
                "label": self._format_label(metric.name),
                "type": "slider",
                "min": 0,
                "max": 1,
                "default": metric.value,
                "step": 0.01,
                "description": f"Current {self._format_label(metric.name)} level"
            })
        
        # Add goal-based inputs
        for goal in ast.goals:
            if '$' in goal.value:
                inputs.append({
                    "field_id": f"{goal.name}_Value",
                    "label": f"{self._format_label(goal.name)} Amount",
                    "type": "currency",
                    "default": self._extract_default_value(goal.value),
                    "description": goal.value
                })
        
        return inputs
    
    def _define_output_format(self, ast) -> Dict[str, Any]:
        """Define calculator output format"""
        return {
            "primary_metric": {
                "label": "Total Cost of Delay",
                "format": "currency",
                "calculation": "sum_of_all_delay_costs"
            },
            "secondary_metrics": [
                {
                    "label": "Monthly Savings",
                    "format": "currency",
                    "calculation": "monthly_burn_rate"
                },
                {
                    "label": "Risk-Adjusted ROI",
                    "format": "percentage",
                    "calculation": "expected_value / investment"
                },
                {
                    "label": "Payback Period",
                    "format": "months",
                    "calculation": "investment / monthly_savings"
                }
            ],
            "visualization": {
                "chart_type": "waterfall",
                "show_scenarios": true,
                "timeline_months": 12
            }
        }
    
    def _categorize_value(self, goal_text: str) -> str:
        """Categorize value type"""
        goal_lower = goal_text.lower()
        
        if any(word in goal_lower for word in ['avoid', 'prevent', 'reduce']):
            return "cost_avoidance"
        elif any(word in goal_lower for word in ['increase', 'improve', 'gain']):
            return "value_gain"
        elif any(word in goal_lower for word in ['restore', 'regain', 'recover']):
            return "recovery"
        else:
            return "optimization"
    
    def _format_label(self, name: str) -> str:
        """Format camelCase to Display Label"""
        import re
        spaced = re.sub(r'([A-Z])', r' \1', name)
        return spaced.strip()
    
    def _extract_default_value(self, goal_text: str) -> float:
        """Extract default dollar value from goal"""
        matches = re.findall(r'\$(\d+\.?\d*)\s*([MK])', goal_text)
        if matches:
            amount = float(matches[0][0])
            multiplier = 1_000_000 if matches[0][1] == 'M' else 1_000
            return amount * multiplier
        return 0
