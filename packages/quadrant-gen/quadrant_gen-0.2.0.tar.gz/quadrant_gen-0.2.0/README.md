# Quadrant Generator

A Python library for creating quadrant charts with customizable labels and data points, optimized for web applications and API integrations.

## Features

- Create quadrant charts from CSV strings or data points
- Customizable axis labels and titles
- Automatic text positioning to prevent overlap
- Generate base64-encoded images for easy web integration
- Clean, minimalist design

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/ceccode/quadrant-gen.git
cd quadrant-gen

# Install the package
pip install -e .
```

### Using pip

```bash
pip install quadrant-gen
```

## Usage

The library is designed to be used programmatically in your Python applications, particularly for web applications and APIs.

### CSV Format

Your CSV file should have the following columns:
- `name`: Name of the data point
- `description`: Description of the data point
- `x`: X-coordinate (0.0 to 1.0)
- `y`: Y-coordinate (0.0 to 1.0)

Example:
```csv
name,description,x,y
Product A,High quality,0.2,0.8
Product B,Low cost,0.7,0.3
```

### Python API

#### Using CSV String Input

```python
from quadrant_gen.chart import csv_to_quadrant_chart

# CSV string with your data
csv_string = """
name,description,x,y
Product A,High quality,0.2,0.8
Product B,Low cost,0.7,0.3
"""

# Generate chart directly to base64-encoded image
base64_image = csv_to_quadrant_chart(
    csv_string=csv_string,
    title="My Quadrant Chart",
    x_left="Low X",
    x_right="High X",
    y_bottom="Low Y",
    y_top="High Y",
    format="png"  # or "pdf"
)

# Use the base64 image in HTML
html = f'<img src="{base64_image}" alt="Quadrant Chart">'  
```

#### Using Data Points

```python
from quadrant_gen.chart import generate_quadrant_chart, sample_points

# Use sample data
points = sample_points()

# Or create your own data
points = [
    {"label": "Item 1\n(Description)", "x": 0.2, "y": 0.8},
    {"label": "Item 2\n(Description)", "x": 0.7, "y": 0.3},
]

# Generate chart directly to base64-encoded image
base64_image = generate_quadrant_chart(
    points=points,
    title="My Quadrant Chart",
    x_left="Low X",
    x_right="High X",
    y_bottom="Low Y",
    y_top="High Y",
    format="png"  # or "pdf"
)
```

## Examples

The following examples are included in the repository:

- **Simple Integration Example**: `examples/integration_example.py` - Shows how to use the library in a Python script
- **Flask API Example**: `examples/flask_api_example.py` - RESTful API for generating charts
- **Flask CSV App**: `examples/flask_csv_app/` - Web application with CSV input form

## Integration with Web Applications

The Quadrant Generator is optimized for web applications and API integrations:

### Flask Integration Example

```python
# Important: Set matplotlib backend to 'Agg' before importing any matplotlib modules
# This is required for web applications to avoid GUI-related errors
import matplotlib
matplotlib.use('Agg')

from flask import Flask, render_template_string
from quadrant_gen.chart import csv_to_quadrant_chart

app = Flask(__name__)

@app.route('/')
def index():
    # Sample CSV data
    csv_data = """
name,description,x,y
Product A,High quality,0.2,0.8
Product B,Low cost,0.7,0.3
    """.strip()
    
    # Generate chart as base64 image
    base64_image = csv_to_quadrant_chart(
        csv_string=csv_data,
        title="Product Analysis",
        x_left="Low Cost", x_right="High Cost",
        y_bottom="Low Value", y_top="High Value"
    )
    
    # Return HTML with embedded image
    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Quadrant Chart Example</title>
        </head>
        <body>
            <h1>Product Analysis</h1>
            <img src="{{ chart }}" alt="Quadrant Chart">
        </body>
        </html>
    """, chart=base64_image)

if __name__ == '__main__':
    app.run(debug=True)
```

> **Note:** When using Matplotlib in web applications, you must set the backend to a non-interactive one like 'Agg' before importing any Matplotlib modules. This prevents GUI-related errors, especially on macOS where GUI operations must be on the main thread.

See the complete Flask integration example in `examples/flask_api_example.py`.

### Flask CSV Web Application

The repository includes a complete web application for generating quadrant charts from CSV data:

```bash
# Run the Flask CSV app
cd examples/flask_csv_app
python app.py
# Then open http://127.0.0.1:5001/ in your browser
```

This application provides:
- A form for entering CSV data
- Options to customize chart title and axis labels
- Preview of the generated chart
- Download options for PNG or PDF formats

See `examples/flask_csv_app/` for the complete application.

### API Integration

The library is perfect for API services that need to generate charts on-the-fly:

```python
# In a FastAPI application
from fastapi import FastAPI, Response
from pydantic import BaseModel
from quadrant_gen.chart import csv_to_quadrant_chart

app = FastAPI()

class ChartRequest(BaseModel):
    csv_data: str
    title: str = "Quadrant Chart"
    x_left: str = "Low X"
    x_right: str = "High X"
    y_bottom: str = "Low Y"
    y_top: str = "High Y"

@app.post("/generate-chart/")
async def generate_chart(request: ChartRequest):
    # Generate base64 image
    base64_image = csv_to_quadrant_chart(
        csv_string=request.csv_data,
        title=request.title,
        x_left=request.x_left,
        x_right=request.x_right,
        y_bottom=request.y_bottom,
        y_top=request.y_top
    )
    
    # Return JSON with the base64 image
    return {"chart_data": base64_image}
```

### Output Formats

The library generates base64-encoded images in two formats:

- **PNG**: Web-friendly format for digital display
- **PDF**: Vector format for high-quality printing and scaling

## Contributing

### For Developers

If you're a developer looking to contribute or maintain this package:

- See [PUBLISHING.md](PUBLISHING.md) for instructions on how to build and publish new versions to PyPI

## License

MIT
