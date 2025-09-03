#!/usr/bin/env python3
"""Setup script for SlipperPy development."""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: str) -> bool:
    """Run a shell command and return success status."""
    print(f"Running: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        return False


def main():
    """Main setup function."""
    print("Setting up SlipperPy development environment...")
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Not in a virtual environment!")
        print("It's recommended to use a virtual environment.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return
    
    # Install the package in development mode
    print("\n1. Installing package in development mode...")
    if not run_command("pip install -e ."):
        print("❌ Failed to install package")
        return
    
    # Install development dependencies
    print("\n2. Installing development dependencies...")
    if not run_command("pip install -r requirements-dev.txt"):
        print("❌ Failed to install development dependencies")
        return
    
    # Run tests to make sure everything works
    print("\n3. Running tests...")
    if Path("tests").exists():
        if not run_command("python -m pytest tests/ -v"):
            print("⚠️  Some tests failed, but setup completed")
        else:
            print("✅ All tests passed!")
    else:
        print("ℹ️  No tests directory found, skipping tests")
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Set your environment variables:")
    print("   export SLIPPER_ENDPOINT='https://api.slipper.no/graphql'")
    print("   export SLIPPER_PHONE='+47XXXXXXXX'")
    print("   # Note: SMS code will be requested interactively")
    print("2. Run the example: python examples/basic_usage.py")
    print("3. Start developing!")


if __name__ == "__main__":
    main()
