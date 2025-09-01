import subprocess
import sys
import json
from typing import List

from rich.table import Table
from rich.console import Console

console = Console()


def get_outdated_packages() -> List[dict]:
    """
    Retrieves a list of outdated packages using pip's JSON output format.
    Handles both single JSON array and line-delimited JSON outputs for compatibility.

    Returns:
        A list of dictionaries, where each dictionary represents an outdated package.

    Raises:
        SystemExit: If pip command fails or is not found.
    """
    try:
        command = [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"]
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            console.print(f"[bold red]Error running pip:[/bold red]\n{stderr}")
            raise SystemExit(1)

        output = stdout.strip()
        if not output:
            return []

        # First, try to parse the entire output as a single JSON array.
        # This is the modern format for pip.
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            # If that fails, fall back to parsing line-by-line.
            # This handles older pip versions or unexpected formats.
            return [json.loads(line) for line in output.split("\n")]

    except FileNotFoundError:
        console.print(
            "[bold red]Fatal Error:[/bold red] `pip` is not installed or not in your PATH."
        )
        raise SystemExit(1)
    except Exception as e:
        console.print(
            f"[bold red]An unexpected error occurred while parsing pip output:[/bold red] {e}"
        )
        raise SystemExit(1)


def generate_packages_table(packages: List[dict], title: str) -> Table:
    """
    Generates a Rich Table to display package information.

    Args:
        packages: A list of package dictionaries.
        title: The title for the table.

    Returns:
        A Rich Table object ready for printing.
    """
    table = Table(
        title=title,
        caption=f"{len(packages)} packages selected",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Package Name", style="cyan", no_wrap=True)
    table.add_column("Current Version", style="yellow")
    table.add_column("Latest Version", style="green")

    for pkg in packages:
        # Using .get() provides safety against missing keys, returning None instead of erroring.
        table.add_row(pkg.get("name"), pkg.get("version"), pkg.get("latest_version"))
    return table
