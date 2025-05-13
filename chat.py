import argparse
import json
import os
import sys
import requests
from datetime import datetime
from typing import Dict, Any, Optional
import questionary
from configure import load_config, save_config, configure
from list_models import list_models, get_models
from chat_interface import ChatInterface, NoTTYInterface
from rich.console import Console
from rich.style import Style
from rich.markdown import Markdown

def make_api_request(endpoint: str, data: Dict[str, Any], api_key: str, api_url: str) -> Dict[str, Any] | None:  
    # print(data)

    response = requests.post(f"{api_url}/{endpoint}", headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/Alpha1337k/openrouter-cli",
        "X-Title": "openrouter-cli"
    }, json=data)
    
    if response.status_code != 200:
        print(f"Error: API request failed with status code {response.status_code}")
        print(response.text)
        return None
    
    return response.json()

def handle_no_tty_out(args: argparse.Namespace, response: Dict[str, Any]):
    if (response['choices'][0]['message']['reasoning'] and args.no_thinking_stdout != True):
        print("<think>")
        print(response['choices'][0]['message']['reasoning'])
        print("</think>")
    print(response['choices'][0]['message']['content'])


def chat(args: argparse.Namespace, config: Dict[str, str]) -> None:
    """Interact with the OpenRouter API using a chat model."""

    models = get_models(config["api_url"], config['api_key'])

    if next((model for model in models if model['id'] == args.model), None) is None:
        print(f"Error: The specified model was not supported. Run 'openrouter models' for available models.")
        exit(1)

    interface = ChatInterface() if os.isatty(0) else NoTTYInterface()

    data = {
        "messages": [],
        "model": args.model,
        "provider": {
            "sort": "price"
        }
    }

    while True:
        user_input = interface.run()

        if user_input is None:
            exit(0)
        elif user_input == '':
            continue
        
        data["messages"].append({"role": "user", "content": user_input})

        response = make_api_request("chat/completions", data, 
                                    api_key=config["api_key"], 
                                    api_url=config['api_url'])

        if response is None:
            continue

        if os.isatty(sys.stdin.fileno()) == False:
            handle_no_tty_out(args, response)
            break

        console = Console()

        if (response['choices'][0]['message']['reasoning'] and args.no_thinking_stdout != True):
            md = Markdown(response['choices'][0]['message']['reasoning'])
            console.print(md, markup=True, style=Style(dim=True, italic=True))
            print('\n')

        # print(f"\n{response['choices'][0]['message']['content']}\n")

        md = Markdown(response['choices'][0]['message']['content'])
        console.print(md, markup=True)

        data['messages'].append(response['choices'][0]['message']['content'])

