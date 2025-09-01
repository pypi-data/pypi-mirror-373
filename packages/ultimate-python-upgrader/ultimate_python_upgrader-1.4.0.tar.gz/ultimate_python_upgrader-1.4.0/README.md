# Ultimate Python Upgrader (`py-upgrade`)

[![PyPI version](https://badge.fury.io/py/ultimate-python-upgrader.svg)](https://badge.fury.io/py/ultimate-python-upgrader)
[![CI](https://github.com/psywarrior1998/upgrade_all_python/actions/workflows/ci.yml/badge.svg)](https://github.com/psywarrior1998/upgrade_all_python/actions/workflows/ci.yml)

An intelligent, feature-rich CLI tool to manage and upgrade Python packages with a clean, modern interface and a powerful dependency safety-net.



## Key Features

-   **🛡️ Rollback on Failure**: If an upgrade fails for any reason, the tool automatically reverts the package to its previous stable version. This ensures your environment is never left in a broken state.
-   **Intelligent Dependency Analysis**: Performs a pre-flight check to detect and warn you about potential dependency conflicts *before* you upgrade.
-   **Concurrent & Fast**: Upgrades packages in parallel using multiple workers, dramatically reducing the time you spend waiting.
-   **Rich & Interactive UI**: Uses `rich` to display outdated packages in a clean, readable table with clear progress bars.
-   **Selective Upgrades**: Upgrade all packages, or specify exactly which ones to include or exclude.
-   **Safety First**: Includes a `--dry-run` mode to see what would be upgraded without making any changes.
-   **Automation Friendly**: A `--yes` flag allows for use in automated scripts.

## Installation

The tool is available on PyPI. Install it with pip:

```bash
pip install ultimate-python-upgrader
````

## Usage

Once installed, the `py-upgrade` command will be available.

**1. Check and upgrade all packages interactively**
The tool will check for conflicts and automatically roll back any failed upgrades.

```bash
py-upgrade
```

**2. Disable automatic rollback (not recommended)**

```bash
py-upgrade --yes --no-rollback
```

**3. Perform a dry run to see what needs upgrading**

```bash
py-upgrade --dry-run
```

## Contributing

Contributions are welcome\! Please feel free to submit a pull request.