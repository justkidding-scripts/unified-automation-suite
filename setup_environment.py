#!/usr/bin/env python3
"""
Environment Setup Script
========================
Sets up the environment and dependencies for the Unified Automation Suite.

Author: Enhanced by AI Assistant
Version: 3.0.0
"""

import os
import sys
import subprocess
from pathlib import Path
import sqlite3
import json

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = [
        '.config',
        'logs', 
        'sessions',
        'exports',
        'databases',
        'temp',
        'backups'
    ]
    
    print("📁 Creating directories...")
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   • {directory}/")
    
    print("✅ Directories created")

def create_sample_config():
    """Create sample configuration file"""
    config_content = """# Unified Telegram & SMS Automation Suite Configuration
# =====================================================

[telegram_accounts]
# Add your Telegram accounts here
# Format: account_<number>_<field> = value
# 
# Example:
# account_1_api_id = 12345678
# account_1_api_hash = abcdef1234567890abcdef1234567890
# account_1_phone = +1234567890
# account_1_session_name = session1

[sms_providers]  
# Add your SMS provider configurations
#
# Example:
# provider_1_name = SMS-Activate
# provider_1_api_key = YOUR_API_KEY_HERE
# provider_1_service_id = telegram

[integration]
# Integration settings
auto_workflows = true
cross_tool_sharing = true
theme = dark_professional
log_level = INFO
enable_monitoring = true

[advanced]
# Advanced configuration
max_concurrent_operations = 5
database_timeout = 30
proxy_rotation_enabled = true
anti_detection_enabled = true
batch_size = 100
retry_attempts = 3

[security]
# Security settings
encrypt_sessions = false
secure_delete = true
audit_logging = true

[performance]
# Performance optimization
cache_size = 1000
connection_pool_size = 10
background_processing = true
"""
    
    config_file = Path("config.ini")
    if not config_file.exists():
        config_file.write_text(config_content)
        print("✅ Created sample config.ini")
    else:
        print("⚠️  config.ini already exists, skipping")

def initialize_databases():
    """Initialize SQLite databases"""
    print("🗄️ Initializing databases...")
    
    # Create main integration database
    db_path = "databases/unified_automation.db"
    os.makedirs("databases", exist_ok=True)
    
    try:
        conn = sqlite3.connect(db_path, timeout=30)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        
        # Create a simple test table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS setup_info (
                id INTEGER PRIMARY KEY,
                setup_date TEXT,
                version TEXT,
                status TEXT
            )
        """)
        
        # Insert setup record
        from datetime import datetime
        conn.execute("""
            INSERT INTO setup_info (setup_date, version, status)
            VALUES (?, ?, ?)
        """, (datetime.now().isoformat(), "3.0.0", "initialized"))
        
        conn.commit()
        conn.close()
        
        print("✅ Database initialized")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def create_launch_scripts():
    """Create convenient launch scripts"""
    print("🚀 Creating launch scripts...")
    
    # Unix/Linux launch script
    if os.name != 'nt':
        launch_script = """#!/bin/bash
# Unified Automation Suite Launcher
echo "🚀 Starting Unified Telegram & SMS Automation Suite..."
python3 main.py "$@"
"""
        script_path = Path("launch.sh")
        script_path.write_text(launch_script)
        script_path.chmod(0o755)
        print("   • launch.sh")
    
    # Windows launch script  
    if os.name == 'nt' or True:  # Create for all platforms
        launch_script = """@echo off
REM Unified Automation Suite Launcher
echo 🚀 Starting Unified Telegram ^& SMS Automation Suite...
python main.py %*
pause
"""
        script_path = Path("launch.bat")
        script_path.write_text(launch_script)
        print("   • launch.bat")
    
    print("✅ Launch scripts created")

def run_basic_tests():
    """Run basic functionality tests"""
    print("🧪 Running basic tests...")
    
    try:
        # Test imports
        print("   • Testing imports...")
        import sqlite3
        import json
        import asyncio
        print("     ✅ Core modules")
        
        try:
            import tkinter
            print("     ✅ GUI framework (tkinter)")
        except ImportError:
            print("     ⚠️  GUI framework not available")
        
        # Test database
        print("   • Testing database...")
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE TABLE test (id INTEGER)")
        conn.close()
        print("     ✅ SQLite functionality")
        
        print("✅ Basic tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Basic tests failed: {e}")
        return False

def show_completion_message():
    """Show setup completion message"""
    message = """
🎉 SETUP COMPLETE!
==================

The Unified Telegram & SMS Automation Suite is now ready to use.

📂 What was created:
   • Directory structure for logs, sessions, exports
   • Sample configuration file (config.ini)
   • Database initialization
   • Launch scripts (launch.sh / launch.bat)

🚀 Next Steps:
   1. Edit config.ini with your API credentials
   2. Install any missing dependencies: pip install -r requirements.txt
   3. Run tests: python main.py --test
   4. Launch the suite: python main.py

💡 Quick Launch:
   • Unified GUI: python main.py
   • Telegram only: python main.py --telegram  
   • Run tests: python main.py --test
   • Show help: python main.py --help

📚 Documentation: README.md
🔧 Logs will be in: unified_automation.log

Happy automating! 🚀
"""
    print(message)

def main():
    """Main setup function"""
    print("🔧 UNIFIED AUTOMATION SUITE - ENVIRONMENT SETUP")
    print("=" * 50)
    print("Setting up your automation environment...\n")
    
    success = True
    
    # Run setup steps
    create_directories()
    create_sample_config()
    
    if not initialize_databases():
        success = False
    
    create_launch_scripts()
    
    if not run_basic_tests():
        success = False
    
    print("\n" + "=" * 50)
    
    if success:
        show_completion_message()
    else:
        print("⚠️  Setup completed with some issues. Check the messages above.")
        print("You may need to install dependencies manually:")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()