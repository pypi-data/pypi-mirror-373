#!/usr/bin/env python3
"""
Auto-updater for maxs - checks PyPI for newer versions and offers to upgrade.
"""

import json
import urllib.request
import urllib.error
import subprocess
import sys
from packaging import version
import importlib.metadata


def get_current_version():
    """Get the currently installed version of maxs."""
    try:
        return importlib.metadata.version("maxs")
    except importlib.metadata.PackageNotFoundError:
        return "0.0.0"  # Unknown version


def get_latest_pypi_version():
    """Get the latest version of maxs from PyPI."""
    try:
        url = "https://pypi.org/pypi/maxs/json"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            return data["info"]["version"]
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        json.JSONDecodeError,
        KeyError,
    ):
        return None


def is_newer_version(current, latest):
    """Check if latest version is newer than current version."""
    try:
        return version.parse(latest) > version.parse(current)
    except Exception:
        return False


def get_update_command():
    """Determine the appropriate update command (pipx or pip)."""
    # Check if pipx is available and maxs was installed with pipx
    try:
        result = subprocess.run(["pipx", "list"], capture_output=True, text=True)
        if result.returncode == 0 and "maxs" in result.stdout:
            return ["pipx", "upgrade", "maxs"]
    except FileNotFoundError:
        pass

    # Fallback to pip
    return [sys.executable, "-m", "pip", "install", "--upgrade", "maxs"]


def prompt_user(current_version, latest_version):
    """Prompt user if they want to upgrade."""
    print(f"\n🚀 **UPDATE AVAILABLE!**")
    print(f"   Current version: {current_version}")
    print(f"   Latest version:  {latest_version}")
    print(f"   Release: https://pypi.org/project/maxs/{latest_version}/")

    try:
        response = input("\n💡 Would you like to update now? [y/N]: ").strip().lower()
        return response in ["y", "yes"]
    except (KeyboardInterrupt, EOFError):
        print("\n")
        return False


def perform_update():
    """Perform the actual update."""
    update_cmd = get_update_command()
    cmd_str = " ".join(update_cmd)

    print(f"\n⏳ Updating maxs...")
    print(f"   Running: {cmd_str}")

    try:
        result = subprocess.run(update_cmd, check=True, capture_output=True, text=True)
        print(f"\n✅ **UPDATE SUCCESSFUL!**")
        print(f"   {result.stdout.strip()}")
        print(f"\n🎉 maxs has been updated! Please restart to use the new version.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ **UPDATE FAILED!**")
        print(f"   Error: {e}")
        if e.stderr:
            print(f"   Details: {e.stderr.strip()}")
        return False
    except Exception as e:
        print(f"\n❌ **UPDATE FAILED!**")
        print(f"   Unexpected error: {e}")
        return False


def check_for_updates(silent=False):
    """
    Check for updates and optionally upgrade.

    Args:
        silent: If True, only check but don't prompt user

    Returns:
        dict: Status information about the update check
    """
    current = get_current_version()
    latest = get_latest_pypi_version()

    result = {
        "current_version": current,
        "latest_version": latest,
        "update_available": False,
        "update_performed": False,
        "error": None,
    }

    if latest is None:
        if not silent:
            print("⚠️  Could not check for updates (network error or PyPI unavailable)")
        result["error"] = "network_error"
        return result

    if is_newer_version(current, latest):
        result["update_available"] = True

        if not silent:
            if prompt_user(current, latest):
                result["update_performed"] = perform_update()
            else:
                print(
                    "\n💡 Update skipped. You can update later with: pipx upgrade maxs"
                )
    else:
        if not silent:
            print(f"✅ maxs is up to date! (v{current})")

    return result


def main():
    """CLI entry point for the updater."""
    import argparse

    parser = argparse.ArgumentParser(description="Check for maxs updates")
    parser.add_argument(
        "--silent", action="store_true", help="Check silently without prompts"
    )
    parser.add_argument(
        "--check-only", action="store_true", help="Only check, do not prompt to update"
    )

    args = parser.parse_args()

    result = check_for_updates(silent=args.silent or args.check_only)

    if args.check_only:
        if result["update_available"]:
            print(
                f"UPDATE_AVAILABLE:{result['current_version']}->{result['latest_version']}"
            )
            sys.exit(1)  # Exit code 1 indicates update available
        else:
            print(f"UP_TO_DATE:{result['current_version']}")
            sys.exit(0)  # Exit code 0 indicates up to date


if __name__ == "__main__":
    main()
