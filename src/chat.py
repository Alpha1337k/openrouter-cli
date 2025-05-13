import argparse
import json
import os
import sys
import requests
from requests import Response
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import questionary
from configure import load_config, save_config, configure
from list_models import list_models, get_models
from chat_interface import ChatInterface, NoTTYInterface
from token_streamer import TokenStreamer
from rich.console import Console
from rich.style import Style
from rich.markdown import Markdown


def validate_model(api_url: str, api_key: str, model_id: str) -> None:
    models = get_models(api_url, api_key)

    if next((model for model in models if model["id"] == model_id), None) is None:
        print(
            f"Error: The specified model was not supported. Run 'openrouter models' for available models."
        )
        exit(1)


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


def handle_stream_data(
    args: argparse.Namespace,
    data: Any,
    requires_splitter: bool | None,
    content_streamer: TokenStreamer | None,
    reasoning_streamer: TokenStreamer | None,
) -> Tuple[str, str, bool | None]:
    content_buffer = ""
    reasoning_buffer = ""

    reasoning = data["choices"][0]["delta"].get("reasoning")
    content = data["choices"][0]["delta"].get("content")

    if reasoning:
        if reasoning_streamer and args.no_thinking_stdout != True:
            reasoning_streamer.add_tokens(reasoning)
        reasoning_buffer += reasoning

        requires_splitter = True

    if content:
        # Let's print all the remaining tokens in the reasoning buffer.
        if reasoning_streamer:
            reasoning_streamer.flush()

        if content_streamer:
            # Add a splitter if reasoning is done and the content is starting.
            if (
                requires_splitter == True
                and args.no_thinking_stdout != True
            ):
                content_streamer.add_tokens("\n---\n")
                requires_splitter = False

            content_streamer.add_tokens(content)
        content_buffer += content

    return (reasoning_buffer, content_buffer, requires_splitter)


def traverse_response_stream(args: argparse.Namespace, response: Response):
    buffer = ""

    content_buffer = ""
    reasoning_buffer = ""
    requires_splitter = None

    console = Console()

    functions = {
        "md_reasoning": lambda md: console.print(
            Markdown(md), markup=True, style=Style(dim=True, italic=True)
        ),
        "md_content": lambda md: console.print(Markdown(md), markup=True),
    }

    reasoning_streamer: TokenStreamer | None = None
    content_streamer: TokenStreamer | None = None

    if args.pretty == True:
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

                        (reasoning_chunk, content_chunk, requires_splitter) = (
                            handle_stream_data(
                                args,
                                data_obj,
                                requires_splitter,
                                content_streamer,
                                reasoning_streamer,
                            )
                        )

                        reasoning_buffer += reasoning_chunk
                        content_buffer += content_chunk

                    except json.JSONDecodeError:
                        pass
            except Exception:
                break

    if args.pretty == False:
        if len(reasoning_buffer) and args.no_thinking_stdout != True:
            print("<think>\n", reasoning_buffer, "</think>\n")
        print(content_buffer)

    return content_buffer, reasoning_buffer


def chat(args: argparse.Namespace, config: Dict[str, str]) -> None:
    """Interact with the OpenRouter API using a chat model."""

    validate_model(config["api_url"], config["api_key"], args.model)

    interface = ChatInterface() if os.isatty(0) else NoTTYInterface()

    data = {
        "messages": [],
        "model": args.model,
        "provider": {"sort": "price"},
        "stream": True,
        "temperature": args.temperature or None,
        "seed": args.seed or None,
        "effort": args.effort or None,
    }

    if args.system:
        data["messages"].append({"role": "system", "content": args.system})

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

        data["messages"].append(content)

        if (
            os.isatty(sys.stdout.fileno()) == False
            or os.isatty(sys.stdin.fileno()) == False
        ):
            break
