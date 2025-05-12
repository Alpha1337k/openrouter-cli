"""
OpenRouter CLI - An Ollama-like command line interface for interacting with OpenRouter API
"""

import argparse
import json
import os
import sys
import requests
from datetime import datetime
from typing import Dict, Any, Optional
import questionary
from configure import load_config, save_config, configure
from list_models import list_models
from chat import chat
from chat_interface import ChatInterface

def main() -> None:
    parser = argparse.ArgumentParser(description="OpenRouter CLI - Interact with OpenRouter API")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subparser for the "configure" command
    config_parser = subparsers.add_parser("configure", help="Configure OpenRouter API key")
    config_parser.add_argument("--api-key", help="Set the API key")
    config_parser.add_argument("--api-url", help="Set the API endpoint URL")

    chat_parser = subparsers.add_parser('run', help='Model selection')

    chat_parser.add_argument('model', nargs='?', default=None, 
                               help='Model to use (e.g., google/gemini2.5)')
    
    chat_parser.add_argument("--temperature", type=float, help="Temperature parameter")

    models_parser = subparsers.add_parser("models", help="List available models")
    models_parser.add_argument("--raw", action="store_true", help="Print raw JSON response")
    
    args = parser.parse_args()

    if args.command == "configure":
        configure(args)
    elif args.command == "models":
        list_models(args, config=load_config())
    elif args.command == "run" and args.model is not None:
        chat(args, config=load_config())
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()