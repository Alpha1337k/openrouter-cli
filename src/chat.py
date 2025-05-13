import argparse
import json
import os
import sys
import requests
from requests import Response
from datetime import datetime
from typing import Dict, Any, Optional
import questionary
from src.configure import load_config, save_config, configure
from src.list_models import list_models, get_models
from src.chat_interface import ChatInterface, NoTTYInterface
from src.chat_streamer import TokenStreamer
from rich.console import Console
from rich.style import Style
from rich.markdown import Markdown


def get_chat_completions(
    endpoint: str, data: Dict[str, Any], api_key: str, api_url: str
) -> Response | None:
    # print(data)

    response = requests.post(
        f"{api_url}/{endpoint}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/Alpha1337k/openrouter-cli",
            "X-Title": "openrouter-cli",
        },
        stream=True,
        json=data,
    )

    if response.status_code != 200:
        print(f"Error: API request failed with status code {response.status_code}")
        print(response.text)
        return None

    return response


def traverse_response_stream(args: argparse.Namespace, response: Response):
    buffer = ""

    content_buffer = ""
    reasoning_buffer = ""
    is_first_context = True

    console = Console()

    functions = {
        "md_reasoning": lambda md: console.print(
            Markdown(md), markup=True, style=Style(dim=True, italic=True)
        ),
        "md_content": lambda md: console.print(Markdown(md), markup=True),
    }

    reasoning_streamer: TokenStreamer | None = None
    content_streamer: TokenStreamer | None = None

    if os.isatty(sys.stdin.fileno()):
        reasoning_streamer = TokenStreamer(functions["md_reasoning"])
        content_streamer = TokenStreamer(functions["md_content"])

    for chunk in response.iter_content(chunk_size=1024, decode_unicode=False):
        buffer += chunk.decode("utf-8", errors="replace")
        while True:
            try:
                # Find the next complete SSE line
                line_end = buffer.find("\n")
                if line_end == -1:
                    break
                line = buffer[:line_end].strip()
                buffer = buffer[line_end + 1 :]
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        if content_streamer:
                            content_streamer.flush()
                        break
                    try:
                        data_obj = json.loads(data)

                        # print(data_obj["choices"][0]["delta"])

                        if data_obj["choices"][0]["delta"].get("reasoning"):
                            if reasoning_streamer:
                                reasoning_streamer.add_tokens(
                                    data_obj["choices"][0]["delta"].get("reasoning")
                                )
                            reasoning_buffer += data_obj["choices"][0]["delta"].get(
                                "reasoning"
                            )

                        if data_obj["choices"][0]["delta"].get("content"):
                            # Let's print all the remaining tokens in the reasoning buffer.
                            if reasoning_streamer:
                                reasoning_streamer.flush()

                            if content_streamer:
                                if is_first_context and len(reasoning_buffer):
                                    content_streamer.add_tokens("\n---\n")
                                    is_first_context = False
                                content_streamer.add_tokens(
                                    data_obj["choices"][0]["delta"].get("content")
                                )
                            content_buffer += data_obj["choices"][0]["delta"].get(
                                "content"
                            )

                    except json.JSONDecodeError:
                        pass
            except Exception:
                break

    if os.isatty(sys.stdin.fileno()) == False:
        if len(reasoning_buffer):
            print("<think>\n", reasoning_buffer, "</think>\n")
        print(content_buffer)

    return content_buffer, reasoning_buffer


def chat(args: argparse.Namespace, config: Dict[str, str]) -> None:
    """Interact with the OpenRouter API using a chat model."""

    models = get_models(config["api_url"], config["api_key"])

    if next((model for model in models if model["id"] == args.model), None) is None:
        print(
            f"Error: The specified model was not supported. Run 'openrouter models' for available models."
        )
        exit(1)

    interface = ChatInterface() if os.isatty(0) else NoTTYInterface()

    data = {
        "messages": [],
        "model": args.model,
        "provider": {"sort": "price"},
        "stream": True,
    }

    while True:
        user_input = interface.run()

        if user_input is None:
            exit(0)
        elif user_input == "":
            continue

        data["messages"].append({"role": "user", "content": user_input})

        response = get_chat_completions(
            "chat/completions",
            data,
            api_key=config["api_key"],
            api_url=config["api_url"],
        )

        if response is None:
            continue

        content, reasoning = traverse_response_stream(args, response)

        with open("out2", "+w") as file:
            file.write(reasoning)
            file.write(content)

        data["messages"].append(content)

        if (os.isatty(sys.stdin.fileno())) == False:
            break
