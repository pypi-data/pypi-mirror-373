import subprocess
import sys
import re
from typing import List, Optional, Tuple, Dict
from enum import Enum

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from concurrent.futures import ThreadPoolExecutor, as_completed

from .utils import get_outdated_packages, generate_packages_table


# --- Status enums for clear results ---
class UpgradeStatus(Enum):
    SUCCESS = "SUCCESS"
    UPGRADE_FAILED = "UPGRADE_FAILED"
    ROLLBACK_SUCCESS = "ROLLBACK_SUCCESS"
    ROLLBACK_FAILED = "ROLLBACK_FAILED"


console = Console()
app = typer.Typer(
    name="py-upgrade",
    help="An intelligent, feature-rich CLI tool to manage and upgrade Python packages.",
    add_completion=False,
)


def check_for_conflicts(packages_to_check: List[str]) -> Optional[str]:
    # This function remains unchanged from the previous version
    console.print(
        "\n[bold cyan]Checking for potential dependency conflicts...[/bold cyan]"
    )
    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--dry-run",
        "--upgrade",
    ] + packages_to_check
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    _, stderr = process.communicate()
    conflict_match = re.search(
        r"ERROR: pip's dependency resolver does not currently take into account all the packages that are installed\. This behaviour is the source of the following dependency conflicts\.(.+)",
        stderr,
        re.DOTALL,
    )
    if conflict_match:
        return conflict_match.group(1).strip()
    return None


def upgrade_package(
    pkg: Dict, no_rollback: bool
) -> Tuple[str, str, UpgradeStatus, str, str]:
    """
    Worker function to upgrade a single package, with rollback on failure.

    Returns:
        A tuple of (package_name, new_version, status_enum, original_version, error_message).
    """
    pkg_name = pkg["name"]
    original_version = pkg["version"]
    latest_version = pkg["latest_version"]
    error_message = ""

    try:
        # Use subprocess.run to capture output and check for errors
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", f"{pkg_name}"],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )
        return pkg_name, latest_version, UpgradeStatus.SUCCESS, original_version, ""
    except subprocess.CalledProcessError as e:
        # The upgrade failed. Capture the precise error from stderr.
        error_message = e.stderr.strip()
        if no_rollback:
            return (
                pkg_name,
                latest_version,
                UpgradeStatus.UPGRADE_FAILED,
                original_version,
                error_message,
            )

        # Attempt to roll back to the original version.
        try:
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--force-reinstall",
                    f"{pkg_name}=={original_version}",
                ],
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
            )
            return (
                pkg_name,
                latest_version,
                UpgradeStatus.ROLLBACK_SUCCESS,
                original_version,
                error_message,
            )
        except subprocess.CalledProcessError as rollback_e:
            # The rollback itself failed, which is critical.
            critical_error = f"Upgrade Error: {error_message}\nRollback Error: {rollback_e.stderr.strip()}"
            return (
                pkg_name,
                latest_version,
                UpgradeStatus.ROLLBACK_FAILED,
                original_version,
                critical_error,
            )


