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
# Run pytest discovery from the project root (recommended)
python -m pytest
```

## Demo

Try the examples:

```bash
python demo.py      # Multiple example apps
python example.py   # Simple temperature converter with server
python persistent_apps_example.py  # Shows app directory management
```

## App Directory Management

RH automatically manages app storage for persistent applications:

### Default Behavior

```python
builder = MeshBuilder(mesh_spec, functions_spec, initial_values)

# App name inferred from title, stored in RH_APP_FOLDER
app_path = builder.build_app(title="Temperature Converter")
# Creates: ~/.rh/apps/temperature_converter/index.html

# Explicit app name
app_path = builder.build_app(title="My App", app_name="custom_name")
# Creates: ~/.rh/apps/custom_name/index.html
```

### Directory Configuration

```python
from rh.util import RH_APP_FOLDER, get_app_directory

# Check current app folder location
print(f"Apps stored in: {RH_APP_FOLDER}")

# Get path for specific app
app_dir = get_app_directory("my_calculator")
```

### Environment Variables

Control where RH stores apps by setting environment variables:

```bash
# Custom app folder location
export RH_APP_FOLDER="/path/to/my/apps"

# Custom local data folder (apps will be in $RH_LOCAL_DATA_FOLDER/apps)
export RH_LOCAL_DATA_FOLDER="/path/to/my/data"
```

### Manual Directory Control

For full control over output location:

```python
builder = MeshBuilder(mesh_spec, functions_spec, initial_values)
builder.output_dir = "/path/to/specific/location"
app_path = builder.build_app(title="My App")
```

## Design & Philosophy

This section communicates the design principles and architectural decisions that guide the development of RH, helping both users understand the framework's approach and contributors align with the project's vision. **Contributors are welcome!!!**

### Core Design Principles

**🧩 Declarative over Imperative**
- Users describe *what* relationships exist between variables, not *how* to update the UI
- The framework handles the complex orchestration of updates, event handling, and DOM manipulation
- Mental model: "I have variables that relate to each other" → "I get a working interactive app"

**🔄 Convention over Configuration**
- Smart defaults based on naming patterns (`slider_*`, `readonly_*`, `hidden_*`)
- Type inference from initial values (float → number input, bool → checkbox)
- Zero-config working apps, with escape hatches for customization when needed

**⚡ Functional Programming & Immutability**
- Pure functions with no side effects in core logic
- Immutable configuration objects generated once and used everywhere
- Predictable behavior through referential transparency
- Data transformations rather than object mutations

### Architectural Decisions

**📐 Clean Architecture**
```
┌─────────────────┐
│   MeshBuilder   │  ← Facade/Interface Layer
│    (Facade)     │
├─────────────────┤
│ Generators      │  ← Application Logic
│ • HTML          │
│ • RJSF Schema   │
├─────────────────┤
│ Core Logic      │  ← Business Logic
│ • Type Inference│
│ • Propagation   │
│ • Validation    │
├─────────────────┤
│ Infrastructure  │  ← Framework/Tools
│ • HTTP Server   │
│ • File I/O      │
│ • Templates     │
└─────────────────┘
```

**🔧 Separation of Concerns**
- **Specification Layer**: Parse and validate user input (mesh specs, functions)
- **Configuration Layer**: Transform specs into explicit, normalized config
- **Generation Layer**: Create output artifacts (HTML, JS, schemas) from config
- **Runtime Layer**: Serve applications and handle deployment

**🎯 Single Source of Truth (SSOT)**
- The `generate_config()` method produces the canonical representation
- All downstream components (HTML generator, RJSF schemas, JS functions) consume only this config
- No scattered state or multiple sources of truth

**🔌 Dependency Injection & Plugin Architecture**
- Pluggable components for different output formats
- Registry pattern for optional tool detection (Jinja2, esbuild, etc.)
- Interface-based design allowing custom generators and processors

### Development Philosophy

**📚 Zero Dependencies by Design**
- Core functionality works with Python stdlib only
- Optional enhancements auto-detected and registered
- Reduces deployment complexity and increases reliability

**🧪 Test-Driven Development**
- Tests written first to clarify requirements and edge cases
- Comprehensive test coverage (24+ tests) ensuring behavioral correctness
- Integration tests verify end-to-end functionality

**📖 Documentation as Code**
- README examples are tested as part of the test suite
- Docstrings include type hints and behavioral descriptions
- Self-documenting code through clear naming and structure

**🌱 Incremental Complexity**
- Simple use cases work with minimal code
- Advanced features available through progressive disclosure
- Each abstraction level serves a clear purpose

### Contributor Guidelines

**🤝 What We Welcome**
- **New Generators**: Support for other UI frameworks (Vue, Angular, Svelte)
- **Input Parsers**: YAML/TOML mesh specs, Excel formula parsing, natural language
- **Enhanced Conventions**: More naming patterns, automatic grouping, layout hints
- **Performance Optimizations**: Faster propagation algorithms, caching strategies
- **Developer Experience**: Better error messages, debugging tools, IDE integration

**🎨 Code Style Expectations**
- **Functional first**: Prefer pure functions and data transformations
- **Type hints**: All public APIs should be fully annotated
- **Docstrings**: Include behavior descriptions and simple doctests where applicable
- **Modular design**: Single responsibility principle, composable components
- **Immutable data**: Avoid mutation, prefer transformation and copying

**🏗️ Architectural Consistency**
- New features should extend existing patterns rather than introduce new paradigms
- Maintain the declarative user interface - complexity hidden behind simple APIs
- Follow the SSOT principle - all generators work from the same configuration
- Preserve zero-dependency core with optional enhancements

**🔍 Testing Philosophy**
- Write tests first to clarify the expected behavior
- Test both happy paths and edge cases
- Include integration tests for user-facing workflows
- Ensure examples in documentation actually work

This framework embodies the principle that **complexity should be in the implementation, not the interface**. Users describe simple relationships; the framework handles the complexity of turning those into rich, interactive applications.

## License

MIT License - see LICENSE file for details.
