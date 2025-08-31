"""
Integration tests that verify the generated HTML has proper structure and JavaScript.
"""

import pytest
import tempfile
from pathlib import Path
import json
import re


def test_generated_html_has_proper_structure():
    """Test that the generated HTML contains all necessary components."""
    from rh import MeshBuilder

    mesh_spec = {"fahrenheit": ["celsius"], "kelvin": ["celsius"]}

    functions_spec = {
        "fahrenheit": "return celsius * 9/5 + 32;",
        "kelvin": "return celsius + 273.15;",
    }

    initial_values = {"celsius": 25.0}

    with tempfile.TemporaryDirectory() as tmpdir:
        builder = MeshBuilder(
            mesh_spec=mesh_spec,
            functions_spec=functions_spec,
            initial_values=initial_values,
            output_dir=tmpdir,
        )

        app_path = builder.build_app(title="Integration Test App")
        html_content = app_path.read_text()

        # Test HTML structure
        assert "<!DOCTYPE html>" in html_content
        assert "<html lang=\"en\">" in html_content
        assert "<title>Integration Test App</title>" in html_content

        # Test React and RJSF dependencies
        assert "react" in html_content
        assert "@rjsf/core" in html_content
        assert "@rjsf/validator-ajv8" in html_content

        # Test that our mesh functions are included
        assert "meshFunctions" in html_content
        assert "fahrenheit" in html_content
        assert "celsius * 9/5 + 32" in html_content
        assert "celsius + 273.15" in html_content

        # Test mesh propagator is included
        assert "MeshPropagator" in html_content
        assert "propagate" in html_content

        # Test RJSF form initialization
        assert "renderForm" in html_content
        assert "React.createElement" in html_content


def test_generated_javascript_is_valid():
    """Test that the generated JavaScript contains valid mesh configuration."""
    from rh import MeshBuilder

    mesh_spec = {"output1": ["input1", "input2"], "output2": ["input1"]}

    functions_spec = {
        "output1": "return input1 + input2;",
        "output2": "return input1 * 2;",
    }

    initial_values = {"input1": 10, "input2": 5}

    with tempfile.TemporaryDirectory() as tmpdir:
        builder = MeshBuilder(
            mesh_spec=mesh_spec,
            functions_spec=functions_spec,
            initial_values=initial_values,
            output_dir=tmpdir,
        )

        app_path = builder.build_app()
        html_content = app_path.read_text()

        # Extract the mesh config from JavaScript
        config_match = re.search(
            r'const meshConfig = ({.*?});', html_content, re.DOTALL
        )
        assert config_match, "meshConfig not found in generated HTML"

        config_str = config_match.group(1)
        config = json.loads(config_str)

        # Verify mesh structure
        assert "mesh" in config
        assert "reverseMesh" in config

        # Verify the mesh mapping
        assert config["mesh"]["output1"] == ["input1", "input2"]
        assert config["mesh"]["output2"] == ["input1"]

        # Verify reverse mesh
        assert "input1" in config["reverseMesh"]
        assert set(config["reverseMesh"]["input1"]) == {"output1", "output2"}
        assert config["reverseMesh"]["input2"] == ["output1"]


def test_multiple_ui_conventions_in_html():
    """Test that UI conventions are properly encoded in the HTML."""
    from rh import MeshBuilder

    mesh_spec = {"readonly_result": ["slider_value", "hidden_factor"]}

    functions_spec = {"readonly_result": "return slider_value * hidden_factor;"}

    initial_values = {"slider_value": 50, "hidden_factor": 2}

    with tempfile.TemporaryDirectory() as tmpdir:
        builder = MeshBuilder(
            mesh_spec=mesh_spec,
            functions_spec=functions_spec,
            initial_values=initial_values,
            output_dir=tmpdir,
        )

        app_path = builder.build_app()
        html_content = app_path.read_text()

        # The UI schema should be embedded in the form configuration
        # Look for the formConfig that contains the UI schema
        config_match = re.search(
            r'const formConfig = ({.*?});', html_content, re.DOTALL
        )
        assert config_match, "formConfig not found in generated HTML"

        config_str = config_match.group(1)
        form_config = json.loads(config_str)

        # Verify UI schema conventions
        ui_schema = form_config["uiSchema"]

        # slider_ prefix should create range widget
        assert ui_schema["slider_value"]["ui:widget"] == "range"

        # readonly_ prefix should set readonly
        assert ui_schema["readonly_result"]["ui:readonly"] is True

        # hidden_ prefix should create hidden widget
        assert ui_schema["hidden_factor"]["ui:widget"] == "hidden"


def test_field_overrides_in_generated_html():
    """Test that field overrides are properly applied in the generated form."""
    from rh import MeshBuilder

    mesh_spec = {"result": ["input_value"]}

    functions_spec = {"result": "return input_value * 3.14;"}

    initial_values = {"input_value": 1.0}

    field_overrides = {
        "input_value": {
            "title": "Radius",
            "minimum": 0,
            "maximum": 100,
            "ui:help": "Enter the radius value",
            "ui:widget": "range",
        }
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        builder = MeshBuilder(
            mesh_spec=mesh_spec,
            functions_spec=functions_spec,
            initial_values=initial_values,
            field_overrides=field_overrides,
            output_dir=tmpdir,
        )

        app_path = builder.build_app()
        html_content = app_path.read_text()

        # Extract form configuration
        config_match = re.search(
            r'const formConfig = ({.*?});', html_content, re.DOTALL
        )
        assert config_match

        form_config = json.loads(config_match.group(1))

        # Check schema overrides
        schema = form_config["schema"]
        assert schema["properties"]["input_value"]["title"] == "Radius"
        assert schema["properties"]["input_value"]["minimum"] == 0
        assert schema["properties"]["input_value"]["maximum"] == 100

        # Check UI schema overrides
        ui_schema = form_config["uiSchema"]
        assert ui_schema["input_value"]["ui:help"] == "Enter the radius value"
        assert ui_schema["input_value"]["ui:widget"] == "range"


if __name__ == "__main__":
    pytest.main([__file__])