@app.command()
def upgrade(
    packages_to_upgrade: Optional[List[str]] = typer.Argument(
        None, help="Specific packages to upgrade."
    ),
    exclude: Optional[List[str]] = typer.Option(
        None, "--exclude", "-e", help="List of packages to exclude."
    ),
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Automatically confirm all prompts."
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Simulate the upgrade without making changes."
    ),
    workers: int = typer.Option(
        10, "--workers", "-w", help="Number of concurrent workers."
    ),
    no_rollback: bool = typer.Option(
        False, "--no-rollback", help="Disable automatic rollback on failure."
    ),
):
    """
    Checks for and concurrently upgrades outdated Python packages with dependency analysis and rollback-on-failure.
    """
    outdated_packages = get_outdated_packages()
    if not outdated_packages:
        console.print("[bold green]✨ All packages are up to date! ✨[/bold green]")
        raise typer.Exit()

    if packages_to_upgrade:
        name_to_pkg = {pkg["name"].lower(): pkg for pkg in outdated_packages}
        target_packages = [
            name_to_pkg[name.lower()]
            for name in packages_to_upgrade
            if name.lower() in name_to_pkg
        ]
    else:
        target_packages = outdated_packages

    if exclude:
        exclude_set = {name.lower() for name in exclude}
        target_packages = [
            pkg for pkg in target_packages if pkg["name"].lower() not in exclude_set
        ]

    if not target_packages:
        console.print(
            "[bold yellow]No packages match the specified criteria for upgrade.[/bold yellow]"
        )
        raise typer.Exit()

    table = generate_packages_table(target_packages, title="Outdated Python Packages")
    console.print(table)

    if dry_run:
        console.print(
            f"\n[bold yellow]--dry-run enabled. Would simulate upgrade of {len(target_packages)} packages.[/bold yellow]"
        )
        raise typer.Exit()

    package_names = [pkg["name"] for pkg in target_packages]
    conflicts = check_for_conflicts(package_names)
    if conflicts:
        console.print(
            Panel.fit(
                f"[bold]The following dependency conflicts were found:[/bold]\n\n{conflicts}",
                title="[bold yellow]⚠️  Dependency Warning[/bold yellow]",
                border_style="yellow",
                padding=(1, 2),
            )
        )
    else:
        console.print("[bold green]✅ No dependency conflicts detected.[/bold green]")

    if not yes:
        prompt_message = "\nProceed with the upgrade?"
        if conflicts:
            prompt_message = "\nConflicts were detected. Do you still wish to proceed?"
        try:
            confirmed = typer.confirm(prompt_message)
            if not confirmed:
                console.print("Upgrade cancelled by user.")
                raise typer.Exit()
        except typer.Abort:
            console.print("\nUpgrade cancelled by user.")
            raise typer.Exit()

    console.print(
        f"\n[bold blue]Starting parallel upgrade with {workers} workers...[/bold blue]"
    )
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    )

    results = {
        UpgradeStatus.SUCCESS: 0,
        UpgradeStatus.UPGRADE_FAILED: 0,
        UpgradeStatus.ROLLBACK_SUCCESS: 0,
        UpgradeStatus.ROLLBACK_FAILED: 0,
    }
    failed_rollbacks = []
    failed_upgrades_no_rollback = []

    with progress:
        upgrade_task = progress.add_task(
            "[green]Upgrading...", total=len(target_packages)
        )
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_pkg = {
                executor.submit(upgrade_package, pkg, no_rollback): pkg
                for pkg in target_packages
            }
            for future in as_completed(future_to_pkg):
                pkg_name, latest_version, status, original_version, error_msg = (
                    future.result()
                )
                results[status] += 1

                if status == UpgradeStatus.SUCCESS:
                    progress.console.print(
                        f"  ✅ [green]Successfully upgraded {pkg_name} to {latest_version}[/green]"
                    )
                elif status == UpgradeStatus.ROLLBACK_SUCCESS:
                    progress.console.print(
                        f"  ↪️ [yellow]Failed to upgrade {pkg_name}, but successfully rolled back to {original_version}[/yellow]"
                    )
                elif status == UpgradeStatus.UPGRADE_FAILED:
                    progress.console.print(
                        f"  ❌ [red]Failed to upgrade {pkg_name}. Rollback was disabled.[/red]"
                    )
                    failed_upgrades_no_rollback.append((pkg_name, error_msg))
                elif status == UpgradeStatus.ROLLBACK_FAILED:
                    progress.console.print(
                        f"  🚨 [bold red]CRITICAL: Failed to upgrade {pkg_name} AND failed to roll back to {original_version}. Your environment may be unstable.[/bold red]"
                    )
                    failed_rollbacks.append((pkg_name, error_msg))

                progress.advance(upgrade_task)

    console.print("\n--- [bold]Upgrade Complete[/bold] ---")
    console.print(
        f"[green]Successful upgrades:[/green] {results[UpgradeStatus.SUCCESS]}"
    )
    if results[UpgradeStatus.ROLLBACK_SUCCESS] > 0:
        console.print(
            f"[yellow]Failed upgrades (rolled back):[/yellow] {results[UpgradeStatus.ROLLBACK_SUCCESS]}"
        )
    if results[UpgradeStatus.UPGRADE_FAILED] > 0:
        console.print(
            f"[red]Failed upgrades (no rollback):[/red] {results[UpgradeStatus.UPGRADE_FAILED]}"
        )
        for pkg_name, error in failed_upgrades_no_rollback:
            console.print(
                f"  - [bold]{pkg_name}[/bold]: {error.splitlines()[0]}"
            )  # Show first line of error
    if results[UpgradeStatus.ROLLBACK_FAILED] > 0:
        console.print(
            f"[bold red]CRITICAL-FAILURE (unstable):[/bold red] {results[UpgradeStatus.ROLLBACK_FAILED]}"
        )
        for pkg_name, error in failed_rollbacks:
            console.print(
                Panel(
                    f"[bold]{pkg_name}[/bold]\n---\n{error}",
                    title="[bold red]Detailed Error[/bold red]",
                    border_style="red",
                )
            )
    console.print("--------------------------")


if __name__ == "__main__":
    app()
