#!/usr/bin/env python3
"""
Unified Telegram & SMS Automation Suite - Main Entry Point
==========================================================
Professional entry point for the integrated automation platform.

Author: Enhanced by AI Assistant
Version: 3.0.0
"""

import sys
import os
import argparse
from pathlib import Path
import logging

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('unified_automation.log'),
            logging.StreamHandler()
        ]
    )

def check_dependencies():
    """Check if required dependencies are installed"""
    required_modules = [
        'tkinter', 'telethon', 'aiohttp', 'selenium', 
        'requests', 'pandas', 'sqlite3'
    ]
    
    missing = []
    for module in required_modules:
        try:
            if module == 'tkinter':
                import tkinter
            elif module == 'telethon':
                import telethon
            elif module == 'aiohttp':
                import aiohttp
            elif module == 'selenium':
                import selenium
            elif module == 'requests':
                import requests
            elif module == 'pandas':
                import pandas
            elif module == 'sqlite3':
                import sqlite3
        except ImportError:
            missing.append(module)
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("📦 Install with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies satisfied")
    return True

def launch_unified_gui():
    """Launch the unified launcher GUI"""
    try:
        from unified_launcher import main as launcher_main
        print("🚀 Launching Unified Automation Suite...")
        launcher_main()
    except ImportError as e:
        print(f"❌ Failed to import unified launcher: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to launch unified GUI: {e}")
        sys.exit(1)

def launch_telegram_gui():
    """Launch only Telegram automation GUI"""
    try:
        from enhanced_telegram_gui import main as telegram_main
        print("📱 Launching Telegram Automation GUI...")
        telegram_main()
    except ImportError as e:
        print(f"❌ Failed to import Telegram GUI: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to launch Telegram GUI: {e}")
        sys.exit(1)

def run_tests():
    """Run the integration test suite"""
    try:
        from test_integration import main as test_main
        print("🧪 Running Integration Test Suite...")
        test_main()
    except ImportError as e:
        print(f"❌ Failed to import test suite: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        sys.exit(1)

def setup_environment():
    """Setup environment and configuration"""
    print("🔧 Setting up environment...")
    
    # Create necessary directories
    directories = ['.config', 'logs', 'sessions', 'exports']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    # Create sample configuration if it doesn't exist
    config_file = Path('config.ini')
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
"""
        config_file.write_text(sample_config)
        print(f"📋 Created sample configuration: {config_file}")
    
    print("✅ Environment setup complete")

def show_info():
    """Show information about the suite"""
    info = """
🚀 Unified Telegram & SMS Automation Suite v3.0.0
==================================================

Professional-grade integrated automation platform featuring:

🔥 Core Features:
  • Advanced Telegram automation with multi-account support
  • SMS marketplace integration with real-time verification
  • Invisible member detection (premium stealth scraping)
  • Cross-tool data synchronization and workflows
  • Professional UI with multiple themes

🎯 Key Components:
  • Unified Launcher - Central control dashboard
  • Telegram GUI - Advanced automation interface  
  • Integration Manager - Data sharing and workflows
  • Test Suite - Comprehensive verification system

📂 Important Files:
  • config.ini - Main configuration
  • requirements.txt - Python dependencies
  • README.md - Complete documentation

🚀 Quick Start:
  1. Install dependencies: pip install -r requirements.txt
  2. Setup environment: python main.py --setup
  3. Run tests: python main.py --test
  4. Launch suite: python main.py --gui

💡 For detailed documentation, see README.md
"""
    print(info)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Unified Telegram & SMS Automation Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--gui', '--launcher', action='store_true',
                       help='Launch unified launcher GUI (default)')
    
    parser.add_argument('--telegram', action='store_true',
                       help='Launch only Telegram automation GUI')
    
    parser.add_argument('--test', action='store_true',
                       help='Run integration test suite')
    
    parser.add_argument('--setup', action='store_true',
                       help='Setup environment and configuration')
    
    parser.add_argument('--info', action='store_true',
                       help='Show information about the suite')
    
    parser.add_argument('--check-deps', action='store_true',
                       help='Check if dependencies are installed')
    
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Set logging level')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Show header
    print("🚀 Unified Telegram & SMS Automation Suite v3.0.0")
    print("=" * 55)
    
    # Handle specific arguments
    if args.info:
        show_info()
        return
    
    if args.check_deps:
        if not check_dependencies():
            sys.exit(1)
        return
    
    if args.setup:
        setup_environment()
        return
    
    if args.test:
        if not check_dependencies():
            sys.exit(1)
        run_tests()
        return
    
    if args.telegram:
        if not check_dependencies():
            sys.exit(1)
        launch_telegram_gui()
        return
    
    # Default: Launch unified GUI or show help
    if args.gui or len(sys.argv) == 1:
        if not check_dependencies():
            print("\n💡 Tip: Run 'python main.py --setup' first to configure the environment")
            sys.exit(1)
        launch_unified_gui()
    else:
        parser.print_help()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"\n❌ Unexpected error: {e}")
        print("💡 Check logs for more details: unified_automation.log")
        sys.exit(1)