# ROI-DSL Compiler v2.1 - Complete Package Structure

## 📦 Package Contents

```
roi-dsl-compiler/
│
├── 🚀 ENTRY POINTS
│   ├── roi_compile.py              # Main CLI entry point
│   ├── setup.py                    # Package installation
│   ├── demo.py                     # Usage examples demo
│   └── test_cli.py                 # Test suite
│
├── 📚 DOCUMENTATION
│   ├── README.md                   # Comprehensive documentation
│   ├── QUICKSTART.md               # Quick start guide
│   ├── LICENSE                     # MIT License
│   └── DIRECTORY_STRUCTURE.md      # This file
│
├── 🔧 COMPILER CORE
│   └── compiler/
│       ├── __init__.py             # Package exports
│       ├── parser.py               # ROI-DSL → AST parser
│       ├── validator.py            # Semantic validation
│       ├── interpreter.py          # Business logic analysis
│       ├── transpiler_mintsite.py  # MintSite JSON generator
│       ├── transpiler_campaign.py  # SMS campaign generator
│       ├── transpiler_agent.py     # AI agent generator
│       ├── transpiler_rmetrics.py  # Metrics config generator
│       ├── transpiler_vroi.py      # vROI calculator generator
│       └── transpiler_sk_skill.py  # Semantic Kernel skill generator
│
├── ⚙️ RUNTIME ENGINES
│   └── runtime/
│       ├── rmetrics_engine.py      # Metrics computation
│       └── drift_detector.py       # Drift detection
│
├── 📖 GRAMMAR & SPECS
│   └── grammar/
│       └── roi_dsl_v2.ebnf         # Formal EBNF grammar
│
├── 📝 EXAMPLES
│   └── examples/
│       └── clinical_trial_sponsor.roi  # Complete example
│
└── 📤 OUTPUTS (Generated)
    └── outputs/
        ├── mintsite/               # Landing page configs
        ├── agents/                 # AI agent configs
        ├── campaigns/              # SMS campaigns
        ├── rmetrics/               # Metrics dashboards
        ├── vroi/                   # ROI calculators
        └── skills/                 # Semantic Kernel skills
```

---

## 📋 File Details

### Core Compiler (compiler/)

**parser.py** (230 lines)
- Converts .roi text → Abstract Syntax Tree (AST)
- Handles all ROI-DSL syntax elements
- Exports: `ROIDSLParser`, `ROIDSLAST`, `parse_roi_file()`

**validator.py** (180 lines)
- Semantic validation & guardrails
- Checks mandatory fields, naming conventions
- Detects circular references, undefined identifiers
- Returns: `{'errors': [...], 'warnings': [...]}`

**interpreter.py** (200 lines)
- Extracts business insights from AST
- Calculates risk scores, urgency levels
- Identifies pain points, value drivers
- Suggests improvements

**transpiler_mintsite.py** (180 lines)
- Generates MintSite JSON configuration
- Builds hero sections, value props, CTAs
- Infers icons, verticals, SEO metadata

**transpiler_campaign.py** (90 lines)
- Generates SMS campaign sequences
- Creates trigger-based messaging
- Persona-targeted content

**transpiler_agent.py** (150 lines)
- Generates AI agent configurations
- Builds conversation flows
- Defines escalation rules

**transpiler_rmetrics.py** (140 lines)
- Generates metrics dashboard configs
- Defines alerts, thresholds
- Builds visualization layouts

**transpiler_vroi.py** (150 lines)
- Generates vROI calculator configs
- Models delay costs, timelines
- Defines input/output formats

**transpiler_sk_skill.py** (40 lines)
- Generates Semantic Kernel skills
- Exports persona & goals

---

### Command-Line Interface

**roi_compile.py** (550 lines)
- Main CLI controller
- Commands: `compile`, `validate`, `preview`
- Options: `--verbose`, `--dry-run`, `--watch`, `--output`
- Colored terminal output
- Progress indicators
- Error handling

---

### Runtime Engines

**rmetrics_engine.py** (20 lines)
- Computes RMetric scores
- Formula evaluation

**drift_detector.py** (15 lines)
- Detects metric drift
- Threshold-based alerts

