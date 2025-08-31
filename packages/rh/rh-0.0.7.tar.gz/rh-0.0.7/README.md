# RH - Reactive Html Framework

Transform variable relationships into interactive web applications with real-time updates.

## Quick Start

```python
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
initial_values = {
    "temp_celsius": 20.0
}

# Create and build the app
builder = MeshBuilder(mesh_spec, functions_spec, initial_values)
app_path = builder.build_app(title="Temperature Converter")

# Serve it locally
builder.serve(port=8080)
```

## Features

- **Bidirectional Dependencies**: Variables can depend on each other cyclically
- **Real-time Updates**: Changes propagate instantly through the mesh
- **Convention over Configuration**: Smart defaults based on variable names
- **Type Inference**: Automatic UI widget selection from initial values
- **Zero External Dependencies**: Works with Python stdlib only

## UI Conventions

Variable names automatically determine UI behavior:

```python
initial_values = {
    "slider_opacity": 50,        # → Range slider (0-100)
    "readonly_result": 0,        # → Read-only display
    "hidden_internal": 10,       # → Hidden field
    "color_theme": "#ff0000",    # → Color picker
    "date_created": "2023-01-01" # → Date input
}
```

## Advanced Example

```python
# Physics calculator with custom field overrides
mesh_spec = {
    "kinetic_energy": ["mass", "velocity"],
    "momentum": ["mass", "velocity"],
    "total_energy": ["kinetic_energy", "potential_energy"]
}

functions_spec = {
    "kinetic_energy": "return 0.5 * mass * velocity * velocity;",
    "momentum": "return mass * velocity;",
    "total_energy": "return kinetic_energy + potential_energy;"
}

field_overrides = {
    "mass": {
        "title": "Mass (kg)",
        "minimum": 0.1,
        "maximum": 1000,
        "ui:help": "Object mass in kilograms"
    }
}

builder = MeshBuilder(mesh_spec, functions_spec, 
                     initial_values={"mass": 10, "velocity": 5, "potential_energy": 100},
                     field_overrides=field_overrides)
```

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

## Demo

Try the examples:

```bash
python demo.py      # Multiple example apps
python example.py   # Simple temperature converter with server
```

## License

MIT License - see LICENSE file for details.
