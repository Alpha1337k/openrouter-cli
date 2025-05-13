import argparse
import json
import os
import sys
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from configure import load_config, save_config, configure
import pydoc
import humanize


def get_models(api_url: str, api_key: str):
    """Get all available models from the API."""

    response = requests.get(
        f"{api_url}/models", headers={"Authorization": f"Bearer {api_key}"}
    )

    if response.status_code != 200:
        print(
            f"Error: Failed to retrieve models with status code {response.status_code}"
        )
        print(response.text)
        sys.exit(1)

    return response.json()["data"]


def list_models(args: argparse.Namespace, config: Dict[str, str]) -> None:
    """List available models."""

    models = get_models(config["api_url"], config["api_key"])

    if args.raw:
        print(json.dumps(models, indent=2))
    else:
        formatted_list = []

        for model in models:
            base_string = f"- {model['id']:50}"

            context_string = ""

            if model["top_provider"]["context_length"] is not None:
                context_string += f"\t@ {humanize.naturalsize(model['top_provider']['context_length'], gnu=True)} context"
            else:
                context_string += f"\t@ - context"

            base_string += f"{context_string:20}"

            base_string += (
                f"({datetime.fromtimestamp(model['created']).strftime('%d-%m-%Y')})"
            )

            price_strings = (
                f"In: ${(float(model['pricing']['prompt']) * 1_000_000):.3f}/1M",
                f"Out: ${(float(model['pricing']['completion']) * 1_000_000):.3f}/1M",
            )

            base_string += f"\t[ {price_strings[0]:15} {price_strings[1]:15} ]"

            formatted_list.append(base_string)

        pydoc.pager("\n".join(formatted_list))
