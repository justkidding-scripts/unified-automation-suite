#!/usr/bin/env python3
"""Quick launcher for the Unified Automation Suite"""
import sys
import subprocess
from pathlib import Path

venv_python = Path(__file__).parent / "venv" / "bin" / "python"
if not venv_python.exists():
    venv_python = Path(__file__).parent / "venv" / "Scripts" / "python.exe"

if venv_python.exists():
    subprocess.run([str(venv_python), str(Path(__file__).parent / "main.py")] + sys.argv[1:])
else:
    print("❌ Virtual environment not found. Please run setup.py first.")
    sys.exit(1)
