import click
import shutil
from pathlib import Path
from importlib import resources
from jinja2 import Environment, PackageLoader

@click.command()
@click.argument('project_name')
def main(project_name: str):
    """Initialize a new MATER project"""
    create_project(project_name)
    
    click.echo(f"\n✅ MATER project '{project_name}' initialized!")
    click.echo("\n🚀 Next steps:")
    click.secho(f"   cd {project_name}", fg='bright_blue', bold=True)
    click.secho("   uv sync", fg='bright_blue', bold=True)
    click.echo("\n🎮 Run your first MATER simulation:")
    click.secho("   uv run mater-cli run --example", fg='bright_blue', bold=True)
    click.echo("\n📊 Work with your own data:")
    click.echo("   - Complete config.toml with your provider & project info")
    click.echo("   - Add your raw datasets to data/raw/")
    click.echo("      Supported formats: CSV, JSON, Excel, Parquet, YAML, XML, TSV, Pickle")
    click.echo("   - Create scripts to transform dataset files in MATER-formatted data")
    click.secho("     uv run mater-cli create script", fg='bright_blue', bold=True)
    click.echo("   - Customize the generated scripts in transforms/datasets/")
    click.echo("   - Run your scripts to create MATER-formatted data")
    click.echo("     → JSON files are saved in data/input/")
    click.echo("   - Create the dimensions hierarchy from your MATER-formatted data")
    click.secho("     uv run mater-cli create dimensions-hierarchy", fg='bright_blue', bold=True)
    click.echo("     → JSON file is saved in data/dimensions_hierarchy/")
    click.echo("   - Run your own MATER simulation:")
    click.secho("     uv run mater-cli run", fg='bright_blue', bold=True)


def create_project(project_name: str) -> None:
    """Create MATER project structure"""
    project_path = Path(project_name)
    
    if project_path.exists():
        click.echo(f"❌ Project '{project_name}' already exists!")
        return
    
    project_path.mkdir()
    generate_files_from_templates(project_path, project_name)
    setup_structure(project_path)
    display_project_structure(project_path)

def generate_files_from_templates(project_path: Path, project_name: str) -> None:
    """Generate project files from templates"""
    env = Environment(loader=PackageLoader('init_mater_project', 'templates'))
    
    files_to_generate = [
        (".gitignore.j2", ".gitignore"),
        (".python-version.j2", ".python-version"),
        ("config.toml.j2", "config.toml"),
        ("main.py.j2", "main.py"),
        ("pyproject.toml.j2", "pyproject.toml"),
        ("README.md.j2", "README.md"),
        ("settings.py.j2", "settings.py"),
        ("commands/__init__.py.j2", "commands/__init__.py"),
        ("commands/build_input_data.py.j2", "commands/build_input_data.py"),
        ("commands/build_dimensions.py.j2", "commands/build_dimensions.py"),
        ("commands/generate_data_script.py.j2", "commands/generate_data_script.py"),
        ("commands/list_simulation.py.j2", "commands/list_simulation.py"),
        ("commands/map_dimensions.py.j2", "commands/map_dimensions.py"),
        ("commands/run.py.j2", "commands/run.py"),
    ]
    
    for _, destination in files_to_generate:
        output_file = project_path / destination
        output_file.parent.mkdir(parents=True, exist_ok=True)
    
    for template_name, destination in files_to_generate:
        template = env.get_template(template_name)
        content = template.render(project_name=project_name)
        (project_path / destination).write_text(content)
    
    click.echo("\n...generating project files from templates")

def setup_structure(project_path: Path) -> None:
    """Setup project structure with folders and files"""
    folders_to_copy = ["data", "examples", "outputs", "transforms"]

    for folder in folders_to_copy:
        shutil.copytree(resources.files("init_mater_project") / "templates" / folder, project_path / folder)

    click.echo("...setting up project structure")


def display_project_structure(project_path: Path) -> None:
    """Display the complete project structure"""
    _display_directory_tree(project_path, project_path.name)


def _display_directory_tree(path: Path, name: str, prefix: str = "") -> None:
    """Recursively display directory tree"""
    click.echo(f"\n{prefix}{name}/")
    
    items = [
        item for item in path.iterdir() 
        if not (item.is_file() and item.name == ".gitkeep")
    ]
    items = sorted(items, key=lambda x: (x.is_file(), x.name))
    
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        current_prefix = prefix + ("└── " if is_last else "├── ")
        next_prefix = prefix + ("    " if is_last else "│   ")
        
        if item.is_dir():
            if item.name in ["__pycache__", ".git"]:
                continue  
            click.echo(f"{current_prefix}{item.name}/")
            _display_directory_contents(item, next_prefix)
        else:
            click.echo(f"{current_prefix}{item.name}")


def _display_directory_contents(path: Path, prefix: str) -> None:
    """Display contents of a directory"""
    items = [
        item for item in path.iterdir() 
        if not (item.is_file() and item.name == ".gitkeep")
    ]
    items = sorted(items, key=lambda x: (x.is_file(), x.name))
    
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        current_prefix = prefix + ("└── " if is_last else "├── ")
        next_prefix = prefix + ("    " if is_last else "│   ")
        
        if item.is_dir():
            click.echo(f"{current_prefix}{item.name}/")
            _display_directory_contents(item, next_prefix)
        else:
            click.echo(f"{current_prefix}{item.name}")