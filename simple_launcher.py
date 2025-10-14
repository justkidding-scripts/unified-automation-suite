#!/usr/bin/env python3
"""
Simple Working Launcher for Unified Automation Suite
===================================================
A straightforward launcher that just works.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
from pathlib import Path

class SimpleLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 Unified Automation Suite")
        self.root.geometry("600x400")
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the launcher GUI"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="🚀 Unified Automation Suite", 
                         font=("Arial", 18, "bold"))
        title.pack(pady=(0, 20))
        
        subtitle = ttk.Label(main_frame, text="Professional Telegram & SMS Automation Platform", 
                           font=("Arial", 10))
        subtitle.pack(pady=(0, 30))
        
        # Main buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Telegram GUI
        telegram_btn = ttk.Button(button_frame, text="📱 Launch Telegram Automation", 
                                 command=self.launch_telegram, width=30)
        telegram_btn.pack(pady=5, fill=tk.X)
        
        # SMS Marketplace
        sms_btn = ttk.Button(button_frame, text="📞 Launch SMS Marketplace", 
                            command=self.launch_sms, width=30)
        sms_btn.pack(pady=5, fill=tk.X)
        
        # Configuration
        config_btn = ttk.Button(button_frame, text="⚙️ Open Configuration", 
                               command=self.open_config, width=30)
        config_btn.pack(pady=5, fill=tk.X)
        
        # Tests
        test_btn = ttk.Button(button_frame, text="🧪 Run Tests", 
                             command=self.run_tests, width=30)
        test_btn.pack(pady=5, fill=tk.X)
        
        # Status
        self.status_var = tk.StringVar(value="Ready to launch applications")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.pack(pady=(20, 0))
        
        # Info text
        info_text = tk.Text(main_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        info_text.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        info_content = """
🔥 Features:
• Advanced Telegram automation with multi-account support
• SMS marketplace integration for phone verification
• Professional GUI with dark theme support
• Cross-platform compatibility (Windows, Linux, macOS)
• Stealth scraping capabilities
• Real-time monitoring and logging

💡 Quick Start:
1. Click 'Launch Telegram Automation' to start the main interface
2. Configure your accounts in the settings
3. Use 'SMS Marketplace' for phone number verification
4. Run tests to verify everything is working

⚠️ Remember to configure your API credentials before use!
        """
        
        info_text.config(state=tk.NORMAL)
        info_text.insert(tk.END, info_content.strip())
        info_text.config(state=tk.DISABLED)
        
    def update_status(self, message):
        """Update status message"""
        self.status_var.set(message)
        self.root.update()
        
    def launch_telegram(self):
        """Launch Telegram automation GUI"""
        try:
            self.update_status("🚀 Launching Telegram Automation...")
            
            # Launch enhanced_telegram_gui.py directly
            python_path = sys.executable
            script_path = Path(__file__).parent / "enhanced_telegram_gui.py"
            
            if not script_path.exists():
                messagebox.showerror("Error", f"Telegram GUI script not found: {script_path}")
                self.update_status("❌ Error: Telegram GUI not found")
                return
            
            subprocess.Popen([python_path, str(script_path)])
            self.update_status("✅ Telegram Automation launched successfully")
            
        except Exception as e:
            messagebox.showerror("Launch Error", f"Failed to launch Telegram GUI: {e}")
            self.update_status(f"❌ Error: {e}")
    
    def launch_sms(self):
        """Launch SMS marketplace"""
        try:
            self.update_status("📞 Launching SMS Marketplace...")
            
            python_path = sys.executable
            script_path = Path(__file__).parent / "marketplace_gui.py"
            
            if not script_path.exists():
                messagebox.showerror("Error", f"SMS Marketplace script not found: {script_path}")
                self.update_status("❌ Error: SMS Marketplace not found")
                return
            
            subprocess.Popen([python_path, str(script_path)])
            self.update_status("✅ SMS Marketplace launched successfully")
            
        except Exception as e:
            messagebox.showerror("Launch Error", f"Failed to launch SMS Marketplace: {e}")
            self.update_status(f"❌ Error: {e}")
    
    def open_config(self):
        """Open configuration file"""
        try:
            config_path = Path(__file__).parent / "config.ini"
            
            if not config_path.exists():
                messagebox.showinfo("Info", "Creating default configuration file...")
                # Create default config
                with open(config_path, 'w') as f:
                    f.write("""[telegram_accounts]
# Add your Telegram accounts here
# account_1_api_id = YOUR_API_ID
# account_1_api_hash = YOUR_API_HASH
# account_1_phone = +1234567890

[sms_providers]
# Add your SMS provider API keys
# sms_activate_key = YOUR_API_KEY

[settings]
theme = dark
auto_save = true
log_level = INFO
""")
            
            # Try to open with default text editor
            if os.name == 'nt':  # Windows
                os.startfile(config_path)
            elif os.name == 'posix':  # Linux/macOS
                subprocess.run(['xdg-open', str(config_path)], check=True)
                
            self.update_status("📝 Configuration file opened")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open configuration: {e}")
            self.update_status(f"❌ Error: {e}")
    
    def run_tests(self):
        """Run basic tests"""
        try:
            self.update_status("🧪 Running tests...")
            
            # Basic import tests
            test_results = []
            
            try:
                import telethon
                test_results.append("✅ Telethon: OK")
            except ImportError:
                test_results.append("❌ Telethon: Missing")
            
            try:
                import selenium
                test_results.append("✅ Selenium: OK")
            except ImportError:
                test_results.append("❌ Selenium: Missing")
                
            try:
                import requests
                test_results.append("✅ Requests: OK")
            except ImportError:
                test_results.append("❌ Requests: Missing")
            
            # Check files
            required_files = [
                "enhanced_telegram_gui.py",
                "marketplace_gui.py",
                "main.py"
            ]
            
            for file in required_files:
                if Path(file).exists():
                    test_results.append(f"✅ {file}: Found")
                else:
                    test_results.append(f"❌ {file}: Missing")
            
            # Show results
            result_message = "\n".join(test_results)
            messagebox.showinfo("Test Results", result_message)
            
            self.update_status("✅ Tests completed")
            
        except Exception as e:
            messagebox.showerror("Test Error", f"Failed to run tests: {e}")
            self.update_status(f"❌ Error: {e}")
    
    def run(self):
        """Run the launcher"""
        self.root.mainloop()

def main():
    """Main entry point"""
    launcher = SimpleLauncher()
    launcher.run()

if __name__ == "__main__":
    main()