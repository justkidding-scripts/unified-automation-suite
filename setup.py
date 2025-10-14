#!/usr/bin/env python3
"""
Unified Automation Suite - Setup Script
=======================================
Automated setup for the Telegram & SMS automation platform.
Handles virtual environment creation, dependency installation, and environment configuration.

Author: Enhanced by AI Assistant
Version: 3.1.0
"""

import sys
import os
import subprocess
import platform
import shutil
from pathlib import Path


class SetupManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent.absolute()
        self.venv_dir = self.base_dir / "venv"
        self.system_python = self.find_system_python()
        self.os_type = platform.system().lower()
        
    def find_system_python(self):
        """Find the system Python that supports tkinter"""
        python_candidates = [
            "/usr/bin/python3",
            "/usr/bin/python3.13",
            "/usr/bin/python3.12", 
            "/usr/bin/python3.11",
            "/usr/bin/python3.10",
            "/usr/bin/python",
            shutil.which("python3"),
            shutil.which("python")
        ]
        
        for python_path in python_candidates:
            if python_path and Path(python_path).exists():
                try:
                    # Test if this Python has tkinter
                    result = subprocess.run([
                        python_path, "-c", "import tkinter; print('OK')"
                    ], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        print(f"✅ Found system Python with tkinter: {python_path}")
                        return python_path
                except:
                    continue
        
        print("❌ No Python installation with tkinter found")
        return sys.executable
    
    def install_system_dependencies(self):
        """Install system-level dependencies"""
        print("🔧 Installing system dependencies...")
        
        if self.os_type == "linux":
            try:
                # Check if we can install packages
                subprocess.run(["which", "apt-get"], check=True, capture_output=True)
                print("📦 Installing tkinter and dev tools...")
                subprocess.run([
                    "sudo", "apt-get", "update"
                ], check=False)
                subprocess.run([
                    "sudo", "apt-get", "install", "-y", 
                    "python3-tk", "python3-dev", "python3-venv", 
                    "python3-full", "build-essential"
                ], check=False)
                print("✅ System dependencies installed")
            except subprocess.CalledProcessError:
                print("⚠️ Could not install system packages (running without sudo?)")
                print("   Please install manually: sudo apt-get install python3-tk python3-dev python3-venv")
    
    def create_virtual_environment(self):
        """Create virtual environment with system site packages"""
        print(f"🏗️ Creating virtual environment with {self.system_python}...")
        
        # Remove existing venv if it exists
        if self.venv_dir.exists():
            print("🗑️ Removing existing virtual environment...")
            shutil.rmtree(self.venv_dir)
        
        # Create new venv with system site packages (for tkinter access)
        try:
            subprocess.run([
                self.system_python, "-m", "venv", str(self.venv_dir),
                "--system-site-packages"
            ], check=True)
            print("✅ Virtual environment created successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    
    def get_venv_python(self):
        """Get the Python executable from the virtual environment"""
        if os.name == 'nt':  # Windows
            return self.venv_dir / "Scripts" / "python.exe"
        else:  # Unix-like
            return self.venv_dir / "bin" / "python"
    
    def install_dependencies(self):
        """Install Python dependencies in virtual environment"""
        print("📦 Installing Python dependencies...")
        
        venv_python = self.get_venv_python()
        if not venv_python.exists():
            print(f"❌ Virtual environment Python not found: {venv_python}")
            return False
        
        try:
            # First upgrade pip
            subprocess.run([
                str(venv_python), "-m", "pip", "install", "--upgrade", "pip"
            ], check=True)
            
            # Install from clean requirements
            requirements_file = self.base_dir / "requirements_clean.txt"
            if not requirements_file.exists():
                print("❌ Clean requirements file not found")
                return False
            
            subprocess.run([
                str(venv_python), "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True)
            
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def test_installation(self):
        """Test if the installation is working"""
        print("🧪 Testing installation...")
        
        venv_python = self.get_venv_python()
        test_imports = [
            "tkinter",
            "telethon",
            "aiohttp", 
            "selenium",
            "requests",
            "pandas",
            "sqlalchemy"
        ]
        
        failed_imports = []
        for module in test_imports:
            try:
                result = subprocess.run([
                    str(venv_python), "-c", f"import {module}; print(f'{module}: OK')"
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    print(f"  ✅ {module}")
                else:
                    print(f"  ❌ {module}: {result.stderr.strip()}")
                    failed_imports.append(module)
            except subprocess.TimeoutExpired:
                print(f"  ⏰ {module}: Import timeout")
                failed_imports.append(module)
            except Exception as e:
                print(f"  ❌ {module}: {e}")
                failed_imports.append(module)
        
        if failed_imports:
            print(f"⚠️ Some imports failed: {', '.join(failed_imports)}")
            return False
        else:
            print("✅ All imports successful")
            return True
    
    def create_activation_scripts(self):
        """Create easy activation scripts"""
        print("📜 Creating activation scripts...")
        
        # Create activation script for Unix-like systems
        if self.os_type in ['linux', 'darwin']:
            activate_script = self.base_dir / "activate.sh"
            with open(activate_script, 'w') as f:
                f.write(f"""#!/bin/bash
# Unified Automation Suite - Environment Activation
echo "🚀 Activating Unified Automation Suite Environment..."
source "{self.venv_dir}/bin/activate"
export PYTHONPATH="$PYTHONPATH:{self.base_dir}"
echo "✅ Environment activated. You can now run:"
echo "   python main.py --gui    # Launch full GUI"
echo "   python main.py --test   # Run tests"
echo "   python main.py --info   # Show information"
""")
            activate_script.chmod(0o755)
            print(f"✅ Created activation script: {activate_script}")
        
        # Create launcher script
        launcher_script = self.base_dir / "launch.py"
        with open(launcher_script, 'w') as f:
            f.write(f'''#!/usr/bin/env python3
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
''')
        launcher_script.chmod(0o755)
        print(f"✅ Created launcher script: {launcher_script}")
    
    def setup_configuration(self):
        """Setup initial configuration"""
        print("⚙️ Setting up configuration...")
        
        # Create necessary directories
        directories = ['.config', 'logs', 'sessions', 'exports', 'data']
        for directory in directories:
            dir_path = self.base_dir / directory
            dir_path.mkdir(exist_ok=True)
            print(f"📁 Created directory: {directory}")
        
        # Create sample configuration
        config_file = self.base_dir / 'config.ini'
        if not config_file.exists():
            sample_config = """[telegram_accounts]
# Add your Telegram accounts here
# account_1_api_id = YOUR_API_ID
# account_1_api_hash = YOUR_API_HASH  
# account_1_phone = +1234567890
# account_1_session_name = session1

[sms_providers]
# Add your SMS provider configurations
# provider_1_name = SMS-Activate
# provider_1_api_key = YOUR_API_KEY

[integration]
auto_workflows = true
cross_tool_sharing = true
theme = dark_professional
log_level = INFO

[advanced]
max_concurrent_operations = 5
database_timeout = 30
proxy_rotation_enabled = true
anti_detection_enabled = true

[gui_settings]
window_size = 1200x800
theme = dark
auto_save = true
show_advanced_options = false
"""
            config_file.write_text(sample_config)
            print(f"✅ Created configuration file: {config_file}")
    
    def run_setup(self):
        """Run the complete setup process"""
        print("🚀 Unified Automation Suite - Setup Process")
        print("=" * 50)
        
        # Step 1: Install system dependencies
        self.install_system_dependencies()
        
        # Step 2: Create virtual environment  
        if not self.create_virtual_environment():
            print("❌ Setup failed at virtual environment creation")
            return False
        
        # Step 3: Install dependencies
        if not self.install_dependencies():
            print("❌ Setup failed at dependency installation")
            return False
        
        # Step 4: Test installation
        if not self.test_installation():
            print("⚠️ Setup completed but some components may not work properly")
        
        # Step 5: Create activation scripts
        self.create_activation_scripts()
        
        # Step 6: Setup configuration
        self.setup_configuration()
        
        print("\n🎉 Setup completed successfully!")
        print("=" * 50)
        print("Next steps:")
        print("1. Configure your accounts in config.ini")
        print("2. Run the application:")
        if self.os_type in ['linux', 'darwin']:
            print("   ./activate.sh && python main.py --gui")
        print("   python launch.py --gui")
        print("3. Or run tests first:")
        print("   python launch.py --test")
        
        return True


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("""
Unified Automation Suite - Setup Script

Usage: python setup.py

This script will:
1. Install system dependencies (tkinter, dev tools)
2. Create a virtual environment with system site packages
3. Install Python dependencies
4. Test the installation
5. Create activation and launcher scripts
6. Setup initial configuration

No arguments required - just run it!
""")
        return

    setup_manager = SetupManager()
    success = setup_manager.run_setup()
    
    if success:
        sys.exit(0)
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    main()