---

## 🎯 Output Formats

### 1. MintSite (JSON)
```json
{
  "site_version": "2.1",
  "persona": {...},
  "value_framework": {...},
  "automation": {...},
  "hero_section": {...},
  "value_props": [...],
  "case_studies": [...],
  "cta": {...},
  "seo": {...}
}
```

### 2. AI Agent (JSON)
```json
{
  "agent_type": "roi_qualification_bot",
  "persona": {...},
  "qualification_logic": {...},
  "conversation_flow": [...],
  "automation_rules": [...],
  "escalation_criteria": {...}
}
```

### 3. SMS Campaign (JSON)
```json
{
  "campaign_type": "value_first_sms",
  "persona": {...},
  "messages": [...],
  "triggers": [...],
  "metrics": {...}
}
```

### 4. RMetrics (JSON)
```json
{
  "metrics_engine_version": "2.1",
  "base_metrics": {...},
  "computed_metrics": {...},
  "thresholds": {...},
  "alerts": [...],
  "dashboard_config": {...}
}
```

### 5. vROI Calculator (JSON)
```json
{
  "calculator_type": "value_of_avoiding_delay",
  "persona": {...},
  "value_drivers": [...],
  "cost_avoidance": {...},
  "timeline_model": {...},
  "calculator_inputs": [...],
  "output_format": {...}
}
```

### 6. Semantic Kernel Skill (TXT)
```ini
[skill]
persona=Sponsor

[task]
Goals=Restore CRO control, Avoid burn cost
Metrics=0.45, 0.67
```

---

## 🔄 Compilation Workflow

```
.roi File
    ↓
[Parser] → AST
    ↓
[Validator] → Errors/Warnings
    ↓
[Interpreter] → Business Insights
    ↓
[Transpilers] → JSON/TXT Outputs
    ↓
outputs/ directory
```

---

## 📊 Code Statistics

| Component      | Files | Lines | Purpose                    |
|----------------|-------|-------|----------------------------|
| CLI            | 1     | 550   | User interface             |
| Compiler Core  | 9     | 1,400 | Parsing & transpilation    |
| Runtime        | 2     | 35    | Computation engines        |
| Examples       | 1     | 25    | Sample .roi files          |
| Documentation  | 4     | 800   | Guides & references        |
| **Total**      | **17**| **2,810** | **Complete system**    |

---

## 🚀 Quick Start Commands

```bash
# Install
pip install -e .

# Validate
python3 roi_compile.py validate examples/clinical_trial_sponsor.roi

# Preview
python3 roi_compile.py preview examples/clinical_trial_sponsor.roi

# Compile
python3 roi_compile.py compile examples/clinical_trial_sponsor.roi

# Verbose compilation
python3 roi_compile.py compile examples/clinical_trial_sponsor.roi --verbose

# Watch mode
python3 roi_compile.py compile examples/clinical_trial_sponsor.roi --watch

# Run tests
python3 test_cli.py

# Run demo
python3 demo.py
```

---

## 🎓 Learning Path

1. **Read** → QUICKSTART.md (5 min)
2. **Study** → examples/clinical_trial_sponsor.roi (2 min)
3. **Run** → `python3 roi_compile.py compile examples/...` (30 sec)
4. **Explore** → outputs/ directory (2 min)
5. **Create** → your_first.roi (10 min)
6. **Compile** → your own .roi file (30 sec)
7. **Reference** → README.md as needed

---

## 🔧 Development

### Adding a New Output Type

1. Create `compiler/transpiler_newtype.py`
2. Implement `compile(self, ast)` method
3. Add to `roi_compile.py` in `_transpile_output()`
4. Add to EBNF grammar (optional)
5. Test with example .roi file

### Extending the Grammar

1. Edit `grammar/roi_dsl_v2.ebnf`
2. Update `compiler/parser.py` parsing logic
3. Update `compiler/validator.py` validation rules
4. Add examples

---

## 📞 Support

- **Docs**: README.md, QUICKSTART.md
- **Issues**: GitHub Issues
- **Email**: dev@hyperaimarketing.com

---

**Built by HyperAIMarketing** | v2.1.0 | MIT License
