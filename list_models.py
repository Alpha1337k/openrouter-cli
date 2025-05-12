import argparse
import json
import os
import sys
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from configure import load_config, save_config, configure

def list_models(args: argparse.Namespace, config: Dict[str, str]) -> None:
    """List available models."""
    response = requests.get(f"{config['api_url']}/models", headers={"Authorization": f"Bearer {config['api_key']}"})
    
    if response.status_code != 200:
        print(f"Error: Failed to retrieve models with status code {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    models = response.json()["data"]
    
    if args.raw:
        print(json.dumps(models, indent=2))
    else:
        print("Available models:")
        for model in models:
            print(f"- {model['id']} {datetime.fromtimestamp(model['created']).strftime('%d-%m-%Y')}")