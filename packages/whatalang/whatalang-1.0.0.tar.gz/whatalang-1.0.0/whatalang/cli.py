#!/usr/bin/env python3
"""
Whatalang Command Line Interface
"""

import sys
import os
from pathlib import Path

from .lexer import Lexer
from .parser import Parser
from .reactive import ReactiveInterpreter


def run_whatalang_file(file_path: str, verbose: bool = False) -> int:
    """Run a Whatalang program from a file"""
    try:
        # Read the source file
        with open(file_path, 'r') as f:
            source = f.read()
        
        if verbose:
            print(f"📁 Loading: {file_path}")
            print(f"📝 Source ({len(source)} characters):")
            print("=" * 50)
            print(source)
            print("=" * 50)
            print()
        
        # Lexical Analysis
        if verbose:
            print("🔤 LEXICAL ANALYSIS")
            print("-" * 30)
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        if verbose:
            print(f"Generated {len(tokens)-1} tokens")
        
        # Parsing
        if verbose:
            print("\n🌳 PARSING")
            print("-" * 30)
        
        parser = Parser(tokens)
        program = parser.parse()
        
        if verbose:
            print(f"Generated AST with {len(program.statements)} statements")
        
        # Execution
        if verbose:
            print("\n⚡ EXECUTION")
            print("-" * 30)
        
        interpreter = ReactiveInterpreter()
        output = interpreter.execute(program)
        
        # Display output
        if verbose:
            print("\n📊 OUTPUT:")
            print("-" * 30)
        
        for line in output:
            print(line)
        
        # Show final state if verbose
        if verbose:
            print("\n🎯 FINAL STATE:")
            print("-" * 30)
            final_state = interpreter.get_state()
            if final_state:
                for key, value in final_state.items():
                    print(f"  {key}: {value}")
            else:
                print("  (empty state)")
        
        return 0
        
    except FileNotFoundError:
        print(f"❌ Error: File '{file_path}' not found")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return 1


def run_whatalang_source(source: str, verbose: bool = False) -> int:
    """Run Whatalang source code directly"""
    try:
        if verbose:
            print("📝 SOURCE CODE:")
            print("=" * 50)
            print(source)
            print("=" * 50)
            print()
        
        # Lexical Analysis
        if verbose:
            print("🔤 LEXICAL ANALYSIS")
            print("-" * 30)
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        if verbose:
            print(f"Generated {len(tokens)-1} tokens")
        
        # Parsing
        if verbose:
            print("\n🌳 PARSING")
            print("-" * 30)
        
        parser = Parser(tokens)
        program = parser.parse()
        
        if verbose:
            print(f"Generated AST with {len(program.statements)} statements")
        
        # Execution
        if verbose:
            print("\n⚡ EXECUTION")
            print("-" * 30)
        
        interpreter = ReactiveInterpreter()
        output = interpreter.execute(program)
        
        # Display output
        if verbose:
            print("\n📊 OUTPUT:")
            print("-" * 30)
        
        for line in output:
            print(line)
        
        # Show final state if verbose
        if verbose:
            print("\n🎯 FINAL STATE:")
            print("-" * 30)
            final_state = interpreter.get_state()
            if final_state:
                for key, value in final_state.items():
                    print(f"  {key}: {value}")
            else:
                print("  (empty state)")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return 1


def main():
    """Main entry point for the Whatalang CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Whatalang - A reactive programming language",
        epilog="Examples: whatalang program.wa, whatalang program.what, whatalang program"
    )
    
    parser.add_argument(
        "input", 
        nargs="?", 
        help="Whatalang source file (.wa) or source code"
    )
    
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Show detailed execution information"
    )
    
    parser.add_argument(
        "-e", "--eval", 
        help="Execute Whatalang source code directly"
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version="Whatalang 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Show help if no arguments
    if not args.input and not args.eval:
        parser.print_help()
        return 0
    
    # Execute source code directly
    if args.eval:
        return run_whatalang_source(args.eval, args.verbose)
    
    # Execute file
    if args.input:
        # Check if it's a file path
        if os.path.exists(args.input):
            return run_whatalang_file(args.input, args.verbose)
        else:
            # Try common Whatalang extensions
            for ext in ['', '.wa', '.what']:
                file_path = args.input + ext
                if os.path.exists(file_path):
                    return run_whatalang_file(file_path, args.verbose)
            
            # If no file found, treat as source code
            return run_whatalang_source(args.input, args.verbose)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
