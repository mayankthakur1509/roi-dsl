"""
MintSite Transpiler
Generates MintSite JSON configuration from ROI-DSL AST
"""

import json
from typing import Dict, Any, List


class MintSiteTranspiler:
    """Transpiles ROI-DSL to MintSite configuration"""
    
    def compile(self, ast) -> str:
        """Generate MintSite JSON configuration"""
        
        site_config = {
            "site_version": "2.1",
            "persona": self._extract_persona(ast),
            "value_framework": {
                "pillars": [{"name": g.name, "value": g.value} for g in ast.goals],
                "metrics": {m.name: m.value for m in ast.metrics},
                "computed_metrics": {rm.name: rm.expr for rm in ast.rmetrics}
            },
            "automation": {
                "triggers": [
                    {
                        "condition": t.condition,
                        "action": t.action,
                        "type": "threshold_alert"
                    }
                    for t in ast.triggers
                ]
            },
            "page_variants": self._extract_variants(ast),
            "hero_section": self._build_hero(ast),
            "value_props": self._build_value_props(ast),
            "case_studies": self._build_case_studies(ast),
            "cta": self._build_cta(ast),
            "seo": self._build_seo(ast)
        }
        
        return json.dumps(site_config, indent=2)
    
    def _extract_persona(self, ast) -> Dict[str, str]:
        """Extract persona information"""
        if ast.persona:
            return {
                "role": ast.persona.name,
                "description": ast.persona.value,
                "target_vertical": self._infer_vertical(ast.persona.value)
            }
        return {"role": "Unknown", "description": "", "target_vertical": "general"}
    
    def _extract_variants(self, ast) -> Dict[str, Any]:
        """Extract page variants"""
        variants = {
            "hero": None,
            "resume": None,
            "cta": None
        }
        
        for variant in ast.variants:
            if variant.type == "Hero":
                variants["hero"] = variant.value
            elif variant.type == "Resume":
                variants["resume"] = variant.value
            elif variant.type == "CTA":
                variants["cta"] = variant.value
        
        return variants
    
    def _build_hero(self, ast) -> Dict[str, Any]:
        """Build hero section"""
        hero_variant = next((v.value for v in ast.variants if v.type == "Hero"), None)
        
        primary_goal = ast.goals[0] if ast.goals else None
        
        return {
            "headline": hero_variant or (ast.persona.value if ast.persona else "Transform Your Business"),
            "subheadline": primary_goal.value if primary_goal else "Achieve measurable results",
            "background_theme": "professional",
            "cta_primary": next((v.value for v in ast.variants if v.type == "CTA"), "Get Started")
        }
    
    def _build_value_props(self, ast) -> List[Dict[str, Any]]:
        """Build value proposition blocks"""
        props = []
        
        for goal in ast.goals:
            props.append({
                "title": goal.name,
                "description": goal.value,
                "icon": self._infer_icon(goal.value),
                "quantified": "$" in goal.value or "%" in goal.value
            })
        
        return props
    
    def _build_case_studies(self, ast) -> List[Dict[str, Any]]:
        """Build case study placeholders"""
        # Generate based on goals
        case_studies = []
        
        for i, goal in enumerate(ast.goals[:3], 1):  # Max 3 case studies
            case_studies.append({
                "case_id": f"case_{i}",
                "industry": self._infer_vertical(ast.persona.value if ast.persona else ""),
                "challenge": goal.value,
                "result": f"Achieved {goal.name}",
                "testimonial_placeholder": True
            })
        
        return case_studies
    
    def _build_cta(self, ast) -> Dict[str, str]:
        """Build call-to-action configuration"""
        cta_variant = next((v.value for v in ast.variants if v.type == "CTA"), "Schedule Consultation")
        
        return {
            "primary_text": cta_variant,
            "secondary_text": "Learn More",
            "urgency_message": self._generate_urgency(ast),
            "button_style": "prominent"
        }
    
    def _build_seo(self, ast) -> Dict[str, Any]:
        """Build SEO metadata"""
        persona_desc = ast.persona.value if ast.persona else "business transformation"
        primary_goal = ast.goals[0].value if ast.goals else ""
        
        return {
            "title": f"{persona_desc} - {primary_goal}",
            "meta_description": f"Help {persona_desc} achieve {primary_goal}. Proven framework with measurable results.",
            "keywords": [
                ast.persona.value if ast.persona else "",
                *[g.name for g in ast.goals]
            ],
            "og_type": "website"
        }
    
    def _infer_vertical(self, text: str) -> str:
        """Infer industry vertical from text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['clinical', 'trial', 'cro', 'pharma']):
            return "clinical_research"
        elif any(word in text_lower for word in ['saas', 'software', 'tech']):
            return "technology"
        elif any(word in text_lower for word in ['manufacturing', 'supply', 'operations']):
            return "manufacturing"
        elif any(word in text_lower for word in ['finance', 'banking', 'investment']):
            return "financial"
        else:
            return "professional_services"
    
    def _infer_icon(self, goal_text: str) -> str:
        """Infer appropriate icon from goal text"""
        text_lower = goal_text.lower()
        
        if any(word in text_lower for word in ['cost', 'save', 'burn']):
            return "dollar-sign"
        elif any(word in text_lower for word in ['time', 'timeline', 'delay']):
            return "clock"
        elif any(word in text_lower for word in ['control', 'oversight', 'manage']):
            return "shield-check"
        elif any(word in text_lower for word in ['risk', 'compliance']):
            return "alert-triangle"
        else:
            return "check-circle"
    
    def _generate_urgency(self, ast) -> str:
        """Generate urgency message based on metrics"""
        high_risk_metrics = [m for m in ast.metrics if m.value > 0.6]
        
        if high_risk_metrics:
            metric_name = high_risk_metrics[0].name
            return f"High {metric_name} detected - Take action now"
        
        return "Limited time offer - Schedule your consultation today"
