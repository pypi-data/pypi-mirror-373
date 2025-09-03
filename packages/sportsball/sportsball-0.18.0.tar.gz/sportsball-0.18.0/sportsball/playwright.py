"""Utility for providing and installing playwright."""

# pylint: disable=subprocess-run-check,global-statement
import subprocess

from playwright._impl._driver import compute_driver_executable, get_driver_env

_INSTALLED = False


def ensure_install():
    """Provides a playwright instance guaranteeing an install."""
    global _INSTALLED
    if not _INSTALLED:
        driver_executable, driver_cli = compute_driver_executable()
        completed_process = subprocess.run(
            [driver_executable, driver_cli, "install"], env=get_driver_env()
        )
        assert completed_process.returncode == 0
        _INSTALLED = True
