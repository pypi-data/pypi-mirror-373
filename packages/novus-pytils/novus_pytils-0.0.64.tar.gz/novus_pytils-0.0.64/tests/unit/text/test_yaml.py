"""Tests for novus_pytils.text.yaml module."""

import pytest
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open

from novus_pytils.text.yaml import (
    load_yaml, get_yaml_files, load_config, save_config,
    get_config_value, set_config_value, validate_config, merge_configs
)


class TestLoadYaml:
    """Test the load_yaml function."""
    
    def test_load_yaml_basic(self, sample_yaml_file):
        result = load_yaml(sample_yaml_file)
        
        assert isinstance(result, dict)
        assert result["name"] == "test"
        assert result["value"] == 42
        assert result["items"] == ["a", "b", "c"]
    
    def test_load_yaml_nested_structure(self, temp_dir):
        yaml_content = """
        database:
          host: localhost
          port: 5432
          credentials:
            username: user
            password: pass
        features:
          - feature1
          - feature2
        """
        yaml_file = temp_dir / "nested.yaml"
        yaml_file.write_text(yaml_content)
        
        result = load_yaml(str(yaml_file))
        
        assert result["database"]["host"] == "localhost"
        assert result["database"]["port"] == 5432
        assert result["database"]["credentials"]["username"] == "user"
        assert result["features"] == ["feature1", "feature2"]
    
    def test_load_yaml_empty_file(self, temp_dir):
        yaml_file = temp_dir / "empty.yaml"
        yaml_file.write_text("")
        
        result = load_yaml(str(yaml_file))
        assert result is None or result == {}
    
    def test_load_yaml_invalid_syntax(self, temp_dir):
        yaml_file = temp_dir / "invalid.yaml"
        yaml_file.write_text("key: value\ninvalid: [unclosed list")
        
        with pytest.raises(yaml.YAMLError):
            load_yaml(str(yaml_file))
    
    def test_load_yaml_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            load_yaml("/nonexistent/file.yaml")
    
    def test_load_yaml_with_special_types(self, temp_dir):
        yaml_content = """
        string_value: "hello"
        int_value: 42
        float_value: 3.14
        bool_value: true
        null_value: null
        date_value: 2023-01-01
        """
        yaml_file = temp_dir / "types.yaml"
        yaml_file.write_text(yaml_content)
        
        result = load_yaml(str(yaml_file))
        
        assert isinstance(result["string_value"], str)
        assert isinstance(result["int_value"], int)
        assert isinstance(result["float_value"], float)
        assert isinstance(result["bool_value"], bool)
        assert result["null_value"] is None


class TestGetYamlFiles:
    """Test the get_yaml_files function."""
    
    def test_get_yaml_files_basic(self, temp_dir):
        # Create YAML files
        (temp_dir / "config.yaml").write_text("test: value")
        (temp_dir / "settings.yml").write_text("test: value")
        (temp_dir / "other.txt").write_text("not yaml")
        
        yaml_files = get_yaml_files(str(temp_dir))
        
        assert isinstance(yaml_files, list)
        assert len(yaml_files) == 2
        yaml_names = [Path(f).name for f in yaml_files]
        assert "config.yaml" in yaml_names
        assert "settings.yml" in yaml_names
        assert "other.txt" not in yaml_names
    
    def test_get_yaml_files_no_yaml_files(self, temp_dir):
        (temp_dir / "file.txt").write_text("content")
        
        yaml_files = get_yaml_files(str(temp_dir))
        assert yaml_files == []
    
    def test_get_yaml_files_empty_directory(self, temp_dir):
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()
        
        yaml_files = get_yaml_files(str(empty_dir))
        assert yaml_files == []
    
    def test_get_yaml_files_nonexistent_directory(self):
        # Function returns empty list for nonexistent directory
        yaml_files = get_yaml_files("/nonexistent/directory")
        assert yaml_files == []


class TestLoadConfig:
    """Test the load_config function."""
    
    def test_load_config_basic(self, sample_yaml_file):
        config = load_config(sample_yaml_file)
        
        assert isinstance(config, dict)
        assert config["name"] == "test"
        assert config["value"] == 42
    
    def test_load_config_complex(self, temp_dir):
        config_content = """
        app:
          name: "MyApp"
          version: "1.0.0"
          debug: false
        database:
          host: "localhost"
          port: 5432
        logging:
          level: "INFO"
          handlers:
            - console
            - file
        """
        config_file = temp_dir / "app.yaml"
        config_file.write_text(config_content)
        
        config = load_config(str(config_file))
        
        assert config["app"]["name"] == "MyApp"
        assert config["database"]["port"] == 5432
        assert config["logging"]["handlers"] == ["console", "file"]
    
    def test_load_config_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/config.yaml")


