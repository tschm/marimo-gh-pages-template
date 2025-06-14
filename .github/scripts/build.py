"""
Build script for marimo notebooks.

This script exports marimo notebooks to HTML/WebAssembly format and generates
an index.html file that lists all the notebooks. It handles both regular notebooks
(from the notebooks/ directory) and apps (from the apps/ directory).

The script can be run from the command line with optional arguments:
    python .github/scripts/build.py [--output-dir OUTPUT_DIR]

The exported files will be placed in the specified output directory (default: _site).
"""

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "jinja2==3.1.3"
# ]
# ///

import warnings
import subprocess
import argparse
from typing import List
from pathlib import Path
import jinja2


def _export_html_wasm(notebook_path: Path, output_dir: Path, as_app: bool = False) -> bool:
    """Export a single marimo notebook to HTML/WebAssembly format.

    This function takes a marimo notebook (.py file) and exports it to HTML/WebAssembly format.
    If as_app is True, the notebook is exported in "run" mode with code hidden, suitable for
    applications. Otherwise, it's exported in "edit" mode, suitable for interactive notebooks.

    Args:
        notebook_path (Path): Path to the marimo notebook (.py file) to export
        output_dir (Path): Directory where the exported HTML file will be saved
        as_app (bool, optional): Whether to export as an app (run mode) or notebook (edit mode).
                                Defaults to False.

    Returns:
        bool: True if export succeeded, False otherwise
    """
    # Convert .py extension to .html for the output file
    output_path: Path = notebook_path.with_suffix(".html")

    # Base command for marimo export
    cmd: List[str] = ["uvx", "marimo", "export", "html-wasm", "--sandbox"]

    # Configure export mode based on whether it's an app or a notebook
    if as_app:
        print(f"Exporting {notebook_path} to {output_path} as app")
        cmd.extend(["--mode", "run", "--no-show-code"])  # Apps run in "run" mode with hidden code
    else:
        print(f"Exporting {notebook_path} to {output_path} as notebook")
        cmd.extend(["--mode", "edit"])  # Notebooks run in "edit" mode

    try:
        # Create full output path and ensure directory exists
        output_file: Path = output_dir / notebook_path.with_suffix(".html")
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Add notebook path and output file to command
        cmd.extend([str(notebook_path), "-o", str(output_file)])

        # Run marimo export command
        print(cmd)
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        # Handle marimo export errors
        warnings.warn(f"Error exporting {notebook_path}:")
        warnings.warn(e.stderr)
        return False
    except Exception as e:
        # Handle unexpected errors
        warnings.warn(f"Unexpected error exporting {notebook_path}: {e}")
        return False


def generate_index(output_dir: Path, notebooks_data: List[dict] | None = None, apps_data: List[dict] | None = None) -> None:
    """Generate an index.html file that lists all the notebooks.

    This function creates an HTML index page that displays links to all the exported
    notebooks. The index page includes the marimo logo and displays each notebook
    with a formatted title and a link to open it.

    Args:
        notebooks_data (List[dict]): List of dictionaries with data for notebooks
        apps_data (List[dict]): List of dictionaries with data for apps
        output_dir (Path): Directory where the index.html file will be saved

    Returns:
        None
    """
    print("Generating index.html")

    # Create the full path for the index.html file
    index_path: Path = output_dir / "index.html"

    # Ensure the output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Set up Jinja2 environment
        template_dir = Path(__file__).parent / "templates"
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=jinja2.select_autoescape(["html", "xml"])
        )

        # Load the template
        template = env.get_template("index.html.j2")

        # Render the template with notebook and app data
        rendered_html = template.render(notebooks=notebooks_data, apps=apps_data)

        # Write the rendered HTML to the index.html file
        with open(index_path, "w") as f:
            f.write(rendered_html)

    except IOError as e:
        # Handle file I/O errors
        print(f"Error generating index.html: {e}")
    except jinja2.exceptions.TemplateError as e:
        # Handle template errors
        print(f"Error rendering template: {e}")


def export(folder: Path, output_dir: Path, as_app: bool=False) -> List[dict]:
    """Export all marimo notebooks in a folder to HTML/WebAssembly format.

    This function finds all Python files in the specified folder and exports them
    to HTML/WebAssembly format using the export_html_wasm function. It returns a
    list of dictionaries containing the data needed for the template.

    Args:
        folder (Path): Path to the folder containing marimo notebooks
        output_dir (Path): Directory where the exported HTML files will be saved
        as_app (bool, optional): Whether to export as apps (run mode) or notebooks (edit mode).

    Returns:
        List[dict]: List of dictionaries with "display_name" and "html_path" for each notebook
    """
    # Check if the folder exists
    if not folder.exists():
        warnings.warn(f"Directory not found: {folder}")
        return []

    # Find all Python files recursively in the folder
    notebooks = list(folder.rglob("*.py"))

    # Exit if no notebooks were found
    if not notebooks:
        warnings.warn(f"No notebooks found in {folder}!")
        return []

    # For each successfully exported notebook, add its data to the notebook_data list
    notebook_data = [
        {
            "display_name": (nb.stem.replace("_", " ").title()),
            "html_path": str(nb.with_suffix(".html")),
        }
        for nb in notebooks
        if _export_html_wasm(nb, output_dir, as_app=as_app)
    ]

    return notebook_data


def main() -> None:
    """Main function to build marimo notebooks.

    This function:
    1. Parses command line arguments
    2. Exports all marimo notebooks in the 'notebooks' and 'apps' directories
    3. Generates an index.html file that lists all the notebooks

    Command line arguments:
        --output-dir: Directory where the exported files will be saved (default: _site)

    Returns:
        None
    """
    # Set up command line argument parsing
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Build marimo notebooks")
    parser.add_argument(
        "--output-dir", default="_site", help="Output directory for built files"
    )
    args: argparse.Namespace = parser.parse_args()

    # Convert output_dir to Path
    output_dir: Path = Path(args.output_dir)

    # Export notebooks from the notebooks/ directory
    notebooks_data = export(Path("notebooks"), output_dir, as_app=False)

    # Export apps from the apps/ directory
    apps_data = export(Path("apps"), output_dir, as_app=True)

    # Exit if no notebooks or apps were found
    if not notebooks_data and not apps_data:
        warnings.warn("No notebooks or apps found!")
        return

    # Generate the index.html file that lists all notebooks and apps
    generate_index(output_dir=output_dir, notebooks_data=notebooks_data, apps_data=apps_data)


if __name__ == "__main__":
    main()
