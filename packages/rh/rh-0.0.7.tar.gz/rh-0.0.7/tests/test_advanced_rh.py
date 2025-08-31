"""
Advanced tests for MeshBuilder functionality.

Tests for more complex features like propagation rules, function resolution,
and advanced UI configuration.
"""

import pytest
from typing import Dict, Any


def test_reverse_mesh_generation():
    """Test that reverse mesh (propagation rules) are generated correctly"""
    from rh import MeshBuilder

    mesh_spec = {
        "temp_fahrenheit": ["temp_celsius"],
        "temp_kelvin": ["temp_celsius"],
        "kinetic_energy": ["mass", "velocity"],
        "momentum": ["mass", "velocity"],
        "total": ["kinetic_energy", "momentum"],
    }

    functions_spec = {
        "temp_fahrenheit": "return temp_celsius * 9/5 + 32;",
        "temp_kelvin": "return temp_celsius + 273.15;",
        "kinetic_energy": "return 0.5 * mass * velocity * velocity;",
        "momentum": "return mass * velocity;",
        "total": "return kinetic_energy + momentum;",
    }

    builder = MeshBuilder(mesh_spec=mesh_spec, functions_spec=functions_spec)
    config = builder.generate_config()

    reverse_mesh = config["propagation_rules"]["reverseMesh"]

    # temp_celsius should trigger both fahrenheit and kelvin conversions
    assert "temp_celsius" in reverse_mesh
    assert set(reverse_mesh["temp_celsius"]) == {"temp_fahrenheit", "temp_kelvin"}

    # mass and velocity should trigger kinetic_energy and momentum
    assert "mass" in reverse_mesh
    assert set(reverse_mesh["mass"]) == {"kinetic_energy", "momentum"}
    assert "velocity" in reverse_mesh
    assert set(reverse_mesh["velocity"]) == {"kinetic_energy", "momentum"}

    # kinetic_energy and momentum should trigger total
    assert "kinetic_energy" in reverse_mesh
    assert reverse_mesh["kinetic_energy"] == ["total"]
    assert "momentum" in reverse_mesh
    assert reverse_mesh["momentum"] == ["total"]


def test_function_resolution_inline():
    """Test that inline JavaScript functions are properly resolved"""
    from rh import MeshBuilder

    mesh_spec = {"output": ["input"]}

    functions_spec = {"output": "return input * 2;"}

    builder = MeshBuilder(mesh_spec=mesh_spec, functions_spec=functions_spec)
    config = builder.generate_config()

    functions_js = config["functions"]

    # Should contain a properly formatted JS function
    assert "const meshFunctions" in functions_js
    assert "output" in functions_js
    assert "function(input)" in functions_js
    assert "return input * 2;" in functions_js


def test_field_overrides():
    """Test that field overrides are properly applied"""
    from rh import MeshBuilder

    mesh_spec = {"result": ["input_value"]}

    functions_spec = {"result": "return input_value * 2;"}

    initial_values = {"input_value": 10}

    field_overrides = {
        "input_value": {
            "title": "Custom Input Title",
            "minimum": 0,
            "maximum": 100,
            "ui:help": "This is a custom help text",
            "ui:widget": "range",
        }
    }

    builder = MeshBuilder(
        mesh_spec=mesh_spec,
        functions_spec=functions_spec,
        initial_values=initial_values,
        field_overrides=field_overrides,
    )

    config = builder.generate_config()

    # Check schema overrides
    schema_props = config["schema"]["properties"]
    assert schema_props["input_value"]["title"] == "Custom Input Title"
    assert schema_props["input_value"]["minimum"] == 0
    assert schema_props["input_value"]["maximum"] == 100

    # Check UI schema overrides
    ui_schema = config["uiSchema"]
    assert ui_schema["input_value"]["ui:help"] == "This is a custom help text"
    assert ui_schema["input_value"]["ui:widget"] == "range"


