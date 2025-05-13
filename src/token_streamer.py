import argparse
import json
import os
import sys
import requests
from requests import Response
from datetime import datetime
from typing import Dict, Any, Optional
import questionary
from configure import load_config, save_config, configure
from list_models import list_models, get_models
from chat_interface import ChatInterface, NoTTYInterface
from rich.console import Console
from rich.style import Style
from rich.markdown import Markdown
import re


class TokenStreamer:
    def __init__(self, renderer):
        """
        Initialize a markdown streamer that handles token streams reliably.
        """
        self.console = Console()
        self.buffer = ""
        self.renderer = renderer
        self.render_calls = 0

    def add_tokens(self, tokens):
        """
        Add tokens to the stream buffer and attempt to render complete blocks.

        Args:
            tokens (str): New tokens to add to the stream
        """
        # Add new tokens to our buffer
        self.buffer += tokens

        # Try to render any complete blocks
        self._try_render()

    def _try_render(self):
        """
        Attempt to identify and render complete markdown blocks from the buffer.
        Uses a conservative approach: only renders what we're confident is complete.
        """

        # Look for safe points to split the buffer
        split_point = self._find_safe_split_point()

        if split_point > 0:
            # We found a safe split point
            content_to_render = self.buffer[:split_point]
            self.buffer = self.buffer[split_point:]

            if self.render_calls != 0:
                print("\n")
            # Render the content
            self.renderer(content_to_render)

            self.render_calls += 1

    def _find_safe_split_point(self):
        """
        Find a position in the buffer where it's safe to split and render.
        Returns the index after which to split, or 0 if no safe point found.
        """
        # If buffer is empty, nothing to split
        if not self.buffer:
            return 0

        # First, check if there are any code blocks in the buffer
        code_blocks = list(re.finditer(r"```[^\n]*\n|~~~[^\n]*\n", self.buffer))

        # If we have code block markers, we need to be careful
        if code_blocks:
            # Count opening and closing fences to find complete code blocks
            fence_pairs = self._find_complete_fence_pairs()

            if not fence_pairs:
                # We have unclosed fences - not safe to split
                return 0

            # The last complete code block ends at the second position of the last pair
            last_complete_block_end = fence_pairs[-1][1]

            # Look for a paragraph break after the last complete code block
            after_code = self.buffer[last_complete_block_end:]
            paragraph_break = after_code.find("\n\n")

            if paragraph_break >= 0:
                # Safe to split after this paragraph break
                return last_complete_block_end + paragraph_break + 2
            else:
                # No paragraph break after code block,
                # but safe to split right after the complete code block
                return last_complete_block_end

        # No code blocks, look for paragraph breaks
        # Pattern: Double newline not inside a code block
        breaks = list(re.finditer(r"\n\n", self.buffer))

        if breaks:
            # Get the position after the last paragraph break
            return breaks[-1].end()

        # No safe split points found
        return 0

    def _find_complete_fence_pairs(self):
        """
        Find pairs of opening and closing code block fences in the buffer.
        Returns a list of (start, end) tuples for complete code blocks.
        """
        # Find all fence markers (opening and closing)
        fence_markers = list(re.finditer(r"```|~~~", self.buffer))

        if len(fence_markers) % 2 != 0:
            # Odd number of fence markers means we have an unclosed fence
            return []

        pairs = []
        stack = []

        for marker in fence_markers:
            marker_text = marker.group(0)
            pos = marker.end()

            if not stack:
                # This is an opening fence
                stack.append((marker_text, pos))
            else:
                # This could be a closing fence if it matches the opening type
                opening_text, opening_pos = stack[-1]

                if marker_text == opening_text:
                    # Matching pair found
                    stack.pop()
                    pairs.append((opening_pos, pos))
                else:
                    # Not a matching pair, treat as a new opening fence
                    stack.append((marker_text, pos))

        # If we have anything left on the stack, we have unclosed fences
        if stack:
            return []

        return pairs

    def flush(self):
        """
        Render any remaining content in the buffer.
        Call this at the end of the stream.
        """
        if self.buffer.strip():
            if self.render_calls != 0:
                print("")

            self.renderer(self.buffer.strip())
            self.buffer = ""
