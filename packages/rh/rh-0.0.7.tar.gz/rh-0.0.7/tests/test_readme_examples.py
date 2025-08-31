"""
Test that the examples in the README work correctly.
"""

import pytest
import tempfile
from pathlib import Path


def test_readme_quick_start_example():
    """Test the quick start example from the README."""
    from rh import MeshBuilder

    # Define relationships between variables
    mesh_spec = {
        "temp_fahrenheit": ["temp_celsius"],
        "temp_kelvin": ["temp_celsius"],
    }

    # Define how to compute each relationship
    functions_spec = {
        "temp_fahrenheit": "return temp_celsius * 9/5 + 32;",
        "temp_kelvin": "return temp_celsius + 273.15;",
    }

    # Set initial values
    initial_values = {"temp_celsius": 20.0}

    # Create and build the app
    with tempfile.TemporaryDirectory() as tmpdir:
        builder = MeshBuilder(mesh_spec, functions_spec, initial_values)
        builder.output_dir = tmpdir
        app_path = builder.build_app(title="Temperature Converter")

        # Verify the app was created
        assert app_path.exists()
        assert app_path.suffix == ".html"

        # Verify content
        html_content = app_path.read_text()
        assert "Temperature Converter" in html_content
        assert "temp_celsius * 9/5 + 32" in html_content
        assert "temp_celsius + 273.15" in html_content


def test_readme_ui_conventions_example():
    """Test the UI conventions example from the README."""
    from rh import MeshBuilder

    mesh_spec = {"result": ["slider_opacity", "readonly_result", "hidden_internal"]}

    functions_spec = {
        "result": "return slider_opacity + readonly_result + hidden_internal;"
    }

    initial_values = {
        "slider_opacity": 50,  # → Range slider (0-100)
        "readonly_result": 0,  # → Read-only display
        "hidden_internal": 10,  # → Hidden field
    }

    builder = MeshBuilder(mesh_spec, functions_spec, initial_values)
    config = builder.generate_config()

    ui_schema = config["uiSchema"]

    # Verify conventions are applied
    assert ui_schema["slider_opacity"]["ui:widget"] == "range"
    assert ui_schema["readonly_result"]["ui:readonly"] is True
    assert ui_schema["hidden_internal"]["ui:widget"] == "hidden"


def test_readme_advanced_example():
    """Test the advanced physics example from the README."""
    from rh import MeshBuilder

    # Physics calculator with custom field overrides
    mesh_spec = {
        "kinetic_energy": ["mass", "velocity"],
        "momentum": ["mass", "velocity"],
        "total_energy": ["kinetic_energy", "potential_energy"],
    }

    functions_spec = {
        "kinetic_energy": "return 0.5 * mass * velocity * velocity;",
        "momentum": "return mass * velocity;",
        "total_energy": "return kinetic_energy + potential_energy;",
    }

    field_overrides = {
        "mass": {
            "title": "Mass (kg)",
            "minimum": 0.1,
            "maximum": 1000,
            "ui:help": "Object mass in kilograms",
        }
    }

    builder = MeshBuilder(
        mesh_spec,
        functions_spec,
        initial_values={"mass": 10, "velocity": 5, "potential_energy": 100},
        field_overrides=field_overrides,
    )

    config = builder.generate_config()

    # Test field overrides were applied
    schema = config["schema"]
    assert schema["properties"]["mass"]["title"] == "Mass (kg)"
    assert schema["properties"]["mass"]["minimum"] == 0.1
    assert schema["properties"]["mass"]["maximum"] == 1000

    ui_schema = config["uiSchema"]
    assert ui_schema["mass"]["ui:help"] == "Object mass in kilograms"

    # Test propagation rules
    reverse_mesh = config["propagation_rules"]["reverseMesh"]
    assert "mass" in reverse_mesh
    assert set(reverse_mesh["mass"]) == {"kinetic_energy", "momentum"}
    assert "velocity" in reverse_mesh
    assert set(reverse_mesh["velocity"]) == {"kinetic_energy", "momentum"}
    assert "kinetic_energy" in reverse_mesh
    assert reverse_mesh["kinetic_energy"] == ["total_energy"]


if __name__ == "__main__":
    pytest.main([__file__])
