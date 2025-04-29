"""
Command-line interface commands for the Coding Agent.
"""

import argparse
import sys
from typing import List, Optional

from coding_agent.core.model_service import model_service


def handle_model_command(args: List[str]) -> None:
    """
    Handle model-related commands from the command line.
    
    Args:
        args: Command-line arguments for the model command
    """
    parser = argparse.ArgumentParser(description="Manage AI models")
    subparsers = parser.add_subparsers(dest="model_command", help="Model commands")
    
    # Switch model command
    switch_parser = subparsers.add_parser("switch", help="Switch to a different AI provider")
    switch_parser.add_argument("provider", choices=["openai", "anthropic", "google"], 
                              help="The AI provider to switch to")
    
    # Get current model command
    subparsers.add_parser("current", help="Show the current AI provider")
    
    # Parse arguments
    parsed_args = parser.parse_args(args)
    
    # Handle commands
    if parsed_args.model_command == "switch":
        success = model_service.switch_provider(parsed_args.provider)
        if success:
            print(f"Switched to {parsed_args.provider} provider")
        else:
            print(f"Failed to switch to {parsed_args.provider} provider")
            sys.exit(1)
    
    elif parsed_args.model_command == "current":
        current_provider = model_service.get_current_provider()
        print(f"Current AI provider: {current_provider}")
    
    else:
        parser.print_help()


def parse_args(args: List[str]) -> None:
    """
    Parse command-line arguments and dispatch to the appropriate handler.
    
    Args:
        args: Command-line arguments
    """
    parser = argparse.ArgumentParser(description="Coding Agent CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Model command
    model_parser = subparsers.add_parser("model", help="Manage AI models")
    
    # Parse top-level command
    parsed_args, remaining = parser.parse_known_args(args)
    
    # Dispatch to appropriate handler
    if parsed_args.command == "model":
        handle_model_command(remaining)
    else:
        parser.print_help()
