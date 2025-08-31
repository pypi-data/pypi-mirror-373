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
        return f'''<!DOCTYPE html>
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

    <!-- RJSF Dependencies -->
    <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@rjsf/core@5/dist/rjsf-core.umd.js"></script>
    <script src="https://unpkg.com/@rjsf/utils@5/dist/rjsf-utils.umd.js"></script>
    <script src="https://unpkg.com/@rjsf/validator-ajv8@5/dist/rjsf-validator-ajv8.umd.js"></script>
    <script src="https://unpkg.com/@rjsf/bootstrap-4@5/dist/rjsf-bootstrap-4.umd.js"></script>

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
</html>'''

    def _generate_mesh_propagator_js(self, mesh_config_js: str) -> str:
        """Generate the mesh propagator JavaScript class."""
        return f'''class MeshPropagator {{
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
);'''

    def _generate_app_initialization(self, config: Dict[str, Any]) -> str:
        """Generate the main app initialization JavaScript."""
        rjsf_config = {
            "schema": config["schema"],
            "uiSchema": config["uiSchema"],
            "formData": config["initial_values"],
        }

        return f'''// Initialize RJSF form
const Form = JSONSchemaForm.default;
const validator = validator;

const formConfig = {json.dumps(rjsf_config)};

// Create onChange handler that uses mesh propagator
const onChange = ({{formData}}, id) => {{
    if (id && meshPropagator.reverseMesh[id]) {{
        const newFormData = meshPropagator.propagate(id, formData[id], formData);
        // Update form with new data
        renderForm(newFormData);
    }}
}};

function renderForm(formData = formConfig.formData) {{
    const element = React.createElement(Form, {{
        schema: formConfig.schema,
        uiSchema: formConfig.uiSchema,
        formData: formData,
        onChange: onChange,
        validator: validator,
        onSubmit: ({{formData}}) => console.log("Data submitted: ", formData)
    }});
    
    ReactDOM.render(element, document.getElementById('rjsf-form'));
}}

// Initial render
renderForm();'''
