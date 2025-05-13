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
from importlib.metadata import version

def float_range(mini, maxi):
    """Return function handle of an argument type function for
    ArgumentParser checking a float range: mini <= arg <= maxi
      mini - minimum acceptable argument
      maxi - maximum acceptable argument"""

    # Define the function with default arguments
    def float_range_checker(arg):
        """New Type function for argparse - a float within predefined range."""

        try:
            f = float(arg)
        except ValueError:
            raise argparse.ArgumentTypeError("must be a floating point number")
        if f < mini or f > maxi:
            raise argparse.ArgumentTypeError(
                "must be in range [" + str(mini) + " .. " + str(maxi) + "]"
            )
        return f

    # Return function handle to checking function
    return float_range_checker


def main() -> None:
    parser = argparse.ArgumentParser(
        description="OpenRouter CLI - Interact with OpenRouter API"
    )

    parser.add_argument('-v', '--version', action='version', version=version('openrouter-cli'))

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subparser for the "configure" command
    config_parser = subparsers.add_parser(
        "configure", help="Configure OpenRouter API key"
    )
    config_parser.add_argument("--api-key", help="Set the API key")
    config_parser.add_argument("--api-url", help="Set the API endpoint URL")

    chat_parser = subparsers.add_parser("run", help="Model selection")

    chat_parser.add_argument(
        "model",
        nargs="?",
        default=None,
        help="Model to use (e.g., google/gemini-2.5-flash-preview)",
    )

    chat_parser.add_argument(
        "--temperature", type=float_range(0, 1), help="Sampling temperature"
    )
    chat_parser.add_argument(
        "--seed", type=float, help="Seed for deterministic outputs."
    )
    chat_parser.add_argument(
        "--effort",
        choices=["high", "medium", "low"],
        help="OpenAI-style reasoning effort setting",
    )
    chat_parser.add_argument(
        "--system", type=str, help="System prompt to use during the chat."
    )

    chat_parser.add_argument(
        "--no-thinking-stdout",
        action="store_true",
        help="Disable displaying thinking tokens.",
    )

    chat_parser.add_argument(
        "--pretty",
        action="store_true",
        default=None,
        help="Display content as pretty text, even in an non-tty context.",
    )

    chat_parser.add_argument(
        "--raw",
        action="store_false",
        dest="pretty",
        help="Display content as raw text, even in an tty context.",
    )

    models_parser = subparsers.add_parser("models", help="List available models")
    models_parser.add_argument(
        "--raw", action="store_true", help="Print raw JSON response"
    )

    args = parser.parse_args()

    if args.command == "configure":
        configure(args)
    elif args.command == "models":
        list_models(args, config=load_config())
    elif args.command == "run" and args.model is not None:
        if args.pretty is None:
            args.pretty = True if sys.stdout.isatty() else False

        chat(args, config=load_config())
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
