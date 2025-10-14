#!/usr/bin/env python3
"""
SMS Marketplace Suite Launcher
Starts both the enhanced GUI application and mobile API server
"""

import sys
import time
import threading
import subprocess
import signal
import os
from datetime import datetime

def print_banner():
    """Print startup banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║           📱 SMS MARKETPLACE PROFESSIONAL SUITE              ║
    ║                                                              ║
    ║  🚀 Enhanced with Premium Features & Mobile API              ║
    ║  💎 Performance Scaling & Revenue Optimization               ║
    ║  🌍 Multi-Market Expansion & Voice Calls                     ║
    ║  📊 Advanced Analytics & Push Notifications                  ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Check if required dependencies are available"""
    required_modules = [
        'tkinter',
        'flask', 
        'flask_cors',
        'flask_limiter',
        'PyJWT',
        'requests',
        'numpy',
        'aiohttp'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module.replace('-', '_').replace('PyJWT', 'jwt'))
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"⚠️  Missing dependencies: {', '.join(missing_modules)}")
        print("Install them with: pip install " + " ".join(missing_modules))
        return False
    
    return True

def start_mobile_api_server():
    """Start the mobile API server in a separate thread"""
    try:
        from mobile_app_api import start_mobile_api_server
        print(f"📱 Starting Mobile API Server at {datetime.now().strftime('%H:%M:%S')}")
        start_mobile_api_server(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        print(f"❌ Failed to start Mobile API Server: {e}")

def start_gui_application():
    """Start the GUI application"""
    try:
        from marketplace_gui import SMSMarketplaceGUI
        import tkinter as tk
        
        print(f"🖥️  Starting GUI Application at {datetime.now().strftime('%H:%M:%S')}")
        
        # Create root window
        root = tk.Tk()
        root.title("SMS Marketplace Professional Suite")
        root.geometry("1200x800")
        
        # Apply dark theme to root
        root.configure(bg="#2c3e50")
        
        # Create GUI instance
        app = SMSMarketplaceGUI(root)
        
        # Add enhanced features status to GUI
        if hasattr(app, 'enhanced_features') and app.enhanced_features:
            app.log_message("🌟 Professional Suite: All enhanced features active")
            app.log_message("💡 Mobile API available at http://localhost:5000")
        
        # Start GUI main loop
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Failed to start GUI Application: {e}")
        import traceback
        traceback.print_exc()

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print(f"\n🛑 Shutdown signal received at {datetime.now().strftime('%H:%M:%S')}")
    print("Cleaning up processes...")
    sys.exit(0)

def install_dependencies():
    """Install missing dependencies"""
    print("🔧 Installing required dependencies...")
    
    packages = [
        'flask',
        'flask-cors', 
        'flask-limiter',
        'PyJWT',
        'requests',
        'numpy',
        'aiohttp'
    ]
    
    try:
        for package in packages:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        print("✅ All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def main():
    """Main launcher function"""
    print_banner()
    print(f"🚀 Starting SMS Marketplace Suite at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Check dependencies
    if not check_dependencies():
        response = input("🔧 Would you like to install missing dependencies? (y/n): ")
        if response.lower().startswith('y'):
            if not install_dependencies():
                sys.exit(1)
        else:
            print("⚠️  Cannot proceed without dependencies")
            sys.exit(1)
    
    print("✅ All dependencies available")
    
    # Start mobile API server in background thread
    print("📱 Initializing Mobile API Server...")
    api_thread = threading.Thread(target=start_mobile_api_server, daemon=True)
    api_thread.start()
    
    # Give API server time to start
    time.sleep(2)
    
    # Start GUI application in main thread
    print("🖥️  Initializing GUI Application...")
    
    try:
        start_gui_application()
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print(f"👋 SMS Marketplace Suite shut down at {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()