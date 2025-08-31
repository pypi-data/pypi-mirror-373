# pytemplify
Text file generator framework using parsed dictionary data and Jinja2 templates.

## How to create your generator using `pytemplify`
Install uv:
```shell
curl -Ls https://astral.sh/uv/install.sh | sh
```
Install `pytemplify`:
```shell
pip install pytemplify
```
Generate the first skeleton of your generator using `mygen-init`:
```shell
cd <your-repo-path>
mygen-init
```
Complete the `TODO`s in modules; main implementation module is `parser_<your-generator-name>.py`.

Try to run:
```shell
uv pip install -r requirements.txt
uv venv
source .venv/bin/activate
<your-generator-name>
```
```shell
uv pip install nox
nox
```

## Running Tests and Linters with nox

To run all sessions (formatting, linting, and tests):

```shell
nox
```

To run only tests:

```shell
nox -s tests
```

To run only linting:

```shell
nox -s lint
```

To run only code formatting:

```shell
nox -s format_code
```

## Publishing to PyPI with uv

1. Build the package:

```shell
uv build
```

2. Publish to PyPI:

```shell
uv publish
```

For test PyPI, use:

```shell
uv publish --repository testpypi
```

## Using TemplateRenderer

The `TemplateRenderer` class is a powerful utility for rendering Jinja2 templates with special features like manual sections preservation and content injection.

### Basic Usage

```python
from pytemplify.renderer import TemplateRenderer
from pathlib import Path

# Create a renderer with data
data = {"project_name": "MyProject", "version": "1.0.0"}
renderer = TemplateRenderer(data)

# Render a string template
template = "Project: {{ project_name }}, Version: {{ version }}"
result = renderer.render_string(template)
print(result)  # Output: "Project: MyProject, Version: 1.0.0"

# Render a template file
renderer.render_file(Path("templates/config.ini.j2"))

# Generate files from a template directory
renderer.generate(Path("templates"), Path("output"))
```

### Manual Sections

Manual sections allow you to preserve user-modified content between template regenerations:

```python
template = """
# Configuration
project_name = {{ project_name }}

# Custom settings
MANUAL SECTION START: custom_settings
# Add your custom settings here
debug = True
MANUAL SECTION END
"""

# Previously rendered content with user modifications
previous = """
# Configuration
project_name = OldProject

# Custom settings
MANUAL SECTION START: custom_settings
# User added these settings
debug = True
verbose = True
log_level = DEBUG
MANUAL SECTION END
"""

# The manual section will be preserved in the new render
result = renderer.render_string(template, previous)
```

### Content Injection

You can inject content into specific parts of existing files:

```python
template = """
<!-- injection-pattern: imports -->
pattern: (?P<injection>import .*)
<!-- injection-string-start -->
import os
import sys
import json
<!-- injection-string-end -->
"""

existing_file = """
import os
import sys
# Other code here
"""

# Will inject the new import statements
result = renderer.inject_string(template, existing_file)
```

### Template Directory Generation

Generate an entire directory structure from templates:

```python
# Will process all .j2 files in templates/ and generate the corresponding 
# structure in output/ with rendered content
renderer.generate(Path("templates"), Path("output"))
```

For more details, see the API documentation in the code.

## TIPs
Activate uv virtual environment:
```shell
source .venv/bin/activate
```
Deactivate uv virtual environment:
```shell
deactivate
```