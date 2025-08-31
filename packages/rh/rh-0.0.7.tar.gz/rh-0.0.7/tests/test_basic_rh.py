"""
Basic tests for the core MeshBuilder functionality.

Following TDD principles, starting with simple tests and building incrementally.
"""

import pytest
from typing import Dict, Any


def test_mesh_builder_imports():
    """Test that we can import the main classes"""
    from rh import MeshBuilder

    assert MeshBuilder is not None


def test_basic_mesh_creation():
    """Test creating a basic mesh with simple temperature conversion"""
    from rh import MeshBuilder

    # Simple mesh with one conversion
    mesh_spec = {
        "temp_fahrenheit": ["temp_celsius"],
    }

    functions_spec = {
        "temp_fahrenheit": "return temp_celsius * 9/5 + 32;",
    }

    initial_values = {
        "temp_celsius": 0.0,
    }

    # Should be able to create a MeshBuilder instance
    builder = MeshBuilder(
        mesh_spec=mesh_spec,
        functions_spec=functions_spec,
        initial_values=initial_values,
    )

    assert builder is not None
    assert builder.mesh == mesh_spec


def test_generate_config():
    """Test that generate_config returns proper structure"""
    from rh import MeshBuilder

    mesh_spec = {
        "temp_fahrenheit": ["temp_celsius"],
    }

    functions_spec = {
        "temp_fahrenheit": "return temp_celsius * 9/5 + 32;",
    }

    initial_values = {
        "temp_celsius": 20.0,
    }

    builder = MeshBuilder(
        mesh_spec=mesh_spec,
        functions_spec=functions_spec,
        initial_values=initial_values,
    )

    config = builder.generate_config()

    # Test configuration structure
    assert "schema" in config
    assert "uiSchema" in config
    assert "functions" in config
    assert "propagation_rules" in config
    assert "initial_values" in config
    assert "mesh" in config

    # Test that initial values are preserved
    assert config["initial_values"]["temp_celsius"] == 20.0


def test_type_inference():
    """Test that types are inferred correctly from initial values"""
    from rh import MeshBuilder

    mesh_spec = {
        "result": ["input_float", "input_int", "input_bool", "input_str"],
    }

    functions_spec = {
        "result": "return input_float + input_int + (input_bool ? 1 : 0) + input_str.length;",
    }

    initial_values = {
        "input_float": 3.14,
        "input_int": 42,
        "input_bool": True,
        "input_str": "hello",
    }

    builder = MeshBuilder(
        mesh_spec=mesh_spec,
        functions_spec=functions_spec,
        initial_values=initial_values,
    )

    config = builder.generate_config()
    schema_props = config["schema"]["properties"]

    assert schema_props["input_float"]["type"] == "number"
    assert schema_props["input_int"]["type"] == "integer"
    assert schema_props["input_bool"]["type"] == "boolean"
    assert schema_props["input_str"]["type"] == "string"


def test_ui_conventions():
    """Test that UI conventions are applied based on variable names"""
    from rh import MeshBuilder

    mesh_spec = {
        "readonly_result": ["slider_opacity", "hidden_internal"],
    }

    functions_spec = {
        "readonly_result": "return slider_opacity + hidden_internal;",
    }

    initial_values = {
        "slider_opacity": 50,
        "hidden_internal": 10,
    }

    builder = MeshBuilder(
        mesh_spec=mesh_spec,
        functions_spec=functions_spec,
        initial_values=initial_values,
    )

    config = builder.generate_config()
    ui_schema = config["uiSchema"]

    # Test convention-based UI widgets
    assert ui_schema["slider_opacity"]["ui:widget"] == "range"
    assert ui_schema["readonly_result"]["ui:readonly"] is True
    assert ui_schema["hidden_internal"]["ui:widget"] == "hidden"


if __name__ == "__main__":
    pytest.main([__file__])
