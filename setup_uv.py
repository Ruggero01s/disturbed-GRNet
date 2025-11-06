"""
Setup script for GRNet project with UV package manager
Run this script to set up the project environment
"""
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(e.stderr)
        return False

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║        GRNet Project Setup with UV Package Manager        ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Check if UV is installed
    print("\n🔍 Checking if UV is installed...")
    try:
        result = subprocess.run("uv --version", shell=True, capture_output=True, text=True)
        print(f"✅ UV is installed: {result.stdout.strip()}")
    except:
        print("❌ UV is not installed!")
        print("\nPlease install UV first:")
        print("  PowerShell: powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\"")
        sys.exit(1)
    
    # Create virtual environment
    if not run_command("uv venv --python 3.9", "Creating virtual environment with Python 3.9"):
        print("\n⚠️  Virtual environment creation failed, but continuing...")
    
    # Sync dependencies
    if not run_command("uv sync", "Installing project dependencies"):
        print("\n⚠️  Some dependencies might have failed to install")
        print("You may need to install them manually")
    
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                    Setup Complete! ✅                      ║
    ╚═══════════════════════════════════════════════════════════╝
    
    Next steps:
    
    1. Activate the virtual environment:
       Windows PowerShell: .venv\\Scripts\\activate
       Windows CMD:        .venv\\Scripts\\activate.bat
    
    2. Start Jupyter Lab:
       uv run jupyter lab
    
    3. Open the notebook:
       code/GRNet_approach.ipynb
    
    For more information, see UV_SETUP.md
    """)

if __name__ == "__main__":
    main()
