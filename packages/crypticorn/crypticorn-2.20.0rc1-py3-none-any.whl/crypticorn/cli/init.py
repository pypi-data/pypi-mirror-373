import importlib.resources
import subprocess
from pathlib import Path

import click

import crypticorn.cli.templates as templates


def get_git_root() -> Path:
    """Get the root directory of the git repository."""
    try:
        return Path(
            subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"], text=True
            ).strip()
        )
    except Exception:
        return Path.cwd()


def copy_template(template_name: str, target_path: Path):
    """Copy a template file to the target path."""
    with (
        importlib.resources.files(templates)
        .joinpath(template_name)
        .open("r") as template_file
    ):
        content = template_file.read()

    target_path.parent.mkdir(parents=True, exist_ok=True)
    with target_path.open("w") as f:
        f.write(content)

    click.secho(f"✅ Created: {target_path}", fg="green")


def check_file_exists(path: Path, force: bool):
    if path.exists() and not force:
        click.secho("File already exists, use --force / -f to overwrite", fg="red")
        return False
    return True


@click.group()
def init_group():
    """Initialize files like CI configs, linters, etc."""
    pass


@init_group.command("ruff")
@click.option("-f", "--force", is_flag=True, help="Force overwrite the ruff.yml")
def init_ruff(force):
    """Add .github/workflows/ruff.yml"""
    root = get_git_root()
    target = root / ".github/workflows/ruff.yml"
    if target.exists() and not force:
        click.secho("File already exists, use --force / -f to overwrite", fg="red")
        return
    copy_template("ruff.yml", target)


@init_group.command("docker")
@click.option(
    "-o", "--output", type=click.Path(), help="Custom output path for the Dockerfile"
)
@click.option("-f", "--force", is_flag=True, help="Force overwrite the Dockerfile")
def init_docker(output, force):
    """Add Dockerfile"""
    root = get_git_root()
    if output and Path(output).is_file():
        click.secho("Output path is a file, please provide a directory path", fg="red")
        return
    target = (Path(output) if output else root) / "Dockerfile"
    if not check_file_exists(target, force):
        return
    copy_template("Dockerfile", target)
    click.secho("Make sure to update the Dockerfile", fg="yellow")


@init_group.command("auth")
@click.option(
    "-o", "--output", type=click.Path(), help="Custom output path for the auth handler"
)
@click.option("-f", "--force", is_flag=True, help="Force overwrite the auth handler")
def init_auth(output, force):
    """Add auth.py with auth handler. Everything you need to start using the auth service."""
    root = get_git_root()
    if output and Path(output).is_file():
        click.secho("Output path is a file, please provide a directory path", fg="red")
        return
    target = (Path(output) if output else root) / "auth.py"
    if not check_file_exists(target, force):
        return
    copy_template("auth.py", target)
    click.secho(
        """
    Make sure to update the .env and .env.example files with:
        IS_DOCKER=0
        API_ENV=local
    and the docker-compose.yml file with:
        environment:
            - IS_DOCKER=1
    and the .github/workflows/main.yaml file with:
        env:
            API_ENV: ${{ github.ref == 'refs/heads/main' && 'prod' || 'dev' }}
    """,
        fg="yellow",
    )


@init_group.command("dependabot")
@click.option("-f", "--force", is_flag=True, help="Force overwrite the dependabot.yml")
def init_dependabot(force):
    """Add dependabot.yml"""
    root = get_git_root()
    target = root / ".github/dependabot.yml"
    if not check_file_exists(target, force):
        return
    copy_template("dependabot.yml", target)


@init_group.command("merge-env")
@click.option("-f", "--force", is_flag=True, help="Force overwrite the .env file")
def init_merge_env(force):
    """Add script to merge environment and file variables into .env"""
    root = get_git_root()
    target = root / "scripts/merge-env.sh"
    if not check_file_exists(target, force):
        return
    copy_template("merge-env.sh", target)
