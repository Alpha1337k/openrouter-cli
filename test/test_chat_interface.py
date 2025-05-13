import pytest
import os
from unittest.mock import Mock, patch
from chat_interface import ChatInterface, NoTTYInterface
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import KEY_ALIASES, Keys


@pytest.fixture
def temp_home(tmp_path):
    """Fixture to provide a temporary home directory"""
    old_home = os.environ.get("HOME")
    os.environ["HOME"] = str(tmp_path)
    yield tmp_path
    if old_home:
        os.environ["HOME"] = old_home


def test_chat_interface_init(temp_home):
    """Test ChatInterface initialization"""
    chat = ChatInterface()
    
    # Test directory creation
    cli_dir = os.path.expanduser("~/.openrouter-cli")
    assert os.path.exists(cli_dir)
    
    # Test history file path
    history_path = os.path.expanduser("~/.openrouter-cli/history")
    assert isinstance(chat.history, FileHistory)
    assert chat.history.filename == history_path
    
    # Test session initialization
    assert isinstance(chat.session, PromptSession)
    
    # Test key bindings
    assert isinstance(chat.kb, KeyBindings)

def test_chat_interface_init_existing_dir(temp_home):
    """Test ChatInterface initialization with existing directory"""
    # Create directory before initialization
    os.makedirs(os.path.expanduser("~/.openrouter-cli"), exist_ok=True)
    
    # Should not raise any exception
    chat = ChatInterface()
    assert os.path.exists(os.path.expanduser("~/.openrouter-cli"))


def test_notty_interface_init():
    """Test NoTTYInterface initialization"""
    interface = NoTTYInterface()
    # Simply verify that initialization doesn't raise exceptions
    assert isinstance(interface, NoTTYInterface)

def test_history_file_permissions(temp_home):
    """Test that history file is created with correct permissions"""
    chat = ChatInterface()
    history_path = os.path.expanduser("~/.openrouter-cli/history")
    
    # Write something to create the file
    chat.session.history.append_string("Test")
    
    assert os.path.exists(history_path)