def test_complex_mesh_with_cycles():
    """Test a mesh that has cycles and complex dependencies"""
    from rh import MeshBuilder

    # This mesh has bidirectional temperature conversion
    mesh_spec = {
        "temp_fahrenheit": ["temp_celsius"],
        "temp_celsius": ["temp_fahrenheit"],  # Bidirectional
        "temp_kelvin": ["temp_celsius"],
        "display_temp": ["temp_fahrenheit", "temp_kelvin"],  # Depends on multiple
    }

    functions_spec = {
        "temp_fahrenheit": "return temp_celsius * 9/5 + 32;",
        "temp_celsius": "return (temp_fahrenheit - 32) * 5/9;",
        "temp_kelvin": "return temp_celsius + 273.15;",
        "display_temp": "return `${temp_fahrenheit}°F / ${temp_kelvin}K`;",
    }

    builder = MeshBuilder(mesh_spec=mesh_spec, functions_spec=functions_spec)
    config = builder.generate_config()

    # Should handle the cycle gracefully
    reverse_mesh = config["propagation_rules"]["reverseMesh"]

    # Both celsius and fahrenheit should trigger each other
    assert "temp_celsius" in reverse_mesh
    assert "temp_fahrenheit" in reverse_mesh
    assert "temp_fahrenheit" in reverse_mesh["temp_celsius"]
    assert "temp_celsius" in reverse_mesh["temp_fahrenheit"]

    # Kelvin and display should be triggered by celsius
    assert "temp_kelvin" in reverse_mesh["temp_celsius"]
    assert "display_temp" in reverse_mesh["temp_fahrenheit"]
    assert "display_temp" in reverse_mesh["temp_kelvin"]


def test_multiple_prefix_conventions():
    """Test multiple UI conventions on different variables"""
    from rh import MeshBuilder

    mesh_spec = {
        "readonly_total": ["slider_value", "hidden_factor"],
        "color_output": ["slider_value"],
        "date_created": [],
    }

    functions_spec = {
        "readonly_total": "return slider_value * hidden_factor;",
        "color_output": "return `rgb(${slider_value}, 100, 150)`;",
    }

    initial_values = {
        "slider_value": 50,
        "hidden_factor": 2,
        "date_created": "2023-01-01",
    }

    builder = MeshBuilder(
        mesh_spec=mesh_spec,
        functions_spec=functions_spec,
        initial_values=initial_values,
    )

    config = builder.generate_config()
    ui_schema = config["uiSchema"]

    # Test all conventions
    assert ui_schema["slider_value"]["ui:widget"] == "range"
    assert ui_schema["readonly_total"]["ui:readonly"] is True
    assert ui_schema["hidden_factor"]["ui:widget"] == "hidden"
    assert ui_schema["color_output"]["ui:widget"] == "color"
    assert ui_schema["date_created"]["ui:widget"] == "date"


def test_computed_variables_are_readonly():
    """Test that computed variables (those with dependencies) are readonly by default"""
    from rh import MeshBuilder

    mesh_spec = {
        "computed_result": ["input_a", "input_b"],
        "another_computed": ["computed_result", "input_c"],
    }

    functions_spec = {
        "computed_result": "return input_a + input_b;",
        "another_computed": "return computed_result * input_c;",
    }

    initial_values = {"input_a": 10, "input_b": 20, "input_c": 2}

    builder = MeshBuilder(
        mesh_spec=mesh_spec,
        functions_spec=functions_spec,
        initial_values=initial_values,
    )

    config = builder.generate_config()
    ui_schema = config["uiSchema"]

    # Computed variables should be readonly
    assert ui_schema["computed_result"]["ui:readonly"] is True
    assert ui_schema["another_computed"]["ui:readonly"] is True

    # Input variables should not be readonly (no entry in ui_schema for readonly)
    assert "input_a" not in ui_schema or "ui:readonly" not in ui_schema.get(
        "input_a", {}
    )
    assert "input_b" not in ui_schema or "ui:readonly" not in ui_schema.get(
        "input_b", {}
    )
    assert "input_c" not in ui_schema or "ui:readonly" not in ui_schema.get(
        "input_c", {}
    )


def test_empty_mesh():
    """Test handling of empty mesh"""
    from rh import MeshBuilder

    mesh_spec = {}
    functions_spec = {}

    builder = MeshBuilder(mesh_spec=mesh_spec, functions_spec=functions_spec)
    config = builder.generate_config()

    assert config["schema"]["properties"] == {}
    assert config["uiSchema"] == {}
    assert config["propagation_rules"]["reverseMesh"] == {}
    assert config["mesh"] == {}


if __name__ == "__main__":
    pytest.main([__file__])
