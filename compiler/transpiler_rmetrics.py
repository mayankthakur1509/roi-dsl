"""
RMetrics Transpiler
Generates metrics computation configuration from ROI-DSL AST
"""

import json
from typing import Dict, Any


class RMetricsTranspiler:
    """Transpiles ROI-DSL to RMetrics configuration"""
    
    def compile(self, ast) -> str:
        """Generate RMetrics configuration JSON"""
        
        config = {
            "metrics_engine_version": "2.1",
            "base_metrics": self._extract_base_metrics(ast),
            "computed_metrics": self._extract_computed_metrics(ast),
            "thresholds": self._extract_thresholds(ast),
            "alerts": self._build_alerts(ast),
            "dashboard_config": self._build_dashboard(ast)
        }
        
        return json.dumps(config, indent=2)
    
    def _extract_base_metrics(self, ast) -> Dict[str, Any]:
        """Extract base metrics"""
        metrics = {}
        
        for metric in ast.metrics:
            metrics[metric.name] = {
                "current_value": metric.value,
                "data_type": "float",
                "unit": self._infer_unit(metric.name),
                "display_name": self._format_display_name(metric.name),
                "category": self._categorize_metric(metric.name)
            }
        
        return metrics
    
    def _extract_computed_metrics(self, ast) -> Dict[str, Any]:
        """Extract computed (RMetric) metrics"""
        computed = {}
        
        for rmetric in ast.rmetrics:
            computed[rmetric.name] = {
                "expression": rmetric.expr,
                "dependencies": self._extract_dependencies(rmetric.expr, ast),
                "display_name": self._format_display_name(rmetric.name),
                "computation_type": "formula"
            }
        
        return computed
    
    def _extract_dependencies(self, expr: str, ast) -> list:
        """Extract metric dependencies from expression"""
        import re
        metric_names = {m.name for m in ast.metrics}
        tokens = re.findall(r'\b[A-Z]\w+\b', expr)
        return [t for t in tokens if t in metric_names]
    
    def _extract_thresholds(self, ast) -> Dict[str, Any]:
        """Extract threshold configurations from triggers"""
        thresholds = {}
        
        for trigger in ast.triggers:
            import re
            match = re.match(r'(\w+)\s*([><=!]+)\s*([\d.]+)', trigger.condition)
            if match:
                metric_name = match.group(1)
                operator = match.group(2)
                value = float(match.group(3))
                
                thresholds[metric_name] = {
                    "operator": operator,
                    "threshold": value,
                    "action": trigger.action,
                    "severity": "high" if value > 0.5 else "medium"
                }
        
        return thresholds
    
    def _build_alerts(self, ast) -> list:
        """Build alert configurations"""
        alerts = []
        
        for trigger in ast.triggers:
            import re
            match = re.match(r'(\w+)\s*([><=!]+)\s*([\d.]+)', trigger.condition)
            if match:
                metric_name = match.group(1)
                
                alert = {
                    "alert_id": f"alert_{metric_name}",
                    "metric": metric_name,
                    "condition": trigger.condition,
                    "action": trigger.action,
                    "notification_channels": ["email", "slack"],
                    "frequency": "immediate"
                }
                
                alerts.append(alert)
        
        return alerts
    
    def _build_dashboard(self, ast) -> Dict[str, Any]:
        """Build dashboard configuration"""
        dashboard = {
            "title": f"{ast.persona.value if ast.persona else 'ROI'} Dashboard",
            "widgets": []
        }
        
        # Add metric widgets
        for metric in ast.metrics:
            dashboard["widgets"].append({
                "type": "gauge",
                "metric": metric.name,
                "title": self._format_display_name(metric.name),
                "thresholds": {
                    "good": 0.3,
                    "warning": 0.5,
                    "critical": 0.7
                }
            })
        
        # Add computed metric widgets
        for rmetric in ast.rmetrics:
            dashboard["widgets"].append({
                "type": "score_card",
                "metric": rmetric.name,
                "title": self._format_display_name(rmetric.name),
                "formula": rmetric.expr
            })
        
        return dashboard
    
    def _infer_unit(self, metric_name: str) -> str:
        """Infer unit from metric name"""
        name_lower = metric_name.lower()
        
        if 'percent' in name_lower or 'rate' in name_lower:
            return "percentage"
        elif 'drift' in name_lower or 'risk' in name_lower:
            return "index"
        elif 'time' in name_lower:
            return "days"
        elif 'cost' in name_lower:
            return "dollars"
        else:
            return "score"
    
    def _format_display_name(self, name: str) -> str:
        """Format camelCase to Display Name"""
        import re
        # Insert space before capital letters
        spaced = re.sub(r'([A-Z])', r' \1', name)
        return spaced.strip()
    
    def _categorize_metric(self, metric_name: str) -> str:
        """Categorize metric by type"""
        name_lower = metric_name.lower()
        
        if any(word in name_lower for word in ['risk', 'drift', 'variance']):
            return "risk"
        elif any(word in name_lower for word in ['cost', 'burn', 'spend']):
            return "financial"
        elif any(word in name_lower for word in ['timeline', 'delay', 'schedule']):
            return "temporal"
        elif any(word in name_lower for word in ['quality', 'compliance']):
            return "quality"
        else:
            return "operational"
