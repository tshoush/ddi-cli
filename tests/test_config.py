import json
import os
import shutil
from unittest.mock import patch
import pytest
from ddi.config import load_config, get_config_value, save_config

@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary directory for config files."""
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(original_cwd)

def test_load_config_exists(temp_config_dir):
    """Test loading an existing config.json."""
    config_data = {"key": "value"}
    with open("config.json", "w") as f:
        json.dump(config_data, f)
    
    config = load_config()
    assert config == config_data

def test_load_config_from_example(temp_config_dir):
    """Test creating config.json from config.json.example."""
    example_data = {"key": "example_value"}
    with open("config.json.example", "w") as f:
        json.dump(example_data, f)

    config = load_config()
    assert config == example_data
    assert os.path.exists("config.json")

@patch('builtins.print')
def test_load_config_no_files(mock_print, temp_config_dir):
    """Test load_config when no config files are present."""
    with pytest.raises(SystemExit) as e:
        load_config()
    assert e.type == SystemExit
    assert e.value.code == 1

@patch('builtins.print')
def test_load_config_invalid_json(mock_print, temp_config_dir):
    """Test load_config with an invalid JSON file."""
    with open("config.json", "w") as f:
        f.write("{'key': 'invalid_json'}")
    
    with pytest.raises(SystemExit) as e:
        load_config()
    assert e.type == SystemExit
    assert e.value.code == 1

def test_get_config_value():
    """Test get_config_value with nested keys."""
    config = {"a": {"b": {"c": "value"}}}
    assert get_config_value(config, "a.b.c") == "value"
    assert get_config_value(config, "a.b.x") is None
    assert get_config_value(config, "a.x.c") is None
    assert get_config_value(config, "x.y.z") is None
    assert get_config_value(config, "a.b.c", default="default") == "value"
    assert get_config_value(config, "a.b.x", default="default") == "default"

def test_save_config(temp_config_dir):
    """Test saving a config file."""
    config_data = {"key": "new_value"}
    save_config(config_data)
    
    with open("config.json", "r") as f:
        saved_config = json.load(f)
    
    assert saved_config == config_data
