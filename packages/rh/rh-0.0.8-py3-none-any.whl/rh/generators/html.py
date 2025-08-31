"""
HTML Generator for creating complete web applications from mesh configurations.
"""

from typing import Dict, Any
from pathlib import Path
import json


class HTMLGenerator:
    """Generates complete HTML applications from mesh configurations."""

    def __init__(self):
        """Initialize the HTML generator."""
        self.template_dir = Path(__file__).parent.parent / "templates"

    def generate_app(self, config: Dict[str, Any], title: str = "Mesh App") -> str:
        """Generate complete HTML application.

        Args:
            config: Configuration dict from MeshBuilder.generate_config()
            title: Title for the HTML page

        Returns:
            Complete HTML content as string
        """
        # Generate JavaScript components
        mesh_config_js = f"const meshConfig = {json.dumps(config['propagation_rules'])}"
        mesh_propagator_js = self._generate_mesh_propagator_js(mesh_config_js)
        app_init_js = self._generate_app_initialization(config)

        # Generate the complete HTML
        return self._generate_base_html(
            title=title,
            mesh_functions=config["functions"],
            mesh_propagator=mesh_propagator_js,
            app_initialization=app_init_js,
        )

    def _generate_base_html(
        self,
        *,
        title: str,
        mesh_functions: str,
        mesh_propagator: str,
        app_initialization: str,
    ) -> str:
        """Generate the base HTML template with all components."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/css/bootstrap.min.css">
    <style>
        .mesh-form-container {{
            max-width: 800px;
            margin: 2rem auto;
            padding: 2rem;
        }}
        .readonly-field {{
            background-color: #f8f9fa;
        }}
        .field-group {{
            border: 1px solid #dee2e6;
            border-radius: 0.375rem;
            padding: 1rem;
            margin-bottom: 1rem;
        }}
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="mesh-form-container">
            <h1>{title}</h1>
            <div id="rjsf-form"></div>
        </div>
    </div>

    <!-- React Dependencies -->
    <script crossorigin src="https://unpkg.com/react@17/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@17/umd/react-dom.production.min.js"></script>
    
    <!-- Simple form library fallback -->
    <script>
        // Fallback form component if CDN fails
        window.SimpleFormComponent = function(props) {{
            const schema = props.schema || {{}};
            const formData = props.formData || {{}};
            const onChange = props.onChange;
            const uiSchema = props.uiSchema || {{}};
            
            function createField(key, fieldSchema, value) {{
                const fieldProps = {{
                    id: key,
                    name: key,
                    value: value || '',
                    onChange: function(e) {{
                        const newData = Object.assign({{}}, formData);
                        const newValue = fieldSchema.type === 'number' ? 
                            parseFloat(e.target.value) || 0 : e.target.value;
                        newData[key] = newValue;
                        if (onChange) onChange({{formData: newData}});
                    }}
                }};
                
                const uiOptions = uiSchema[key] || {{}};
                const isReadonly = uiOptions['ui:readonly'];
                const widget = uiOptions['ui:widget'];
                const help = uiOptions['ui:help'];
                
                let input;
                if (isReadonly) {{
                    fieldProps.readOnly = true;
                    fieldProps.className = 'form-control-plaintext';
                }} else {{
                    fieldProps.className = 'form-control';
                }}
                
                if (widget === 'range') {{
                    input = React.createElement('input', Object.assign({{}}, fieldProps, {{
                        type: 'range',
                        min: uiOptions.minimum || 0,
                        max: uiOptions.maximum || 100,
                        className: 'form-range'
                    }}));
                }} else if (fieldSchema.type === 'number') {{
                    fieldProps.type = 'number';
                    fieldProps.step = 'any';
                    input = React.createElement('input', fieldProps);
                }} else {{
                    fieldProps.type = 'text';
                    input = React.createElement('input', fieldProps);
                }}
                
                const label = React.createElement('label', {{
                    className: 'form-label',
                    htmlFor: key
                }}, fieldSchema.title || key);
                
                const helpText = help ? React.createElement('div', {{
                    className: 'form-text'
                }}, help) : null;
                
                return React.createElement('div', {{
                    className: 'mb-3',
                    key: key
                }}, label, input, helpText);
            }}
            
            const properties = schema.properties || {{}};
            const fields = Object.keys(properties).map(function(key) {{
                return createField(key, properties[key], formData[key]);
            }});
            
            return React.createElement('form', {{className: 'simple-form'}}, fields);
        }};
    </script>
    
    <!-- Try to load RJSF, fall back to simple form -->
    <script src="https://unpkg.com/react-jsonschema-form@1.8.1/dist/react-jsonschema-form.js"></script>

    <!-- Mesh Functions -->
    <script>
        {mesh_functions}
    </script>

    <!-- Mesh Propagator -->
    <script>
        {mesh_propagator}
    </script>

    <!-- App Initialization -->
    <script>
        {app_initialization}
    </script>
</body>
</html>"""

    def _generate_mesh_propagator_js(self, mesh_config_js: str) -> str:
        """Generate the mesh propagator JavaScript class."""
        return f"""class MeshPropagator {{
    constructor(mesh, functions, reverseMesh) {{
        this.mesh = mesh;
        this.functions = functions;
        this.reverseMesh = reverseMesh;
    }}
    
    createCallback(changedVariable) {{
        return (value, formData) => {{
            return this.propagate(changedVariable, value, formData);
        }};
    }}
    
    propagate(changedVariable, newValue, formData) {{
        const newFormData = {{...formData, [changedVariable]: newValue}};
        const computed = new Set();
        const queue = [...(this.reverseMesh[changedVariable] || [])];
        
        while (queue.length > 0) {{
            const funcName = queue.shift();
            
            if (computed.has(funcName)) {{
                console.error(`Cyclic computation detected: ${{funcName}}`);
                throw new Error(`Cyclic computation detected: ${{funcName}}`);
            }}
            
            computed.add(funcName);
            const args = this.mesh[funcName];
            
            try {{
                const argValues = args.map(arg => newFormData[arg]);
                const result = this.functions[funcName](...argValues);
                
                if (newFormData[funcName] !== result) {{
                    newFormData[funcName] = result;
                    
                    // Add dependent functions to queue
                    if (this.reverseMesh[funcName]) {{
                        queue.push(...this.reverseMesh[funcName].filter(f => !computed.has(f)));
                    }}
                }}
            }} catch (error) {{
                console.error(`Error computing ${{funcName}}:`, error);
                // Continue with other computations
            }}
        }}
        
        return newFormData;
    }}
    
    buildReverse(mesh) {{
        const reverse = {{}};
        for (const [funcName, argNames] of Object.entries(mesh)) {{
            for (const argName of argNames) {{
                if (!reverse[argName]) {{
                    reverse[argName] = [];
                }}
                reverse[argName].push(funcName);
            }}
        }}
        return reverse;
    }}
}}

// Initialize mesh propagator with configuration
{mesh_config_js};
const meshPropagator = new MeshPropagator(
    meshConfig.mesh,
    meshFunctions,
    meshConfig.reverseMesh
);"""

    def _generate_app_initialization(self, config: Dict[str, Any]) -> str:
        """Generate the main app initialization JavaScript."""
        rjsf_config = {
            "schema": config["schema"],
            "uiSchema": config["uiSchema"],
            "formData": config["initial_values"],
        }

        return f"""// Initialize form with fallback support
console.log("Starting app initialization...");

// Check if all dependencies are loaded
if (typeof React === 'undefined') {{
    console.error("React is not loaded");
    document.getElementById('rjsf-form').innerHTML = '<div class="alert alert-danger">React library failed to load</div>';
    throw new Error("React is not loaded");
}}

if (typeof ReactDOM === 'undefined') {{
    console.error("ReactDOM is not loaded");
    document.getElementById('rjsf-form').innerHTML = '<div class="alert alert-danger">ReactDOM library failed to load</div>';
    throw new Error("ReactDOM is not loaded");
}}

// Determine which form component to use and normalize UMD shapes
let FormComponent = null;
let useSimpleFallback = false;

function pickFormComponent(candidate) {{
    // candidate may be a function (component) or an object exposing keys like default or Form
    if (!candidate) return null;
    if (typeof candidate === 'function') return candidate;
    // common UMD shapes
    if (typeof candidate.default === 'function') return candidate.default;
    if (candidate.Form && typeof candidate.Form === 'function') return candidate.Form;
    if (candidate.default && candidate.default.Form && typeof candidate.default.Form === 'function') return candidate.default.Form;
    return null;
}}

if (typeof JSONSchemaForm !== 'undefined') {{
    console.log("✅ JSONSchemaForm global detected. Keys:", Object.keys(JSONSchemaForm));
    FormComponent = pickFormComponent(JSONSchemaForm);
    if (!FormComponent) console.warn('JSONSchemaForm found but no callable component detected; object keys:', Object.keys(JSONSchemaForm));
}}

// Also check other known globals used by different bundles
if (!FormComponent && typeof window.RJSFCore !== 'undefined') {{
    console.log('Detected window.RJSFCore:', Object.keys(window.RJSFCore));
    FormComponent = pickFormComponent(window.RJSFCore);
}}

if (!FormComponent && typeof window.RJSF !== 'undefined') {{
    console.log('Detected window.RJSF:', Object.keys(window.RJSF));
    FormComponent = pickFormComponent(window.RJSF);
}}

if (!FormComponent) {{
    console.warn("⚠️ No RJSF component resolved, using fallback component");
    FormComponent = window.SimpleFormComponent;
    useSimpleFallback = true;
}}

if (!FormComponent) {{
    console.error("❌ No form component available even after fallback");
    document.getElementById('rjsf-form').innerHTML = '<div class="alert alert-danger">No form component available</div>';
    throw new Error("No form component available");
}}

// If FormComponent is an object (UMD bundle) but not a function, try to create a small wrapper
if (typeof FormComponent === 'object' && typeof FormComponent !== 'function') {{
    console.log('FormComponent is object; attempting to wrap into callable component');
    const candidate = FormComponent;
    let inner = null;
    if (typeof candidate === 'function') inner = candidate;
    else if (typeof candidate.default === 'function') inner = candidate.default;
    else if (candidate.Form && typeof candidate.Form === 'function') inner = candidate.Form;
    else if (candidate.default && candidate.default.Form && typeof candidate.default.Form === 'function') inner = candidate.default.Form;

    if (inner) {{
        // wrapper component that forwards props
        FormComponent = function(props) {{
            return inner(props);
        }};
        console.log('Wrapped FormComponent created from inner function');
    }} else {{
        console.warn('Could not find inner component function in FormComponent bundle; falling back to SimpleFormComponent');
        FormComponent = window.SimpleFormComponent;
        useSimpleFallback = true;
    }}
}}

try {{
    console.log("Form component type:", typeof FormComponent);
    // Diagnostic: if using an object, show keys and types
    try {{
        if (typeof FormComponent === 'object') {{
            console.log('FormComponent object keys:', Object.keys(FormComponent));
            if (FormComponent.default) console.log('FormComponent.default typeof:', typeof FormComponent.default);
            if (FormComponent.Form) console.log('FormComponent.Form typeof:', typeof FormComponent.Form);
        }}
    }} catch (derr) {{
        console.warn('Diagnostic error inspecting FormComponent', derr);
    }}
    console.log("Using simple fallback:", useSimpleFallback);

    const formConfig = {json.dumps(rjsf_config)};

    // Create onChange handler that uses mesh propagator
    const onChange = ({{formData}}) => {{
        try {{
            console.log("Form data changed:", formData);
            // Check which field changed and propagate
            Object.keys(formData).forEach(key => {{
                if (meshPropagator.reverseMesh[key]) {{
                    const newFormData = meshPropagator.propagate(key, formData[key], formData);
                    // Update form with new data if changed
                    if (JSON.stringify(newFormData) !== JSON.stringify(formData)) {{
                        renderForm(newFormData);
                    }}
                }}
            }});
        }} catch (error) {{
            console.error("Error in onChange:", error);
        }}
    }};

    function renderForm(formData = formConfig.formData) {{
        try {{
            console.log("Rendering form with data:", formData);
            
            const element = React.createElement(FormComponent, {{
                schema: formConfig.schema,
                uiSchema: formConfig.uiSchema,
                formData: formData,
                onChange: onChange,
                onSubmit: ({{formData}}) => console.log("Data submitted: ", formData)
            }});
            
            ReactDOM.render(element, document.getElementById('rjsf-form'));
            console.log("Form rendered successfully");
        }} catch (error) {{
            console.error("Error rendering form:", error);
            document.getElementById('rjsf-form').innerHTML = 
                '<div class="alert alert-danger">Error rendering form: ' + error.message + '</div>';
        }}
    }}

    // Initial render
    console.log("Starting initial render...");
    renderForm();
    
}} catch (error) {{
    console.error("Error in app initialization:", error);
    document.getElementById('rjsf-form').innerHTML = 
        '<div class="alert alert-danger">App initialization failed: ' + error.message + '</div>';
}}"""