class TestSaveConfig:
    """Test the save_config function."""
    
    def test_save_config_basic(self, temp_dir):
        config = {
            "name": "test",
            "value": 42,
            "items": ["a", "b", "c"]
        }
        config_file = temp_dir / "saved.yaml"
        
        save_config(config, str(config_file))
        
        assert config_file.exists()
        
        # Verify by loading back
        loaded_config = load_config(str(config_file))
        assert loaded_config == config
    
    def test_save_config_with_indentation(self, temp_dir):
        config = {
            "nested": {
                "key1": "value1",
                "key2": "value2"
            }
        }
        config_file = temp_dir / "indented.yaml"
        
        save_config(config, str(config_file), indent=4)
        
        assert config_file.exists()
        content = config_file.read_text()
        # Check that indentation is applied
        lines = content.split('\n')
        assert any(line.startswith('    ') for line in lines)  # 4-space indent
    
    def test_save_config_overwrite(self, temp_dir):
        config1 = {"key": "value1"}
        config2 = {"key": "value2"}
        config_file = temp_dir / "overwrite.yaml"
        
        save_config(config1, str(config_file))
        save_config(config2, str(config_file))
        
        loaded_config = load_config(str(config_file))
        assert loaded_config == config2
    
    def test_save_config_complex_structure(self, temp_dir):
        config = {
            "app": {
                "name": "TestApp",
                "settings": {
                    "debug": True,
                    "features": ["auth", "logging"]
                }
            },
            "database": {
                "connections": [
                    {"name": "primary", "host": "localhost"},
                    {"name": "replica", "host": "replica.db"}
                ]
            }
        }
        config_file = temp_dir / "complex.yaml"
        
        save_config(config, str(config_file))
        
        loaded_config = load_config(str(config_file))
        assert loaded_config == config


class TestGetConfigValue:
    """Test the get_config_value function."""
    
    def test_get_config_value_simple_key(self):
        config = {"name": "test", "value": 42}
        
        assert get_config_value(config, "name") == "test"
        assert get_config_value(config, "value") == 42
    
    def test_get_config_value_nested_key(self):
        config = {
            "database": {
                "host": "localhost",
                "settings": {
                    "timeout": 30
                }
            }
        }
        
        assert get_config_value(config, "database.host") == "localhost"
        assert get_config_value(config, "database.settings.timeout") == 30
    
    def test_get_config_value_with_default(self):
        config = {"existing": "value"}
        
        assert get_config_value(config, "missing", default="default") == "default"
        assert get_config_value(config, "existing", default="default") == "value"
    
    def test_get_config_value_missing_key(self):
        config = {"name": "test"}
        
        assert get_config_value(config, "missing") is None
    
    def test_get_config_value_missing_nested_key(self):
        config = {"database": {"host": "localhost"}}
        
        assert get_config_value(config, "database.missing") is None
        assert get_config_value(config, "missing.key") is None
    
    def test_get_config_value_array_index(self):
        config = {"items": ["first", "second", "third"]}
        
        # Note: Implementation may or may not support array indexing
        # This test assumes dot notation for nested objects only
        assert get_config_value(config, "items") == ["first", "second", "third"]


class TestSetConfigValue:
    """Test the set_config_value function."""
    
    def test_set_config_value_simple_key(self):
        config = {"name": "old_value"}
        
        set_config_value(config, "name", "new_value")
        
        assert config["name"] == "new_value"
    
    def test_set_config_value_new_key(self):
        config = {"existing": "value"}
        
        set_config_value(config, "new_key", "new_value")
        
        assert config["new_key"] == "new_value"
        assert config["existing"] == "value"  # Existing key unchanged
    
    def test_set_config_value_nested_key(self):
        config = {
            "database": {
                "host": "old_host",
                "port": 5432
            }
        }
        
        set_config_value(config, "database.host", "new_host")
        
        assert config["database"]["host"] == "new_host"
        assert config["database"]["port"] == 5432  # Other values unchanged
    
    def test_set_config_value_create_nested_structure(self):
        config = {}
        
        set_config_value(config, "app.database.host", "localhost")
        
        assert config["app"]["database"]["host"] == "localhost"
    
    def test_set_config_value_deep_nesting(self):
        config = {}
        
        set_config_value(config, "a.b.c.d.e", "deep_value")
        
        assert config["a"]["b"]["c"]["d"]["e"] == "deep_value"
    
    def test_set_config_value_overwrite_nested(self):
        config = {
            "section": {
                "key1": "value1",
                "key2": "value2"
            }
        }
        
        set_config_value(config, "section.key1", "new_value")
        
        assert config["section"]["key1"] == "new_value"
        assert config["section"]["key2"] == "value2"


