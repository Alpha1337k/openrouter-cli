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
from chat_interface import ChatInterface

def make_api_request(endpoint: str, data: Dict[str, Any], api_key: str) -> Dict[str, Any]:    
    response = requests.post(f"{API_URL}/{endpoint}", headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }, json=data)
    
    if response.status_code != 200:
        print(f"Error: API request failed with status code {response.status_code}")
        print(response.text)
        return None
    
    return response.json()

def chat(args: argparse.Namespace, config: Dict[str, str]) -> None:
    """Interact with the OpenRouter API using a chat model."""

    interface = ChatInterface()

    while True:
        user_input = interface.run()

        if user_input is None:
            exit(1)
        elif user_input == '':
            continue
        
        print(user_input)

        response = make_api_request("chat/completions", data, config["api_key"])

