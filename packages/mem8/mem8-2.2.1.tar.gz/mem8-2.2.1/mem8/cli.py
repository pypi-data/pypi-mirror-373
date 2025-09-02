#!/usr/bin/env python3
"""
mem8 CLI: Memory management for the orchestr8 ecosystem.

This module provides the main entry point for the mem8 CLI, which has been
migrated from Click to Typer for enhanced type safety and developer experience.

The actual implementation is in cli_typer.py, and this module serves as the
main entry point that redirects to the Typer-based implementation.
"""

import os
import sys


def setup_utf8_encoding():
    """Setup UTF-8 encoding for Windows compatibility."""
    # Set environment variables for UTF-8 mode
    os.environ['PYTHONUTF8'] = '1'
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # Configure stdout/stderr streams
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            # Fallback if reconfigure fails
            pass
    
    # Import colorama after setting up encoding
    try:
        import colorama
        colorama.init(autoreset=True)
    except ImportError:
        pass


def main():
    """Entry point for the CLI using Typer."""
    # Setup encoding for Windows compatibility
    setup_utf8_encoding()
    
    # Import and run the Typer-based CLI
    from .cli_typer import typer_app
    typer_app()


if __name__ == "__main__":
    main()