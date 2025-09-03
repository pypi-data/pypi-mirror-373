#!/usr/bin/env python3
"""
Development tools and utilities for txttoqti package.

Provides commands for common development tasks like testing,
linting, formatting, and building.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def run_command(cmd: List[str], cwd: Optional[Path] = None) -> int:
    """
    Run a command and return its exit code.
    
    Args:
        cmd: Command and arguments to run
        cwd: Working directory for command
        
    Returns:
        Exit code from command
    """
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, cwd=cwd)
        return result.returncode
    except FileNotFoundError:
        print(f"Command not found: {cmd[0]}")
        return 1


def test(coverage: bool = True) -> int:
    """Run tests with optional coverage."""
    cmd = ["python", "-m", "pytest"]
    if coverage:
        cmd.extend(["--cov=src/txttoqti", "--cov-report=term-missing"])
    return run_command(cmd)


def lint() -> int:
    """Run linting tools."""
    commands = [
        ["python", "-m", "flake8", "src", "tests"],
        ["python", "-m", "mypy", "src"],
    ]
    
    for cmd in commands:
        exit_code = run_command(cmd)
        if exit_code != 0:
            return exit_code
    return 0


def format_code() -> int:
    """Format code with black."""
    return run_command(["python", "-m", "black", "src", "tests", "scripts"])


def clean() -> int:
    """Clean build artifacts and cache files."""
    import shutil
    
    patterns = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        ".pytest_cache",
        ".mypy_cache",
        "htmlcov",
        ".coverage",
        "dist",
        "build",
        "*.egg-info",
    ]
    
    root = Path(".")
    for pattern in patterns:
        if "*" in pattern:
            for path in root.rglob(pattern):
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    shutil.rmtree(path)
        else:
            for path in root.rglob(pattern):
                if path.is_dir():
                    shutil.rmtree(path)
                    print(f"Removed: {path}")
    
    print("Clean complete")
    return 0


def build() -> int:
    """Build the package."""
    return run_command(["python", "-m", "build"])


def install_dev() -> int:
    """Install package in development mode."""
    return run_command(["pip", "install", "-e", ".[dev]"])


def main() -> None:
    """Main entry point for development tools."""
    parser = argparse.ArgumentParser(description="Development tools for txttoqti")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("--no-cov", action="store_true", help="Disable coverage")
    
    # Lint command
    subparsers.add_parser("lint", help="Run linting tools")
    
    # Format command
    subparsers.add_parser("format", help="Format code with black")
    
    # Clean command
    subparsers.add_parser("clean", help="Clean build artifacts")
    
    # Build command
    subparsers.add_parser("build", help="Build package")
    
    # Install command
    subparsers.add_parser("install-dev", help="Install in development mode")
    
    args = parser.parse_args()
    
    if args.command == "test":
        exit_code = test(coverage=not args.no_cov)
    elif args.command == "lint":
        exit_code = lint()
    elif args.command == "format":
        exit_code = format_code()
    elif args.command == "clean":
        exit_code = clean()
    elif args.command == "build":
        exit_code = build()
    elif args.command == "install-dev":
        exit_code = install_dev()
    else:
        parser.print_help()
        exit_code = 1
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()