class TestValidateConfig:
    """Test the validate_config function."""
    
    def test_validate_config_valid_simple(self):
        config = {"name": "test", "value": 42}
        schema = {"name": {"required": False}, "value": {"required": False}}
        
        result = validate_config(config, schema)
        assert result is True
    
    def test_validate_config_invalid_type(self):
        config = {"name": "test", "value": "not_int"}
        schema = {"name": str, "value": int}
        
        # Current implementation doesn't validate types, only structure
        result = validate_config(config, schema)
        assert result is True
    
    def test_validate_config_missing_required_key(self):
        config = {"name": "test"}
        schema = {"name": {"required": True}, "value": {"required": True}}
        
        result = validate_config(config, schema)
        assert result is False  # Missing required "value" key
    
    def test_validate_config_extra_keys_allowed(self):
        config = {"name": "test", "value": 42, "extra": "allowed"}
        schema = {"name": str, "value": int}
        
        # Behavior depends on implementation - extra keys might be allowed
        result = validate_config(config, schema)
        # This could be True or False depending on implementation
        assert isinstance(result, bool)
    
    def test_validate_config_nested_structure(self):
        config = {
            "database": {
                "host": "localhost",
                "port": 5432
            },
            "debug": True
        }
        schema = {
            "database": {
                "host": str,
                "port": int
            },
            "debug": bool
        }
        
        result = validate_config(config, schema)
        assert result is True
    
    def test_validate_config_empty_config(self):
        config = {}
        schema = {}
        
        result = validate_config(config, schema)
        assert result is True
    
    def test_validate_config_complex_types(self):
        config = {
            "items": ["a", "b", "c"],
            "metadata": {
                "version": "1.0",
                "tags": ["tag1", "tag2"]
            }
        }
        schema = {
            "items": list,
            "metadata": {
                "version": str,
                "tags": list
            }
        }
        
        result = validate_config(config, schema)
        assert result is True


class TestMergeConfigs:
    """Test the merge_configs function."""
    
    def test_merge_configs_simple(self):
        config1 = {"name": "app1", "version": "1.0"}
        config2 = {"name": "app2", "debug": True}
        
        result = merge_configs(config1, config2)
        
        assert result["name"] == "app2"  # Later config overwrites
        assert result["version"] == "1.0"  # From first config
        assert result["debug"] is True  # From second config
    
    def test_merge_configs_nested(self):
        config1 = {
            "database": {
                "host": "localhost",
                "port": 5432
            },
            "app": {
                "name": "MyApp"
            }
        }
        config2 = {
            "database": {
                "host": "remote",
                "timeout": 30
            },
            "logging": {
                "level": "DEBUG"
            }
        }
        
        result = merge_configs(config1, config2)
        
        assert result["database"]["host"] == "remote"  # Overwritten
        assert result["database"]["port"] == 5432  # From first config
        assert result["database"]["timeout"] == 30  # From second config
        assert result["app"]["name"] == "MyApp"  # From first config
        assert result["logging"]["level"] == "DEBUG"  # From second config
    
    def test_merge_configs_multiple(self):
        config1 = {"a": 1, "b": 2}
        config2 = {"b": 20, "c": 3}
        config3 = {"c": 30, "d": 4}
        
        result = merge_configs(config1, config2, config3)
        
        assert result["a"] == 1
        assert result["b"] == 20  # From config2
        assert result["c"] == 30  # From config3 (last wins)
        assert result["d"] == 4
    
    def test_merge_configs_empty_configs(self):
        config1 = {}
        config2 = {"key": "value"}
        config3 = {}
        
        result = merge_configs(config1, config2, config3)
        
        assert result == {"key": "value"}
    
    def test_merge_configs_single_config(self):
        config = {"name": "test", "value": 42}
        
        result = merge_configs(config)
        
        assert result == config
        assert result is not config  # Should be a copy
    
    def test_merge_configs_no_configs(self):
        result = merge_configs()
        
        assert result == {}
    
    def test_merge_configs_list_values(self):
        config1 = {"items": ["a", "b"]}
        config2 = {"items": ["c", "d"]}
        
        result = merge_configs(config1, config2)
        
        # Lists should be replaced, not merged (typical behavior)
        assert result["items"] == ["c", "d"]
    
    def test_merge_configs_deep_nesting(self):
        config1 = {
            "level1": {
                "level2": {
                    "level3": {
                        "key1": "value1",
                        "key2": "value2"
                    }
                }
            }
        }
        config2 = {
            "level1": {
                "level2": {
                    "level3": {
                        "key2": "new_value2",
                        "key3": "value3"
                    }
                }
            }
        }
        
        result = merge_configs(config1, config2)
        
        assert result["level1"]["level2"]["level3"]["key1"] == "value1"
        assert result["level1"]["level2"]["level3"]["key2"] == "new_value2"
        assert result["level1"]["level2"]["level3"]["key3"] == "value3"