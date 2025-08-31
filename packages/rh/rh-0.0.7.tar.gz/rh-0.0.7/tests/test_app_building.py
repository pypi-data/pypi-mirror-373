"""
Tests for application building and HTML generation functionality.
"""

import pytest
import tempfile
from pathlib import Path
from typing import Dict, Any


def test_build_components_from_config():
    """Test that components can be built from explicit config"""
    from rh import MeshBuilder

    mesh_spec = {"temp_fahrenheit": ["temp_celsius"], "temp_kelvin": ["temp_celsius"]}

    functions_spec = {
        "temp_fahrenheit": "return temp_celsius * 9/5 + 32;",
        "temp_kelvin": "return temp_celsius + 273.15;",
    }

    initial_values = {"temp_celsius": 20.0}

    builder = MeshBuilder(
        mesh_spec=mesh_spec,
        functions_spec=functions_spec,
        initial_values=initial_values,
    )

    config = builder.generate_config()
    components = builder.build_components_from_config(config)

    # Test component structure
    assert "rjsf_schema" in components
    assert "rjsf_ui_schema" in components
    assert "js_functions_bundle" in components
    assert "propagation_config" in components

    # Components should match config
    assert components["rjsf_schema"] == config["schema"]
    assert components["rjsf_ui_schema"] == config["uiSchema"]
    assert components["js_functions_bundle"] == config["functions"]
    assert components["propagation_config"] == config["propagation_rules"]


def test_build_app_creates_html_file():
    """Test that build_app creates an HTML file"""
    from rh import MeshBuilder

    mesh_spec = {"result": ["input_value"]}

    functions_spec = {"result": "return input_value * 2;"}

    initial_values = {"input_value": 10}

    with tempfile.TemporaryDirectory() as tmpdir:
        builder = MeshBuilder(
            mesh_spec=mesh_spec,
            functions_spec=functions_spec,
            initial_values=initial_values,
            output_dir=tmpdir,
        )

        app_path = builder.build_app(title="Test App")

        # Should create an HTML file
        assert app_path.exists()
        assert app_path.suffix == ".html"
        assert app_path.name == "index.html"

        # File should contain expected content
        html_content = app_path.read_text()
        assert "Test App" in html_content
        assert "meshFunctions" in html_content


def test_html_content_structure():
    """Test that generated HTML has the expected structure"""
    from rh import MeshBuilder

    mesh_spec = {"fahrenheit": ["celsius"], "kelvin": ["celsius"]}

    functions_spec = {
        "fahrenheit": "return celsius * 9/5 + 32;",
        "kelvin": "return celsius + 273.15;",
    }

    initial_values = {"celsius": 0}

    with tempfile.TemporaryDirectory() as tmpdir:
        builder = MeshBuilder(
            mesh_spec=mesh_spec,
            functions_spec=functions_spec,
            initial_values=initial_values,
            output_dir=tmpdir,
        )

        app_path = builder.build_app(title="Temperature Converter")
        html_content = app_path.read_text()

        # Check for essential HTML structure
        assert "<!DOCTYPE html>" in html_content
        assert "<html" in html_content
        assert "<head>" in html_content
        assert "<body>" in html_content
        assert "Temperature Converter" in html_content

        # Check for React and RJSF dependencies
        assert "react" in html_content.lower()
        assert "rjsf" in html_content.lower()

        # Check for our generated JavaScript
        assert "meshFunctions" in html_content
        assert "fahrenheit" in html_content
        assert "kelvin" in html_content
        assert "celsius * 9/5 + 32" in html_content


def test_custom_output_directory():
    """Test that build_app respects custom output directory"""
    from rh import MeshBuilder

    mesh_spec = {"output": ["input"]}
    functions_spec = {"output": "return input;"}

    with tempfile.TemporaryDirectory() as tmpdir:
        custom_dir = Path(tmpdir) / "custom" / "nested" / "path"

        builder = MeshBuilder(
            mesh_spec=mesh_spec,
            functions_spec=functions_spec,
            output_dir=str(custom_dir),
        )

        app_path = builder.build_app()

        # Should create the directory structure
        assert custom_dir.exists()
        assert app_path.parent == custom_dir
        assert app_path.exists()


def test_mesh_builder_dataclass_defaults():
    """Test that MeshBuilder dataclass has proper defaults"""
    from rh import MeshBuilder

    mesh_spec = {"output": ["input"]}
    functions_spec = {"output": "return input;"}

    # Should work with minimal arguments
    builder = MeshBuilder(mesh_spec=mesh_spec, functions_spec=functions_spec)

    # Check defaults
    assert builder.initial_values == {}
    assert builder.field_overrides == {}
    assert builder.ui_config == {}
    assert builder.output_dir == "./mesh_app"


if __name__ == "__main__":
    pytest.main([__file__])
