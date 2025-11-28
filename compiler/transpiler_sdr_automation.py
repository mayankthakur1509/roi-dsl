"""
SDR Automation Transpiler
Generates complete outbound SDR automation sequences from ROI-DSL
Supports: Email, LinkedIn, SMS, Phone, AI SDR agents
"""

import json
from typing import Dict, Any, List
import re


class SDRAutomationTranspiler:
    """
    Transpiles ROI-DSL to complete SDR automation config
    Generates multi-channel sequences with AI personalization
    """
    
    def compile(self, ast) -> str:
        """Generate complete SDR automation configuration"""
        
        config = {
            "campaign_version": "2.1",
            "campaign_type": "value_first_outbound",
            
            # Persona & targeting
            "target_persona": self._build_persona(ast),
            "icp_filters": self._build_icp_filters(ast),
            
            # Multi-channel sequences
            "sequences": self._build_sequences(ast),
            
            # AI SDR agent config
            "ai_sdr": self._build_ai_sdr(ast),
            
            # Lead scoring
            "lead_scoring": self._build_lead_scoring(ast),
            
            # Trigger automation
            "triggers": self._build_triggers(ast),
            
            # Integrations
            "integrations": self._build_integrations(ast),
            
            # Analytics
            "tracking": self._build_tracking(ast)
        }
        
        return json.dumps(config, indent=2)
    
    def _build_persona(self, ast) -> Dict[str, Any]:
        """Build target persona for SDR campaigns"""
        persona = {
            "primary_role": ast.persona.name if ast.persona else "Unknown",
            "description": ast.persona.value if ast.persona else "",
            "pain_points": [g.value for g in ast.goals],
            "value_props": self._extract_value_props(ast),
            "firmographic_filters": {
                "company_size": self._infer_company_size(ast),
                "industries": self._infer_industries(ast),
                "technologies": self._infer_technologies(ast)
            }
        }
        
        return persona
    
    def _build_icp_filters(self, ast) -> Dict[str, Any]:
        """Build ideal customer profile filters for targeting"""
        return {
            "job_titles": self._generate_job_titles(ast),
            "seniority_levels": ["Director", "VP", "C-Level"],
            "departments": self._infer_departments(ast),
            "company_size": {
                "min_employees": 50,
                "max_employees": 10000
            },
            "exclude_keywords": ["student", "intern", "retired"],
            "intent_signals": self._build_intent_signals(ast)
        }
    
    def _build_sequences(self, ast) -> Dict[str, List[Dict[str, Any]]]:
        """Build multi-channel outbound sequences"""
        
        sequences = {
            "email": self._build_email_sequence(ast),
            "linkedin": self._build_linkedin_sequence(ast),
            "sms": self._build_sms_sequence(ast),
            "phone": self._build_phone_sequence(ast),
            "ai_chat": self._build_ai_chat_sequence(ast)
        }
        
        return sequences
    
    def _build_email_sequence(self, ast) -> List[Dict[str, Any]]:
        """Build 7-touch email sequence"""
        
        primary_goal = ast.goals[0] if ast.goals else None
        primary_metric = ast.metrics[0] if ast.metrics else None
        hero_variant = next((v.value for v in ast.variants if v.type == "Hero"), "Transform Your Operations")
        
        sequence = [
            # Email 1: Problem awareness (Day 0)
            {
                "day": 0,
                "type": "cold_outreach",
                "subject": f"{{first_name}}, are you seeing {primary_metric.name if primary_metric else 'operational drift'}?",
                "body_template": f"""Hi {{{{first_name}}}},

I noticed {{{{company}}}} is in the {{{{industry}}}} space. Based on what I've seen with similar companies, many are facing {primary_goal.value if primary_goal else 'operational challenges'}.

Quick question: Are you currently tracking {primary_metric.name if primary_metric else 'key performance metrics'}?

Most {{{{title}}}}s I work with are surprised to learn their {primary_metric.name if primary_metric else 'metrics'} is typically {int(primary_metric.value * 100) if primary_metric else '45'}% higher than they think.

Worth a 15-minute conversation?

Best,
{{{{sender_name}}}}""",
                "personalization_tokens": ["first_name", "company", "industry", "title", "sender_name"],
                "ai_personalization": True,
                "send_window": "9am-11am local time"
            },
            
            # Email 2: Value prop (Day 2)
            {
                "day": 2,
                "type": "value_follow_up",
                "subject": f"{hero_variant} - {{company}}",
                "body_template": f"""{{{{first_name}}}},

Following up on my previous email about {primary_goal.value if primary_goal else 'your operations'}.

Here's what we typically help {{{{title}}}}s achieve:

{self._format_goals_as_bullets(ast.goals)}

One client ({{{{case_study_company}}}}) saw {self._extract_case_study_result(ast)} in just {self._extract_timeline(ast)}.

Want to see how this applies to {{{{company}}}}?

Calendar link: {{{{calendar_link}}}}

Best,
{{{{sender_name}}}}""",
                "personalization_tokens": ["first_name", "company", "title", "case_study_company", "calendar_link", "sender_name"],
                "ai_personalization": True,
                "send_window": "9am-11am local time",
                "conditions": {
                    "send_if": "no_reply_to_email_1"
                }
            },
            
            # Email 3: Case study (Day 5)
            {
                "day": 5,
                "type": "case_study",
                "subject": "How {{case_study_company}} prevented {{result}}",
                "body_template": self._generate_case_study_email(ast),
                "personalization_tokens": ["first_name", "company", "case_study_company", "result", "sender_name"],
                "ai_personalization": True,
                "send_window": "9am-11am local time",
                "conditions": {
                    "send_if": "no_reply_to_email_2"
                }
            },
            
            # Email 4: Risk/urgency (Day 8)
            {
                "day": 8,
                "type": "risk_urgency",
                "subject": "{{first_name}}, the cost of waiting",
                "body_template": self._generate_risk_email(ast),
                "personalization_tokens": ["first_name", "company", "cost", "sender_name"],
                "ai_personalization": True,
                "send_window": "9am-11am local time",
                "conditions": {
                    "send_if": "no_reply_to_email_3"
                }
            },
            
            # Email 5: Breakup (Day 12)
            {
                "day": 12,
                "type": "breakup",
                "subject": "Closing the loop - {{company}}",
                "body_template": """{{first_name}},

I've reached out a few times about helping {{company}} with {primary_goal}.

I'm assuming this isn't a priority right now, so I'll close the loop on my end.

If anything changes in the next few months and you want to revisit, just reply to this email.

All the best,
{{sender_name}}

P.S. - If you're seeing {metric_name} above {threshold}%, we should definitely talk. That's when most companies see serious issues.""",
                "personalization_tokens": ["first_name", "company", "primary_goal", "metric_name", "threshold", "sender_name"],
                "ai_personalization": True,
                "send_window": "9am-11am local time",
                "conditions": {
                    "send_if": "no_reply_to_email_4"
                }
            },
            
            # Email 6: Re-engagement (Day 30)
            {
                "day": 30,
                "type": "re_engagement",
                "subject": "New data on {{metric_name}} - {{industry}}",
                "body_template": self._generate_reengagement_email(ast),
                "personalization_tokens": ["first_name", "company", "metric_name", "industry", "sender_name"],
                "ai_personalization": True,
                "send_window": "9am-11am local time",
                "conditions": {
                    "send_if": "no_reply_to_sequence"
                }
            }
        ]
        
        return sequence
    
    def _build_linkedin_sequence(self, ast) -> List[Dict[str, Any]]:
        """Build LinkedIn outreach sequence"""
        
        return [
            # Step 1: Connection request (Day 0)
            {
                "day": 0,
                "type": "connection_request",
                "message_template": f"""Hi {{{{first_name}}}},

I help {{{{title}}}}s in {{{{industry}}}} with {ast.goals[0].value if ast.goals else 'operational excellence'}. 

Would love to connect and share some insights relevant to {{{{company}}}}.

Best,
{{{{sender_name}}}}""",
                "personalization_tokens": ["first_name", "title", "industry", "company", "sender_name"],
                "note_character_limit": 300
            },
            
            # Step 2: Value message (Day 3 after connection)
            {
                "day": 3,
                "type": "value_message",
                "condition": "connection_accepted",
                "message_template": f"""Thanks for connecting, {{{{first_name}}}}!

I noticed {{{{company}}}} is {self._infer_company_activity(ast)}. 

We've helped similar companies achieve:
{self._format_goals_as_bullets(ast.goals, max_items=3)}

Worth a quick chat to see if there's a fit?

My calendar: {{{{calendar_link}}}}""",
                "personalization_tokens": ["first_name", "company", "calendar_link"],
                "ai_personalization": True
            },
            
            # Step 3: Content share (Day 7)
            {
                "day": 7,
                "type": "content_share",
                "condition": "no_reply_to_message",
                "message_template": """Thought you might find this relevant - just published a case study on how {{case_study_company}} {case_study_result}.

{{content_link}}

Let me know what you think!""",
                "personalization_tokens": ["case_study_company", "case_study_result", "content_link"],
                "ai_personalization": True
            },
            
            # Step 4: Profile engagement
            {
                "day": 1,
                "type": "profile_engagement",
                "actions": [
                    "view_profile",
                    "like_recent_post",
                    "comment_on_post"
                ],
                "comment_template": "Great point about {{post_topic}}. We've seen similar patterns with {{industry}} companies.",
                "ai_personalization": True
            }
        ]
    
    def _build_sms_sequence(self, ast) -> List[Dict[str, Any]]:
        """Build SMS sequence (for opted-in contacts only)"""
        
        return [
            {
                "day": 0,
                "type": "intro_sms",
                "message_template": f"Hi {{{{first_name}}}}, {ast.goals[0].value if ast.goals else 'quick question about your operations'}. Are you the right person to discuss this? Reply YES or NO.",
                "character_limit": 160,
                "send_window": "10am-4pm local time",
                "require_opt_in": True
            },
            {
                "day": 1,
                "type": "value_sms",
                "condition": "replied_yes",
                "message_template": "Great! We help companies prevent {risk}. Can I send you a quick 60-sec ROI calculator? Reply CALC for link.",
                "character_limit": 160,
                "send_window": "10am-4pm local time"
            },
            {
                "day": 2,
                "type": "calendar_sms",
                "condition": "engaged",
                "message_template": "Based on your input, I see {{estimated_value}}. Worth a 15-min call? {{calendar_link}}",
                "character_limit": 160,
                "send_window": "10am-4pm local time"
            }
        ]
    
    def _build_phone_sequence(self, ast) -> List[Dict[str, Any]]:
        """Build phone call sequence with scripts"""
        
        return [
            {
                "attempt": 1,
                "day": 3,
                "type": "discovery_call",
                "call_script": {
                    "opener": f"Hi {{{{first_name}}}}, this is {{{{caller_name}}}} from {{{{company}}}}. I sent you an email about {ast.goals[0].value if ast.goals else 'operational improvements'}. Do you have 2 minutes?",
                    "pitch": f"We help {{{{title}}}}s prevent {self._extract_primary_risk(ast)}. Quick question: are you currently tracking {ast.metrics[0].name if ast.metrics else 'key metrics'}?",
                    "qualifying_questions": [
                        f"How would you rate your current {m.name}?" for m in ast.metrics[:3]
                    ],
                    "objection_handlers": {
                        "no_time": "I understand. Can I send you a 60-second ROI calculator instead? Takes less time than this call.",
                        "not_interested": "No problem. Just out of curiosity, what's your current approach to {primary_goal}?",
                        "send_info": "Happy to. But quick question first - if you could solve {primary_goal} in the next 30 days, would that be valuable?"
                    },
                    "close": "Based on what you shared, I think there's a fit. Can we schedule 15 minutes next week to dive deeper?"
                },
                "voicemail_script": f"Hi {{{{first_name}}}}, {{{{caller_name}}}} here. Quick question about {ast.goals[0].value if ast.goals else 'your operations'}. I'll send details via email. My direct line is {{{{phone}}}}.",
                "call_window": "10am-4pm local time",
                "max_attempts": 3
            }
        ]
    
    def _build_ai_chat_sequence(self, ast) -> List[Dict[str, Any]]:
        """Build AI SDR chat bot sequence"""
        
        return [
            {
                "trigger": "website_visit",
                "type": "proactive_chat",
                "delay_seconds": 15,
                "message": f"Hi! I noticed you're looking at {ast.goals[0].value if ast.goals else 'our services'}. I'm an AI assistant - can I answer any questions?",
                "conversation_flow": self._build_chat_flow(ast)
            },
            {
                "trigger": "form_abandonment",
                "type": "recovery_chat",
                "delay_seconds": 5,
                "message": "Before you go - quick question: what's your biggest challenge with {pain_point}?",
                "conversation_flow": self._build_chat_flow(ast)
            }
        ]
    
    def _build_ai_sdr(self, ast) -> Dict[str, Any]:
        """Build AI SDR agent configuration"""
        
        return {
            "agent_name": "ROI Discovery Agent",
            "personality": {
                "tone": "professional_consultative",
                "empathy_level": "high",
                "persistence_level": "medium"
            },
            "capabilities": {
                "email_generation": True,
                "linkedin_generation": True,
                "lead_research": True,
                "objection_handling": True,
                "meeting_booking": True
            },
            "personalization_engine": {
                "use_ai": True,
                "data_sources": [
                    "linkedin_profile",
                    "company_website",
                    "recent_news",
                    "glassdoor_reviews",
                    "tech_stack"
                ],
                "personalization_depth": "deep"
            },
            "qualification_criteria": self._build_qualification_criteria(ast),
            "escalation_rules": {
                "escalate_to_human_if": [
                    "high_intent_signal",
                    "c_level_engagement",
                    "meeting_requested",
                    "objection_unresolved"
                ],
                "slack_notification": True,
                "sms_notification": True
            },
            "learning": {
                "track_what_works": True,
                "a_b_test_messages": True,
                "optimize_send_times": True
            }
        }
    
    def _build_lead_scoring(self, ast) -> Dict[str, Any]:
        """Build lead scoring model"""
        
        return {
            "scoring_model": "weighted_points",
            "max_score": 100,
            "qualification_threshold": 60,
            "factors": {
                "firmographic": {
                    "company_size_match": 15,
                    "industry_match": 10,
                    "technology_match": 10,
                    "revenue_range_match": 10
                },
                "engagement": {
                    "email_open": 2,
                    "email_click": 5,
                    "email_reply": 15,
                    "linkedin_connection": 5,
                    "linkedin_message_reply": 10,
                    "website_visit": 3,
                    "calculator_use": 10,
                    "content_download": 8,
                    "meeting_booked": 25
                },
                "intent_signals": {
                    "searched_relevant_keywords": 10,
                    "visited_pricing_page": 15,
                    "multiple_stakeholders_engaged": 20,
                    "competitor_research": 12
                },
                "pain_indicators": self._build_pain_scoring(ast),
                "decay": {
                    "enabled": True,
                    "decay_rate": "5_points_per_week_no_activity"
                }
            },
            "lifecycle_stages": {
                "0-20": "cold",
                "21-40": "warm",
                "41-60": "qualified",
                "61-80": "hot",
                "81-100": "very_hot"
            }
        }
    
    def _build_triggers(self, ast) -> List[Dict[str, Any]]:
        """Build automation triggers from ROI-DSL"""
        
        triggers = []
        
        # Convert ROI-DSL triggers to SDR actions
        for trigger in ast.triggers:
            triggers.append({
                "trigger_name": f"sdr_{trigger.condition.replace(' ', '_')}",
                "condition": trigger.condition,
                "sdr_actions": self._map_trigger_to_sdr_action(trigger),
                "priority": self._assess_trigger_priority(trigger),
                "notification_channels": ["slack", "sms", "email"]
            })
        
        # Add engagement triggers
        triggers.extend([
            {
                "trigger_name": "high_intent_detected",
                "condition": "lead_score > 70",
                "sdr_actions": [
                    "send_urgent_email",
                    "notify_human_sdr",
                    "attempt_immediate_call"
                ],
                "priority": "immediate"
            },
            {
                "trigger_name": "meeting_no_show",
                "condition": "booked_meeting_not_attended",
                "sdr_actions": [
                    "send_followup_email",
                    "offer_reschedule",
                    "send_sms_if_opted_in"
                ],
                "priority": "high"
            },
            {
                "trigger_name": "competitor_mention",
                "condition": "prospect_mentioned_competitor",
                "sdr_actions": [
                    "send_comparison_content",
                    "schedule_demo",
                    "notify_sales_engineer"
                ],
                "priority": "high"
            }
        ])
        
        return triggers
    
    def _build_integrations(self, ast) -> Dict[str, Any]:
        """Build integration configs"""
        
        return {
            "crm": {
                "platform": "salesforce",  # or HubSpot, Pipedrive
                "sync_fields": [
                    "lead_source",
                    "campaign_name",
                    "sequence_step",
                    "lead_score",
                    "engagement_level",
                    "last_activity"
                ],
                "create_tasks": True,
                "update_lead_status": True
            },
            "email": {
                "platform": "sendgrid",  # or AWS SES, Mailgun
                "track_opens": True,
                "track_clicks": True,
                "track_replies": True
            },
            "linkedin": {
                "platform": "phantombuster",  # or Expandi, LinkedHelper
                "daily_connection_limit": 50,
                "daily_message_limit": 30,
                "humanize_timing": True
            },
            "enrichment": {
                "platform": "clearbit",  # or ZoomInfo, Apollo
                "enrich_on": "lead_creation",
                "append_technographics": True,
                "append_intent_data": True
            },
            "calendar": {
                "platform": "calendly",  # or Chili Piper
                "meeting_types": ["discovery_call", "demo", "assessment"],
                "auto_qualify": True
            },
            "notification": {
                "slack_webhook": "{{SLACK_WEBHOOK_URL}}",
                "sms_provider": "twilio",
                "email_alerts": True
            }
        }
    
    def _build_tracking(self, ast) -> Dict[str, Any]:
        """Build analytics tracking config"""
        
        return {
            "kpis": {
                "outbound": [
                    "emails_sent",
                    "emails_opened",
                    "emails_clicked",
                    "emails_replied",
                    "linkedin_connections_sent",
                    "linkedin_connections_accepted",
                    "linkedin_messages_sent",
                    "linkedin_messages_replied"
                ],
                "conversion": [
                    "leads_qualified",
                    "meetings_booked",
                    "meetings_held",
                    "opportunities_created",
                    "deals_won"
                ],
                "velocity": [
                    "response_time",
                    "time_to_qualification",
                    "time_to_meeting",
                    "time_to_opportunity"
                ]
            },
            "attribution": {
                "model": "first_touch",
                "track_channel_performance": True,
                "track_message_performance": True
            },
            "dashboards": [
                "sdr_activity_dashboard",
                "pipeline_generation_dashboard",
                "roi_attribution_dashboard"
            ]
        }
    
    # ==========================================
    # Helper Methods
    # ==========================================
    
    def _extract_value_props(self, ast) -> List[str]:
        """Extract value propositions from goals"""
        return [g.value for g in ast.goals[:3]]
    
    def _infer_company_size(self, ast) -> str:
        """Infer target company size from context"""
        # Look for keywords in goals/metrics
        text = " ".join([g.value for g in ast.goals])
        
        if any(word in text.lower() for word in ['enterprise', 'global', 'multinational']):
            return "enterprise"
        elif any(word in text.lower() for word in ['mid-market', 'regional']):
            return "mid_market"
        else:
            return "smb"
    
    def _infer_industries(self, ast) -> List[str]:
        """Infer target industries"""
        industries = []
        text = " ".join([g.value for g in ast.goals] + [ast.persona.value if ast.persona else ""])
        
        industry_keywords = {
            "pharmaceutical": ["trial", "clinical", "drug", "fda", "pharma"],
            "healthcare": ["patient", "hospital", "medical", "healthcare"],
            "technology": ["saas", "software", "tech", "cloud"],
            "manufacturing": ["production", "supply chain", "factory"],
            "financial": ["financial", "banking", "investment"]
        }
        
        for industry, keywords in industry_keywords.items():
            if any(kw in text.lower() for kw in keywords):
                industries.append(industry)
        
        return industries or ["technology"]
    
    def _infer_technologies(self, ast) -> List[str]:
        """Infer technologies used by prospects"""
        return ["Salesforce", "HubSpot", "Microsoft Dynamics"]
    
    def _generate_job_titles(self, ast) -> List[str]:
        """Generate target job titles"""
        if ast.persona:
            base_role = ast.persona.name
            titles = [
                base_role,
                f"VP of {base_role}",
                f"Director of {base_role}",
                f"Head of {base_role}",
                f"Chief {base_role} Officer"
            ]
            return titles
        return ["Director", "VP", "C-Level"]
    
    def _infer_departments(self, ast) -> List[str]:
        """Infer target departments"""
        text = " ".join([g.value for g in ast.goals])
        
        if "clinical" in text.lower() or "trial" in text.lower():
            return ["Clinical Operations", "R&D", "Regulatory"]
        elif "operations" in text.lower():
            return ["Operations", "COO Office"]
        elif "sales" in text.lower():
            return ["Sales", "Revenue Operations"]
        
        return ["Operations"]
    
    def _build_intent_signals(self, ast) -> List[str]:
        """Build intent signals to track"""
        return [
            f"searching for {ast.goals[0].name if ast.goals else 'solutions'}",
            "visiting competitor websites",
            "downloading industry reports",
            "attending relevant webinars"
        ]
    
    def _format_goals_as_bullets(self, goals, max_items=None) -> str:
        """Format goals as bullet list"""
        items = goals[:max_items] if max_items else goals
        return "\n".join([f"• {g.value}" for g in items])
    
    def _extract_case_study_result(self, ast) -> str:
        """Extract quantified result from case studies"""
        if ast.case_studies:
            first_case = list(ast.case_studies.values())[0]
            # Extract numbers/percentages
            match = re.search(r'(\$[\d,\.]+[MK]?|\d+%)', first_case)
            if match:
                return match.group(1)
        return "$2.4M saved"
    
    def _extract_timeline(self, ast) -> str:
        """Extract timeline from case studies"""
        if ast.case_studies:
            first_case = list(ast.case_studies.values())[0]
            match = re.search(r'(\d+)\s+(days?|weeks?|months?)', first_case.lower())
            if match:
                return f"{match.group(1)} {match.group(2)}"
        return "90 days"
    
    def _generate_case_study_email(self, ast) -> str:
        """Generate case study email body"""
        if ast.case_studies:
            case_name = list(ast.case_studies.keys())[0]
            case_desc = list(ast.case_studies.values())[0]
            
            return f"""{{{{first_name}}}},

Wanted to share a quick case study that might resonate.

**{case_name}**: {case_desc}

The situation sounds similar to what {{{{company}}}} might be facing.

Happy to walk you through the details if you're interested.

Best time for a quick call?

{{{{sender_name}}}}"""
        
        return "Case study email"
    
    def _generate_risk_email(self, ast) -> str:
        """Generate risk/urgency email"""
        primary_metric = ast.metrics[0] if ast.metrics else None
        
        if primary_metric:
            return f"""{{{{first_name}}}},

Quick note on timing.

Based on industry data, when {primary_metric.name} reaches {int(primary_metric.value * 100)}%, companies typically see {{{{negative_outcome}}}} within 60-90 days.

Not trying to create urgency artificially - just sharing what we've observed.

If you're already above {int(primary_metric.value * 100)}%, worth having a conversation sooner rather than later.

Calendar: {{{{calendar_link}}}}

{{{{sender_name}}}}"""
        
        return "Risk email"
    
    def _generate_reengagement_email(self, ast) -> str:
        """Generate re-engagement email"""
        return """{{first_name}},

We haven't connected in a month, but wanted to share some new data we just published on {{metric_name}} in the {{industry}} space.

Key finding: Companies that address this early see {{benefit}}.

Thought it might be relevant to {{company}}.

Link: {{content_link}}

Let me know if you want to discuss.

{{sender_name}}"""
    
    def _infer_company_activity(self, ast) -> str:
        """Infer what the company is doing based on context"""
        return "growing rapidly" 
    
    def _extract_primary_risk(self, ast) -> str:
        """Extract primary risk from goals"""
        if ast.goals:
            first_goal = ast.goals[0].value
            if '$' in first_goal:
                # Extract dollar amount
                match = re.search(r'\$[\d,\.]+[MK]?', first_goal)
                if match:
                    return f"{match.group(0)} in losses"
        return "operational issues"
    
    def _build_chat_flow(self, ast) -> List[Dict[str, Any]]:
        """Build AI chat conversation flow"""
        return [
            {
                "step": 1,
                "type": "greeting",
                "message": "Hi! What brings you here today?"
            },
            {
                "step": 2,
                "type": "qualification",
                "message": f"I help companies with {ast.goals[0].value if ast.goals else 'operations'}. Is this relevant to you?"
            },
            {
                "step": 3,
                "type": "discovery",
                "questions": [f"How would you describe your {m.name}?" for m in ast.metrics[:3]]
            },
            {
                "step": 4,
                "type": "recommendation",
                "message": "Based on what you shared, I think we can help. Want to schedule a call?"
            }
        ]
    
    def _build_qualification_criteria(self, ast) -> Dict[str, Any]:
        """Build qualification criteria"""
        return {
            "must_have": [
                "company_size_match",
                "budget_available",
                "decision_maker_involved"
            ],
            "nice_to_have": [
                "current_pain_point",
                "active_project",
                "competitor_dissatisfaction"
            ],
            "disqualifiers": [
                "no_budget",
                "no_authority",
                "no_need",
                "wrong_company_size"
            ]
        }
    
    def _build_pain_scoring(self, ast) -> Dict[str, int]:
        """Build pain point scoring from metrics"""
        scoring = {}
        for metric in ast.metrics:
            scoring[f"{metric.name}_above_threshold"] = int(metric.value * 20)
        return scoring
    
    def _map_trigger_to_sdr_action(self, trigger) -> List[str]:
        """Map ROI-DSL trigger to SDR actions"""
        action = trigger.action.lower()
        
        if "escalate" in action:
            return ["notify_human_sdr", "send_urgent_email", "attempt_call"]
        elif "alert" in action:
            return ["send_email", "update_lead_score", "add_to_sequence"]
        elif "notify" in action:
            return ["send_email", "slack_notification"]
        else:
            return ["log_event"]
    
    def _assess_trigger_priority(self, trigger) -> str:
        """Assess trigger priority"""
        condition = trigger.condition.lower()
        
        if any(word in condition for word in ['risk', 'critical', 'urgent']):
            return "immediate"
        elif any(word in condition for word in ['high', 'important']):
            return "high"
        else:
            return "medium"
