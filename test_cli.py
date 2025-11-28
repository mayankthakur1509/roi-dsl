#!/usr/bin/env python3
"""
Test script for ROI-DSL Compiler CLI
Demonstrates all major CLI functions
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and display results"""
    print(f"\n{'='*70}")
    print(f"TEST: {description}")
    print(f"{'='*70}")
    print(f"Command: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0

def main():
    """Run test suite"""
    base_dir = Path(__file__).parent
    example_file = base_dir / "examples" / "clinical_trial_sponsor.roi"
    
    # Ensure example file exists
    if not example_file.exists():
        print(f"ERROR: Example file not found: {example_file}")
        return False
    
    print("\n" + "="*70)
    print("ROI-DSL Compiler CLI - Test Suite")
    print("="*70)
    
    tests = [
        # Test 1: Validate
        (
            ["python3", "roi_compile.py", "validate", str(example_file)],
            "Validate ROI-DSL file"
        ),
        
        # Test 2: Validate with verbose
        (
            ["python3", "roi_compile.py", "validate", str(example_file), "--verbose"],
            "Validate with verbose output"
        ),
        
        # Test 3: Preview
        (
            ["python3", "roi_compile.py", "preview", str(example_file)],
            "Preview compilation outputs"
        ),
        
        # Test 4: Dry run compilation
        (
            ["python3", "roi_compile.py", "compile", str(example_file), "--dry-run"],
            "Dry run compilation (no output files)"
        ),
        
        # Test 5: Full compilation
        (
            ["python3", "roi_compile.py", "compile", str(example_file)],
            "Full compilation"
        ),
        
        # Test 6: Compilation with verbose
        (
            ["python3", "roi_compile.py", "compile", str(example_file), "--verbose"],
            "Compilation with verbose output"
        ),
        
        # Test 7: Specific output type
        (
            ["python3", "roi_compile.py", "compile", str(example_file), "--output", "mintsite"],
            "Compile only MintSite output"
        ),
    ]
    
    results = []
    for cmd, description in tests:
        success = run_command(cmd, description)
        results.append((description, success))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for description, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} - {description}")
    
    print(f"\n{passed}/{total} tests passed")
    
    # Check output files
    print("\n" + "="*70)
    print("OUTPUT FILES CHECK")
    print("="*70)
    
    output_dir = base_dir / "outputs"
    expected_files = [
        "mintsite/site_config.json",
        "agents/ai_agent_config.json",
        "campaigns/sms_campaign.json",
        "rmetrics/metrics_config.json",
        "vroi/vroi_calculator.json",
        "skills/semantic_skill.txt"
    ]
    
    for file_path in expected_files:
        full_path = output_dir / file_path
        exists = full_path.exists()
        status = "✓" if exists else "✗"
        print(f"{status} {file_path}")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
