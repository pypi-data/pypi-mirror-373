# jnjrender

**jnjrender** is a Python command-line application designed to render [Jinja2](https://jinja.palletsprojects.com/) templates into YAML files using variables from a specified YAML file. It allows for flexible templating by combining the power of Jinja2 and YAML, making it easy to create complex YAML configurations with dynamic content.

## Features

- Render Jinja2 templates with values from a YAML file.
- Automatically detect the correct Jinja2 template file when a directory is provided, based on the `template` key in the YAML file.
- Output rendered content to the console or save it to a file.
- Preserve file permissions of the Jinja2 template when saving the rendered output.
- Simple command-line interface for ease of use.

## Installation

Clone this repository and install the requirements:

```bash
git clone https://github.com/yourusername/jnjrender.git
cd jnjrender
pip install -r requirements.txt
```

## Usage

### Render a Jinja2 Template File
To render a specific Jinja2 template file with variables from a YAML file:

```bash
python jnjrender.py template.j2 variables.yaml --output output.yaml
```

If no output file is specified, the rendered content will be printed to the console:

```bash
python jnjrender.py template.j2 variables.yaml
```

### Render a Template from a Directory
If the Jinja2 template is located in a directory, and the YAML file contains a `template` key, `jnjrender` will automatically locate the correct template file:

- YAML file (`variables.yaml`):
  ```yaml
  template: example
  ```

- Command:
  ```bash
  python jnjrender.py templates/ variables.yaml --output output.yaml
  ```

In this case, `jnjrender` will look for `templates/example.yaml.j2` and render it using the variables from `variables.yaml`.

### Preserve File Permissions
When saving the rendered output to a file, `jnjrender` will apply the same file permissions as the original Jinja2 template.

## Examples

#### Render a Specific Template
```bash
python jnjrender.py template.j2 variables.yaml --output output.yaml
```

#### Render a Template from a Directory
```bash
python jnjrender.py templates/ variables.yaml --output output.yaml
```

#### Print Rendered Content to Console
```bash
python jnjrender.py template.j2 variables.yaml
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
