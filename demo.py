#!/usr/bin/env python3
"""
ROI-DSL Compiler - Usage Examples
Demonstrates all CLI capabilities
"""

import subprocess
import os
from pathlib import Path

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def run_cmd(cmd_list):
    """Run command and show output"""
    print(f"$ {' '.join(cmd_list)}\n")
    result = subprocess.run(cmd_list, capture_output=True, text=True, cwd="/home/claude/roi_dsl_cli")
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    return result.returncode == 0

def main():
    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║              ROI-DSL COMPILER v2.1 - USAGE EXAMPLES                   ║
║                                                                       ║
║     Transform .roi files into production-ready marketing assets      ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
    """)

    # Example 1: Validation
    print_section("EXAMPLE 1: Validate ROI-DSL Syntax")
    run_cmd(["python3", "roi_compile.py", "validate", "examples/clinical_trial_sponsor.roi"])

    # Example 2: Preview
    print_section("EXAMPLE 2: Preview Compilation Outputs")
    run_cmd(["python3", "roi_compile.py", "preview", "examples/clinical_trial_sponsor.roi"])

    # Example 3: Full Compilation
    print_section("EXAMPLE 3: Full Compilation")
    run_cmd(["python3", "roi_compile.py", "compile", "examples/clinical_trial_sponsor.roi"])

    # Example 4: Verbose Compilation
    print_section("EXAMPLE 4: Verbose Compilation (Detailed Output)")
    run_cmd(["python3", "roi_compile.py", "compile", "examples/clinical_trial_sponsor.roi", "--verbose"])

    # Example 5: Dry Run
    print_section("EXAMPLE 5: Dry Run (Validate Without Generating Files)")
    run_cmd(["python3", "roi_compile.py", "compile", "examples/clinical_trial_sponsor.roi", "--dry-run"])

    # Example 6: Specific Output
    print_section("EXAMPLE 6: Generate Only MintSite")
    run_cmd(["python3", "roi_compile.py", "compile", "examples/clinical_trial_sponsor.roi", "--output", "mintsite"])

    # Show generated files
    print_section("GENERATED OUTPUT FILES")
    outputs_dir = Path("/home/claude/roi_dsl_cli/outputs")
    
    for subdir in outputs_dir.iterdir():
        if subdir.is_dir():
            print(f"\n📁 {subdir.name}/")
            for file in subdir.iterdir():
                if file.is_file():
                    size = file.stat().st_size
                    print(f"  📄 {file.name} ({size} bytes)")

    # Sample output
    print_section("SAMPLE: MintSite Configuration (first 20 lines)")
    mintsite_file = outputs_dir / "mintsite" / "site_config.json"
    if mintsite_file.exists():
        with open(mintsite_file, 'r') as f:
            lines = f.readlines()[:20]
            for line in lines:
                print(line, end='')
        print("\n  ... (truncated)")

    # Final message
    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║                      ✓ ALL EXAMPLES COMPLETED                         ║
║                                                                       ║
║  Next Steps:                                                          ║
║  1. Create your own .roi file                                         ║
║  2. Run: roi compile your_file.roi                                    ║
║  3. Integrate outputs into your applications                          ║
║                                                                       ║
║  Documentation: README.md                                             ║
║  Quick Start:   QUICKSTART.md                                         ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
    """)

if __name__ == '__main__':
    main()
