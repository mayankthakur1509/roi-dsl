#!/usr/bin/env python3
"""
ROI-DSL Compiler CLI v2.1
Command-line interface for compiling ROI-DSL files into downstream assets.

Usage:
    roi compile input.roi
    roi compile input.roi --output mintsite
    roi compile input.roi --watch
    roi validate input.roi
    roi preview input.roi
"""

import sys
import os
import argparse
import time
from pathlib import Path
from typing import Optional, List
import json

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def print_step(step: int, total: int, text: str):
    """Print compilation step"""
    print(f"{Colors.OKBLUE}[{step}/{total}]{Colors.ENDC} {text}")


class ROICompilerCLI:
    """Main CLI controller for ROI-DSL compiler"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.compiler_dir = self.base_dir / "compiler"
        self.output_dir = self.base_dir / "outputs"
        self.examples_dir = self.base_dir / "examples"
        
        # Ensure output directories exist
        self._setup_directories()
    
    def _setup_directories(self):
        """Create output directory structure"""
        dirs = [
            self.output_dir / "campaigns",
            self.output_dir / "agents",
            self.output_dir / "rmetrics",
            self.output_dir / "vroi",
            self.output_dir / "mintsite",
            self.output_dir / "skills",
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    def compile_file(self, input_file: str, output_types: Optional[List[str]] = None, 
                    verbose: bool = False, dry_run: bool = False):
        """
        Compile a .roi file into downstream assets
        
        Args:
            input_file: Path to .roi input file
            output_types: Specific output types to generate (None = all)
            verbose: Show detailed compilation steps
            dry_run: Validate without generating outputs
        """
        print_header("ROI-DSL Compiler v2.1")
        
        # Step 1: Validate input file
        print_step(1, 5, "Validating input file...")
        
        if not os.path.exists(input_file):
            print_error(f"Input file not found: {input_file}")
            return False
        
        if not input_file.endswith('.roi'):
            print_warning("Input file should have .roi extension")
        
        try:
            with open(input_file, 'r') as f:
                roi_content = f.read()
        except Exception as e:
            print_error(f"Failed to read input file: {e}")
            return False
        
        print_success(f"Loaded {len(roi_content)} characters from {input_file}")
        
        # Step 2: Parse ROI-DSL
        print_step(2, 5, "Parsing ROI-DSL syntax...")
        
        try:
            from compiler.parser import ROIDSLParser
            parser = ROIDSLParser(roi_content)
            ast = parser.parse()
            
            if verbose:
                print_info(f"  Found {len(ast.goals)} GOALs")
                print_info(f"  Found {len(ast.metrics)} METRICs")
                print_info(f"  Found {len(ast.rmetrics)} RMetrics")
                print_info(f"  Found {len(ast.triggers)} WHEN/THEN triggers")
                print_info(f"  Output type: {ast.output}")
            
            print_success("Parse complete - AST generated")
            
        except Exception as e:
            print_error(f"Parse failed: {e}")
            if verbose:
                import traceback
                print(traceback.format_exc())
            return False
        
        # Step 3: Validate semantic rules
        print_step(3, 5, "Validating semantic rules...")
        
        try:
            from compiler.validator import ROIValidator
            validator = ROIValidator(ast)
            validation_result = validator.validate()
            
            if validation_result.get('errors'):
                for error in validation_result['errors']:
                    print_error(f"  {error}")
                return False
            
            if validation_result.get('warnings'):
                for warning in validation_result['warnings']:
                    print_warning(f"  {warning}")
            
            print_success("Validation passed - no semantic errors")
            
        except Exception as e:
            print_error(f"Validation failed: {e}")
            return False
        
        if dry_run:
            print_info("Dry run - skipping output generation")
            return True
        
        # Step 4: Interpret and analyze
        print_step(4, 5, "Analyzing value framework...")
        
        try:
            from compiler.interpreter import ROIInterpreter
            interpreter = ROIInterpreter(ast)
            analysis = interpreter.analyze()
            
            if verbose:
                print_info(f"  Persona: {analysis.get('persona', 'N/A')}")
                print_info(f"  Primary Goal: {analysis.get('primary_goal', 'N/A')}")
                print_info(f"  Risk Score: {analysis.get('risk_score', 'N/A')}")
            
            print_success("Analysis complete")
            
        except Exception as e:
            print_warning(f"Analysis skipped: {e}")
            analysis = {}
        
        # Step 5: Transpile to outputs
        print_step(5, 5, "Generating downstream assets...")
        
        outputs_generated = []
        
        # Determine which outputs to generate
        requested_outputs = output_types if output_types else self._get_outputs_from_ast(ast)
        
        for output_type in requested_outputs:
            try:
                result = self._transpile_output(ast, output_type, verbose)
                if result:
                    outputs_generated.append(result)
                    print_success(f"  Generated: {result}")
            except Exception as e:
                print_error(f"  Failed to generate {output_type}: {e}")
                if verbose:
                    import traceback
                    print(traceback.format_exc())
        
        # Summary
        print_header("Compilation Summary")
        print_success(f"Successfully generated {len(outputs_generated)} output(s)")
        
        for output in outputs_generated:
            print(f"  📄 {output}")
        
        print(f"\n{Colors.BOLD}Output directory:{Colors.ENDC} {self.output_dir}\n")
        
        return True
    
    def _get_outputs_from_ast(self, ast) -> List[str]:
        """Determine which outputs to generate based on AST"""
        output_map = {
            'SMS_CAMPAIGN': ['campaigns'],
            'AGENT': ['agents'],
            'RMetrics': ['rmetrics'],
            'vROI': ['vroi'],
            'MintSite': ['mintsite', 'agents', 'campaigns'],  # MintSite generates multiple
            'SK_SKILL': ['skills']
        }
        
        return output_map.get(ast.output, ['mintsite'])
    
    def _transpile_output(self, ast, output_type: str, verbose: bool) -> Optional[str]:
        """Transpile AST to specific output type"""
        
        if output_type == 'sdr':
            from compiler.transpiler_sdr_automation import SDRAutomationTranspiler
            transpiler = SDRAutomationTranspiler()
            output_json = transpiler.compile(ast)
            
            sdr_dir = self.output_dir / "sdr"
            sdr_dir.mkdir(exist_ok=True)
            output_file = sdr_dir / "sdr_automation_config.json"
            with open(output_file, 'w') as f:
                f.write(output_json)
            
            return str(output_file.relative_to(self.base_dir))
        
        elif output_type == 'cloudflare':
            from compiler.transpiler_cloudflare import CloudflarePagesTranspiler
            transpiler = CloudflarePagesTranspiler()
            files = transpiler.compile(ast)
            
            # Write all files
            cloudflare_dir = self.output_dir / "cloudflare"
            cloudflare_dir.mkdir(exist_ok=True)
            (cloudflare_dir / "functions").mkdir(exist_ok=True)
            
            for filename, content in files.items():
                filepath = cloudflare_dir / filename
                filepath.parent.mkdir(parents=True, exist_ok=True)
                with open(filepath, 'w') as f:
                    f.write(content)
            
            return str(cloudflare_dir.relative_to(self.base_dir))
        
        elif output_type == 'mintsite':
            from compiler.transpiler_mintsite import MintSiteTranspiler
            transpiler = MintSiteTranspiler()
            result = transpiler.compile(ast)
            
            output_file = self.output_dir / "mintsite" / "site_config.json"
            with open(output_file, 'w') as f:
                f.write(result)
            
            return str(output_file.relative_to(self.base_dir))
        
        elif output_type == 'skills':
            from compiler.transpiler_sk_skill import SKSkillTranspiler
            transpiler = SKSkillTranspiler()
            result = transpiler.compile(ast)
            
            output_file = self.output_dir / "skills" / "semantic_skill.txt"
            with open(output_file, 'w') as f:
                f.write(result)
            
            return str(output_file.relative_to(self.base_dir))
        
        elif output_type == 'campaigns':
            from compiler.transpiler_campaign import SMSCampaignTranspiler
            transpiler = SMSCampaignTranspiler()
            result = transpiler.compile(ast)
            
            output_file = self.output_dir / "campaigns" / "sms_campaign.json"
            with open(output_file, 'w') as f:
                f.write(result)
            
            return str(output_file.relative_to(self.base_dir))
        
        elif output_type == 'agents':
            from compiler.transpiler_agent import AgentTranspiler
            transpiler = AgentTranspiler()
            result = transpiler.compile(ast)
            
            output_file = self.output_dir / "agents" / "ai_agent_config.json"
            with open(output_file, 'w') as f:
                f.write(result)
            
            return str(output_file.relative_to(self.base_dir))
        
        elif output_type == 'rmetrics':
            from compiler.transpiler_rmetrics import RMetricsTranspiler
            transpiler = RMetricsTranspiler()
            result = transpiler.compile(ast)
            
            output_file = self.output_dir / "rmetrics" / "metrics_config.json"
            with open(output_file, 'w') as f:
                f.write(result)
            
            return str(output_file.relative_to(self.base_dir))
        
        elif output_type == 'vroi':
            from compiler.transpiler_vroi import vROITranspiler
            transpiler = vROITranspiler()
            result = transpiler.compile(ast)
            
            output_file = self.output_dir / "vroi" / "vroi_calculator.json"
            with open(output_file, 'w') as f:
                f.write(result)
            
            return str(output_file.relative_to(self.base_dir))
        
        return None
    
    def validate_file(self, input_file: str, verbose: bool = False):
        """Validate a .roi file without compiling"""
        print_header("ROI-DSL Validator")
        
        if not os.path.exists(input_file):
            print_error(f"Input file not found: {input_file}")
            return False
        
        try:
            with open(input_file, 'r') as f:
                roi_content = f.read()
            
            from compiler.parser import ROIDSLParser
            from compiler.validator import ROIValidator
            
            # Parse
            print_info("Parsing...")
            parser = ROIDSLParser(roi_content)
            ast = parser.parse()
            print_success("Parse successful")
            
            # Validate
            print_info("Validating...")
            validator = ROIValidator(ast)
            result = validator.validate()
            
            if result.get('errors'):
                print_error(f"Found {len(result['errors'])} error(s):")
                for error in result['errors']:
                    print(f"  • {error}")
                return False
            
            if result.get('warnings'):
                print_warning(f"Found {len(result['warnings'])} warning(s):")
                for warning in result['warnings']:
                    print(f"  • {warning}")
            
            print_success("✓ Validation passed - file is valid ROI-DSL")
            
            if verbose:
                print("\nFile contents:")
                print(f"  • {len(ast.goals)} GOALs")
                print(f"  • {len(ast.metrics)} METRICs")
                print(f"  • {len(ast.rmetrics)} RMetrics")
                print(f"  • {len(ast.triggers)} Triggers")
                print(f"  • Output: {ast.output}")
            
            return True
            
        except Exception as e:
            print_error(f"Validation failed: {e}")
            if verbose:
                import traceback
                print(traceback.format_exc())
            return False
    
    def preview_file(self, input_file: str):
        """Preview what a .roi file will generate"""
        print_header("ROI-DSL Preview")
        
        if not os.path.exists(input_file):
            print_error(f"Input file not found: {input_file}")
            return False
        
        try:
            with open(input_file, 'r') as f:
                roi_content = f.read()
            
            from compiler.parser import ROIDSLParser
            from compiler.interpreter import ROIInterpreter
            
            parser = ROIDSLParser(roi_content)
            ast = parser.parse()
            
            interpreter = ROIInterpreter(ast)
            analysis = interpreter.analyze()
            
            # Display preview
            print(f"{Colors.BOLD}Persona:{Colors.ENDC} {analysis.get('persona', 'N/A')}")
            print(f"\n{Colors.BOLD}Goals:{Colors.ENDC}")
            for goal in ast.goals:
                print(f"  • {goal.name}: {goal.value}")
            
            print(f"\n{Colors.BOLD}Metrics:{Colors.ENDC}")
            for metric in ast.metrics:
                print(f"  • {metric.name}: {metric.value}")
            
            if ast.rmetrics:
                print(f"\n{Colors.BOLD}Computed Metrics:{Colors.ENDC}")
                for rmetric in ast.rmetrics:
                    print(f"  • {rmetric.name}: {rmetric.expr}")
            
            if ast.triggers:
                print(f"\n{Colors.BOLD}Automation Triggers:{Colors.ENDC}")
                for trigger in ast.triggers:
                    print(f"  • WHEN {trigger.condition} THEN {trigger.action}")
            
            print(f"\n{Colors.BOLD}Output Type:{Colors.ENDC} {ast.output}")
            
            print(f"\n{Colors.BOLD}Will Generate:{Colors.ENDC}")
            outputs = self._get_outputs_from_ast(ast)
            for output in outputs:
                print(f"  📄 {output}/")
            
            return True
            
        except Exception as e:
            print_error(f"Preview failed: {e}")
            return False
    
    def watch_file(self, input_file: str, interval: int = 2):
        """Watch a .roi file and recompile on changes"""
        print_header("ROI-DSL Watch Mode")
        print_info(f"Watching: {input_file}")
        print_info(f"Press Ctrl+C to stop\n")
        
        if not os.path.exists(input_file):
            print_error(f"Input file not found: {input_file}")
            return False
        
        last_modified = os.path.getmtime(input_file)
        
        # Initial compilation
        self.compile_file(input_file, verbose=False)
        
        try:
            while True:
                time.sleep(interval)
                current_modified = os.path.getmtime(input_file)
                
                if current_modified != last_modified:
                    print(f"\n{Colors.WARNING}⟳ File changed - recompiling...{Colors.ENDC}\n")
                    self.compile_file(input_file, verbose=False)
                    last_modified = current_modified
                    
        except KeyboardInterrupt:
            print(f"\n\n{Colors.OKGREEN}Watch mode stopped{Colors.ENDC}")
            return True


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='ROI-DSL Compiler v2.1 - Compile value-first DSL into downstream assets',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  roi compile example.roi                    # Compile ROI-DSL file
  roi compile example.roi --verbose          # Show detailed compilation
  roi compile example.roi --output mintsite  # Generate only MintSite
  roi compile example.roi --dry-run          # Validate without output
  roi validate example.roi                   # Validate syntax only
  roi preview example.roi                    # Preview outputs
  roi compile example.roi --watch            # Watch and auto-recompile
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Compile command
    compile_parser = subparsers.add_parser('compile', help='Compile ROI-DSL file')
    compile_parser.add_argument('input', help='Input .roi file path')
    compile_parser.add_argument('--output', '-o', choices=['mintsite', 'campaigns', 'agents', 'rmetrics', 'vroi', 'skills', 'cloudflare', 'sdr'],
                               help='Specific output type to generate')
    compile_parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed compilation steps')
    compile_parser.add_argument('--dry-run', '-d', action='store_true', help='Validate without generating outputs')
    compile_parser.add_argument('--watch', '-w', action='store_true', help='Watch file and auto-recompile on changes')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate ROI-DSL syntax')
    validate_parser.add_argument('input', help='Input .roi file path')
    validate_parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed validation info')
    
    # Preview command
    preview_parser = subparsers.add_parser('preview', help='Preview compilation outputs')
    preview_parser.add_argument('input', help='Input .roi file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = ROICompilerCLI()
    
    if args.command == 'compile':
        output_types = [args.output] if args.output else None
        
        if args.watch:
            success = cli.watch_file(args.input)
        else:
            success = cli.compile_file(args.input, output_types, args.verbose, args.dry_run)
        
        sys.exit(0 if success else 1)
    
    elif args.command == 'validate':
        success = cli.validate_file(args.input, args.verbose)
        sys.exit(0 if success else 1)
    
    elif args.command == 'preview':
        success = cli.preview_file(args.input)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
