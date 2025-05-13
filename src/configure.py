from typing import Dict
import json
import os
import sys
import argparse


def load_config() -> Dict[str, str]:
    """Load configuration from file or environment variables."""
    config = {}

    # Check for config file
    config_path = os.path.expanduser("~/.openrouter-cli/.config")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except json.JSONDecodeError:
            print("Error: Invalid config file format")
            sys.exit(1)
    else:
        print("Error: could not load configuration. Did you run `openrouter-cli configure`?")
        exit(1)

    return config


def save_config(config: Dict[str, str]) -> None:
    """Save configuration to file."""

    os.makedirs(os.path.expanduser("~/.openrouter-cli"), exist_ok=True)

    config_path = os.path.expanduser("~/.openrouter-cli/.config")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    os.chmod(config_path, 0o600)
    print(f"Configuration saved to {config_path}")


def configure(args: argparse.Namespace) -> None:
    """Configure the CLI."""
    config = {}

    if args.api_url:
        config["api_url"] = args.api_url
    else:
        config["api_url"] = "https://openrouter.ai/api/v1"

    if args.api_key:
        config["api_key"] = args.api_key
    else:
        api_key = input("Enter your OpenRouter API key: ")
        if api_key.strip():
            config["api_key"] = api_key

    save_config(config)
