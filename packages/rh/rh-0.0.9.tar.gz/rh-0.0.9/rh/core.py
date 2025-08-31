"""
Core RH (Reactive Html Framework) module.

This module implements the main MeshBuilder class for creating reactive
computational meshes with interactive web interfaces.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from pathlib import Path
import os


@dataclass
class MeshBuilder:
    """Main class for building reactive mesh applications.

    A mesh defines relationships between variables through functions,
    enabling bidirectional dependencies and real-time updates in web interfaces.
    """

    mesh_spec: Dict[str, Any]
    functions_spec: Dict[str, Any]
    initial_values: Dict[str, Any] = field(default_factory=dict)
    field_overrides: Dict[str, Any] = field(default_factory=dict)
    ui_config: Dict[str, Any] = field(default_factory=dict)
    output_dir: Optional[str] = None

    def __post_init__(self):
        """Initialize the mesh after construction."""
        self.mesh = self._parse_mesh(self.mesh_spec)

    def _get_output_dir(self, app_name: Optional[str] = None) -> str:
        """Get the output directory for the app.

        Args:
            app_name: Optional name for the app. If provided and no output_dir
                     is set, will use RH_APP_FOLDER/app_name

        Returns:
            Path to the output directory
        """
        if self.output_dir:
            return self.output_dir
        else:
            # Import here to allow dynamic updates during testing
            from .util import RH_APP_FOLDER

            if app_name:
                return os.path.join(RH_APP_FOLDER, app_name)
            else:
                return os.path.join(RH_APP_FOLDER, "default_app")

    def _parse_mesh(self, mesh_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Parse mesh specification from various formats.

        Currently supports direct dict format.
        """
        if isinstance(mesh_spec, dict):
            return mesh_spec
        else:
            raise ValueError(f"Unsupported mesh_spec type: {type(mesh_spec)}")

    def generate_config(self) -> Dict[str, Any]:
        """Generate explicit configuration from inputs and conventions.

        This is the key method - everything downstream uses only this config.
        """
        config = {
            "schema": self._generate_json_schema(),
            "uiSchema": self._generate_ui_schema(),
            "functions": self._resolve_functions(),
            "propagation_rules": self._build_propagation_rules(),
            "initial_values": self.initial_values,
            "mesh": self.mesh,
        }

        return config

    def _generate_json_schema(self) -> Dict[str, Any]:
        """Generate JSON Schema from mesh and initial values."""
        all_variables = self._get_all_variables()
        schema = {"type": "object", "properties": {}, "required": []}

        for var_name in all_variables:
            var_schema = self._infer_variable_schema(var_name)
            schema["properties"][var_name] = var_schema

            # Apply field overrides
            if var_name in self.field_overrides:
                schema["properties"][var_name].update(self.field_overrides[var_name])

        return schema

    def _infer_variable_schema(self, var_name: str) -> Dict[str, Any]:
        """Infer JSON Schema for a variable based on initial values.

        Type inference rules:
        - bool → boolean schema
        - int → integer schema
        - float → number schema
        - str → string schema
        - list → array schema
        - Default (no initial value) → number schema

        Args:
            var_name: Name of the variable to infer schema for

        Returns:
            JSON Schema dictionary for the variable
        """
        if var_name in self.initial_values:
            value = self.initial_values[var_name]
            if isinstance(value, bool):
                return {"type": "boolean"}
            elif isinstance(value, int):
                return {"type": "integer"}
            elif isinstance(value, float):
                return {"type": "number"}
            elif isinstance(value, str):
                return {"type": "string"}
            elif isinstance(value, list):
                return {"type": "array"}

        # Default to number for computed variables
        return {"type": "number"}

    def _generate_ui_schema(self) -> Dict[str, Any]:
        """Generate RJSF UI Schema with conventions and overrides."""
        ui_schema = {}
        all_variables = self._get_all_variables()

        for var_name in all_variables:
            ui_config = self._apply_ui_conventions(var_name)

            # Apply field overrides
            if var_name in self.field_overrides:
                ui_config.update(
                    {
                        k: v
                        for k, v in self.field_overrides[var_name].items()
                        if k.startswith("ui:")
                    }
                )

            if ui_config:
                ui_schema[var_name] = ui_config

        return ui_schema

    def _apply_ui_conventions(self, var_name: str) -> Dict[str, Any]:
        """Apply naming conventions to determine UI widgets.

        Supported conventions:
        - slider_*: Creates range input with 0-100 range
        - readonly_*: Makes field read-only
        - hidden_*: Creates hidden input field
        - color_*: Creates color picker widget
        - date_*: Creates date input widget

        Computed variables (those with dependencies in the mesh) are made
        readonly by default unless they have a slider_ prefix.

        Args:
            var_name: Name of the variable to apply conventions to

        Returns:
            Dictionary of UI configuration options
        """
        ui_config = {}

        # Prefix-based conventions
        if var_name.startswith("slider_"):
            ui_config.update({"ui:widget": "range", "minimum": 0, "maximum": 100})
        elif var_name.startswith("readonly_"):
            ui_config["ui:readonly"] = True
        elif var_name.startswith("hidden_"):
            ui_config["ui:widget"] = "hidden"
        elif var_name.startswith("color_"):
            ui_config["ui:widget"] = "color"
        elif var_name.startswith("date_"):
            ui_config["ui:widget"] = "date"

        # Check if this is a computed variable (has dependencies)
        if var_name in self.mesh:
            # If there is an explicit initial value for this computed variable,
            # allow it to be editable (useful for bidirectional/demo cases).
            if var_name in self.initial_values:
                # keep it editable
                pass
            else:
                # This is a computed variable - make it readonly by default
                if "ui:readonly" not in ui_config and not var_name.startswith(
                    "slider_"
                ):
                    ui_config["ui:readonly"] = True

        return ui_config

    def _get_all_variables(self) -> set:
        """Get all variables (inputs and outputs) in the mesh."""
        variables = set(self.mesh.keys())  # Output variables
        for args in self.mesh.values():
            variables.update(args)  # Input variables
        return variables

    def _resolve_functions(self) -> str:
        """Resolve and bundle JavaScript functions."""
        # Simple implementation for now - just return the functions as a JS object
        js_functions = []
        for name, code in self.functions_spec.items():
            # For inline functions, wrap in function syntax
            if isinstance(code, str) and not code.strip().startswith("function"):
                args = self.mesh.get(name, [])
                func_code = f"function({', '.join(args)}) {{ {code} }}"
            else:
                func_code = code
            js_functions.append(f'"{name}": {func_code}')

        return f"const meshFunctions = {{{','.join(js_functions)}}};"

    def _build_propagation_rules(self) -> Dict[str, Any]:
        """Build propagation rules for the mesh."""
        return {"reverseMesh": self._build_reverse_mesh(), "mesh": self.mesh}

    def _build_reverse_mesh(self) -> Dict[str, list]:
        """Build reverse mapping from arguments to functions."""
        reverse = {}
        for func_name, arg_names in self.mesh.items():
            for arg_name in arg_names:
                if arg_name not in reverse:
                    reverse[arg_name] = []
                reverse[arg_name].append(func_name)
        return reverse

    def build_components_from_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate RJSF components from explicit config.

        Args:
            config: Configuration dictionary from generate_config()

        Returns:
            Dict with component specifications for external use
        """
        return {
            "rjsf_schema": config["schema"],
            "rjsf_ui_schema": config["uiSchema"],
            "js_functions_bundle": config["functions"],
            "propagation_config": config["propagation_rules"],
        }

    def build_app(
        self,
        *,
        title: str = "Mesh App",
        serve: bool = False,
        port: int = 8080,
        app_name: Optional[str] = None,
        embed_rjsf: bool = False,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Path:
        """Generate complete HTML app with all assets bundled.

        Args:
            title: Title for the HTML page
            serve: Whether to start a development server
            port: Port for development server
            app_name: Name for the app (used for directory if output_dir not set)

        Returns:
            Path to the generated HTML file
        """
        from .generators.html import HTMLGenerator

        config = self.generate_config()

        # Infer app_name from title if not provided
        if app_name is None:
            app_name = title.lower().replace(" ", "_")

        output_dir = self._get_output_dir(app_name)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        html_generator = HTMLGenerator()
        # Attach meta information to config for generator to render descriptions
        if meta:
            config["meta"] = meta
        html_content = html_generator.generate_app(config, title, embed_rjsf=embed_rjsf)

        app_file = output_path / "index.html"
        app_file.write_text(html_content)

        if serve:
            self.serve(output_dir, port=port)

        return app_file

    def serve(self, directory: Optional[str] = None, port: int = 8080):
        """Serve the app locally for development.

        Args:
            directory: Directory to serve (if not provided, uses output_dir logic)
            port: Port to serve on
        """
        from .util import serve_directory

        if directory is None:
            directory = self._get_output_dir()

        serve_directory(directory, port=port)
