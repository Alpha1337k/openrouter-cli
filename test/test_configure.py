import pytest
import os
import json
from unittest.mock import patch
from configure import load_config, save_config, configure
from argparse import Namespace


@pytest.fixture
def temp_config_dir(tmp_path):
    old_home = os.environ.get("HOME")
    os.environ["HOME"] = str(tmp_path)
    yield tmp_path
    if old_home:
        os.environ["HOME"] = old_home


def test_load_config_nonexistent(temp_config_dir):
    with pytest.raises(SystemExit):
        load_config()


def test_load_config_invalid_json(temp_config_dir):
    config_path = os.path.expanduser("~/.openrouter-cli/.config")

    os.makedirs(os.path.expanduser("~/.openrouter-cli"), exist_ok=True)

    with open(config_path, "w") as f:
        f.write("invalid json")

    with pytest.raises(SystemExit):
        load_config()


def test_load_config_valid(temp_config_dir):
    config_path = os.path.expanduser("~/.openrouter-cli/.config")
    test_config = {"api_key": "test_key", "api_url": "test_url"}

    os.makedirs(os.path.expanduser("~/.openrouter-cli"), exist_ok=True)

    with open(config_path, "w") as f:
        json.dump(test_config, f)

    config = load_config()
    assert config == test_config


def test_save_config(temp_config_dir):
    test_config = {"api_key": "test_key", "api_url": "test_url"}
    save_config(test_config)

    config_path = os.path.expanduser("~/.openrouter-cli/.config")
    assert os.path.exists(config_path)
    assert oct(os.stat(config_path).st_mode)[-3:] == "600"

    with open(config_path) as f:
        saved_config = json.load(f)
    assert saved_config == test_config


def test_configure_with_args(temp_config_dir):
    args = Namespace(api_key="cli_key", api_url="cli_url")
    configure(args)

    config_path = os.path.expanduser("~/.openrouter-cli/.config")
    with open(config_path) as f:
        config = json.load(f)

    assert config["api_key"] == "cli_key"
    assert config["api_url"] == "cli_url"


@patch("builtins.input", return_value="user_input_key")
def test_configure_with_user_input(mock_input, temp_config_dir):
    args = Namespace(api_key=None, api_url=None)
    configure(args)

    config_path = os.path.expanduser("~/.openrouter-cli/.config")
    with open(config_path) as f:
        config = json.load(f)

    assert config["api_key"] == "user_input_key"
    assert config["api_url"] == "https://openrouter.ai/api/v1"
