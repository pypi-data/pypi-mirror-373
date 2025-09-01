import sys
import subprocess
from unittest.mock import patch

from typer.testing import CliRunner
from upgrade_tool.main import app, upgrade_package, UpgradeStatus

# CliRunner is a utility from Typer for testing command-line applications
runner = CliRunner()


def test_app_shows_up_to_date_message(monkeypatch):
    """
    Tests that the correct message is shown when no packages are outdated.
    """
    monkeypatch.setattr("upgrade_tool.main.get_outdated_packages", lambda: [])
    result = runner.invoke(app)
    assert result.exit_code == 0
    assert "All packages are up to date!" in result.stdout


def test_app_exclusion_logic(monkeypatch):
    """
    Tests the --exclude functionality.
    """
    mock_outdated = [
        {"name": "requests", "version": "2.25.0", "latest_version": "2.28.0"},
        {"name": "numpy", "version": "1.20.0", "latest_version": "1.23.0"},
    ]
    monkeypatch.setattr(
        "upgrade_tool.main.get_outdated_packages", lambda: mock_outdated
    )
    result = runner.invoke(app, ["--exclude", "requests", "--dry-run"])
    assert result.exit_code == 0
    assert "requests" not in result.stdout
    assert "numpy" in result.stdout
    assert "1 packages selected" in result.stdout


# --- NEW: Comprehensive tests for the upgrade_package worker function ---


@patch("upgrade_tool.main.subprocess.run")
def test_upgrade_package_success(mock_run):
    """Tests the successful upgrade path of the worker function."""
    mock_run.return_value = subprocess.CompletedProcess(
        args=[], returncode=0, stdout="", stderr=""
    )
    pkg = {"name": "requests", "version": "2.25.0", "latest_version": "2.28.0"}

    name, _, status, _, error = upgrade_package(pkg, no_rollback=False)

    assert status == UpgradeStatus.SUCCESS
    assert name == "requests"
    assert error == ""
    # Assert that pip install --upgrade was called
    mock_run.assert_called_once_with(
        [sys.executable, "-m", "pip", "install", "--upgrade", "requests"],
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",
    )


@patch("upgrade_tool.main.subprocess.run")
def test_upgrade_failure_with_successful_rollback(mock_run):
    """Tests that a failed upgrade triggers a successful rollback."""
    # Simulate a failure on the first call (upgrade) and success on the second (rollback)
    mock_run.side_effect = [
        subprocess.CalledProcessError(returncode=1, cmd=[], stderr="Upgrade failed!"),
        subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        ),  # This is the rollback call
    ]
    pkg = {"name": "requests", "version": "2.25.0", "latest_version": "2.28.0"}

    _, _, status, _, error = upgrade_package(pkg, no_rollback=False)

    assert status == UpgradeStatus.ROLLBACK_SUCCESS
    assert "Upgrade failed!" in error
    assert mock_run.call_count == 2
    # Check the second call was the rollback
    rollback_call_args = mock_run.call_args_list[1].args[0]
    assert "--force-reinstall" in rollback_call_args
    assert "requests==2.25.0" in rollback_call_args


@patch("upgrade_tool.main.subprocess.run")
def test_upgrade_failure_with_failed_rollback(mock_run):
    """Tests a critical failure where both upgrade and rollback fail."""
    # Simulate failure on both calls
    mock_run.side_effect = [
        subprocess.CalledProcessError(returncode=1, cmd=[], stderr="Upgrade failed!"),
        subprocess.CalledProcessError(
            returncode=1, cmd=[], stderr="Rollback also failed!"
        ),
    ]
    pkg = {"name": "requests", "version": "2.25.0", "latest_version": "2.28.0"}

    _, _, status, _, error = upgrade_package(pkg, no_rollback=False)

    assert status == UpgradeStatus.ROLLBACK_FAILED
    assert "Upgrade Error: Upgrade failed!" in error
    assert "Rollback Error: Rollback also failed!" in error
    assert mock_run.call_count == 2


@patch("upgrade_tool.main.subprocess.run")
def test_upgrade_failure_with_no_rollback_enabled(mock_run):
    """Tests that a failed upgrade does not attempt rollback when disabled."""
    # Simulate failure on the first call
    mock_run.side_effect = subprocess.CalledProcessError(
        returncode=1, cmd=[], stderr="Upgrade failed!"
    )
    pkg = {"name": "requests", "version": "2.25.0", "latest_version": "2.28.0"}

    _, _, status, _, error = upgrade_package(pkg, no_rollback=True)

    assert status == UpgradeStatus.UPGRADE_FAILED
    assert "Upgrade failed!" in error
    # With no_rollback=True, only one call to subprocess.run should be made
    mock_run.assert_called_once()
