# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "jinja2==3.1.3"
# ]
# ///

import sys
from pathlib import Path
from jinja2 import Template


def get_filenames(directory):
    """Get the base filenames (without extension) of all Python files in the directory."""
    path = Path(directory)
    return [file.stem for file in path.glob("*.py")]

def main():
    # Check if the template file path is provided
    if len(sys.argv) < 3:
        print("Usage: python render_template.py <template_file> <output_file>")
        sys.exit(1)
    
    template_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Get lists of notebooks and apps
    notebooks = get_filenames("notebooks")
    apps = get_filenames("apps")
    
    # Read the template
    with open(template_file, 'r') as f:
        template_content = f.read()
    
    # Create a Jinja2 template
    template = Template(template_content)
    
    # Render the template with the data
    rendered_content = template.render(notebooks=notebooks, apps=apps)
    
    # Write the output
    with open(output_file, 'w') as f:
        f.write(rendered_content)
    
    print(f"Template rendered successfully to {output_file}")

if __name__ == "__main__":
    main()