# 🚀 ROI-DSL Compiler - Quick Start Guide

## Installation (30 seconds)

```bash
cd roi-dsl-compiler
pip install -e .
```

## Basic Usage

### 1. Validate Your First .roi File

```bash
python3 roi_compile.py validate examples/clinical_trial_sponsor.roi
```

Expected output:
```
============================================================
               ROI-DSL Validator
============================================================

ℹ Parsing...
✓ Parse successful
ℹ Validating...
✓ ✓ Validation passed - file is valid ROI-DSL
```

### 2. Preview What Will Be Generated

```bash
python3 roi_compile.py preview examples/clinical_trial_sponsor.roi
```

### 3. Compile to All Outputs

```bash
python3 roi_compile.py compile examples/clinical_trial_sponsor.roi
```

Expected output:
```
============================================================
               ROI-DSL Compiler v2.1
============================================================

[1/5] Validating input file...
✓ Loaded 456 characters from examples/clinical_trial_sponsor.roi

[2/5] Parsing ROI-DSL syntax...
✓ Parse complete - AST generated

[3/5] Validating semantic rules...
✓ Validation passed - no semantic errors

[4/5] Analyzing value framework...
✓ Analysis complete

[5/5] Generating downstream assets...
✓   Generated: outputs/mintsite/site_config.json
✓   Generated: outputs/agents/ai_agent_config.json
✓   Generated: outputs/campaigns/sms_campaign.json

============================================================
               Compilation Summary
============================================================
✓ Successfully generated 3 output(s)

  📄 outputs/mintsite/site_config.json
  📄 outputs/agents/ai_agent_config.json
  📄 outputs/campaigns/sms_campaign.json

Output directory: outputs/
```

### 4. View Generated Files

```bash
cat outputs/mintsite/site_config.json
```

## Common Commands

### Validate Only (No Output)
```bash
python3 roi_compile.py validate your_file.roi
```

### Compile with Verbose Output
```bash
python3 roi_compile.py compile your_file.roi --verbose
```

### Generate Only MintSite
```bash
python3 roi_compile.py compile your_file.roi --output mintsite
```

### Watch Mode (Auto-Recompile on Save)
```bash
python3 roi_compile.py compile your_file.roi --watch
```

### Dry Run (Validate Without Files)
```bash
python3 roi_compile.py compile your_file.roi --dry-run
```

## Your First .roi File

Create `my_first.roi`:

```roi
PERSONA Buyer: "VP Engineering"

GOAL CostReduction: "Reduce infrastructure costs 30%"
GOAL TimeRecovery: "Save 20 hours/week in manual work"

METRIC CurrentCost: 0.65
METRIC ManualWork: 0.75

RMetric TotalPain: "CurrentCost * 0.6 + ManualWork * 0.4"

WHEN CurrentCost > 0.60 THEN escalate("finance")
WHEN ManualWork > 0.70 THEN alert("ops")

VARIANT Hero: "Engineering Leader"
VARIANT CTA: "Cost Calculator"

OUTPUT MintSite
```

Then compile it:

```bash
python3 roi_compile.py compile my_first.roi
```

## Testing the CLI

Run the test suite:

```bash
python3 test_cli.py
```

This will:
1. Validate the example file
2. Preview outputs
3. Compile all output types
4. Verify generated files

## Output Directory Structure

After compilation, you'll find:

```
outputs/
├── mintsite/
│   └── site_config.json         # Landing page configuration
├── agents/
│   └── ai_agent_config.json     # AI bot configuration
├── campaigns/
│   └── sms_campaign.json        # SMS sequences
├── rmetrics/
│   └── metrics_config.json      # KPI dashboard config
├── vroi/
│   └── vroi_calculator.json     # ROI calculator config
└── skills/
    └── semantic_skill.txt       # Semantic Kernel skill
```

## Next Steps

1. **Customize your .roi file** - Add your persona, goals, and metrics
2. **Run compilation** - Generate all downstream assets
3. **Integrate outputs** - Use JSON configs in your apps
4. **Iterate** - Use watch mode for rapid development

## Getting Help

```bash
# General help
python3 roi_compile.py --help

# Command-specific help
python3 roi_compile.py compile --help
python3 roi_compile.py validate --help
python3 roi_compile.py preview --help
```

## Troubleshooting

### "Module not found" error
```bash
pip install -e .
```

### "Permission denied" error
```bash
chmod +x roi_compile.py
```

### Syntax errors in .roi file
```bash
python3 roi_compile.py validate your_file.roi --verbose
```

This will show exactly which line has the syntax error.

---

**You're ready to go!** 🎉

Start with the example file, then create your own `.roi` files for your specific use cases.
