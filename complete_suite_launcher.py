#!/usr/bin/env python3
"""
Complete Unified Automation Suite Launcher
==========================================
Launches the entire suite with beautiful gradient texture backgrounds
matching the provided design aesthetic.

Features:
- Telegram Automation Suite with gradient background
- SMS Marketplace Professional with gradient background  
- Mobile API Server
- Unified theme and texture management
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import threading
import time
import subprocess
from datetime import datetime
# Removed PIL imports since we're using flat colors only

class TexturedWindow:
    """Base class for windows with flat gray backgrounds"""
    
    def __init__(self, root, title, width=1200, height=800):
        self.root = root
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        
        # Set simple flat gray background
        self.root.configure(bg='#606060')  # Medium gray
        
        # Configure styles
        self.setup_textured_styles()
    
    def setup_textured_styles(self):
        """Setup styles for textured backgrounds"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Sophisticated 5-shade gray theme colors
        style.configure('Textured.TLabel', 
                       background='#606060',  # Medium gray
                       foreground='#E0E0E0',  # Very light gray text
                       font=('Segoe UI', 10))
        
        style.configure('Textured.TFrame', 
                       background='#606060',  # Medium gray
                       borderwidth=0)
        
        style.configure('Textured.TButton',
                       background='#808080',  # Light gray
                       foreground='#E0E0E0',  # Very light gray text
                       borderwidth=1,
                       relief='flat',
                       font=('Segoe UI', 9, 'bold'))
        style.map('Textured.TButton',
                 background=[('active', '#909090'), ('pressed', '#707070')])
        
        style.configure('Textured.TEntry',
                       fieldbackground='#505050',  # Dark gray
                       foreground='#E0E0E0',  # Very light gray text
                       borderwidth=1,
                       insertcolor='#E0E0E0')
        
        style.configure('Textured.TLabelFrame',
                       background='#505050',  # Dark gray
                       foreground='#E0E0E0',  # Very light gray text
                       borderwidth=2,
                       relief='groove')
        
        style.configure('Title.TLabel',
                       background='#606060',  # Medium gray
                       foreground='#C0C0C0',  # Light gray text
                       font=('Segoe UI', 24, 'bold'))
        
        style.configure('Subtitle.TLabel',
                       background='#606060',  # Medium gray
                       foreground='#D0D0D0',  # Light gray text
                       font=('Segoe UI', 12))

class CompleteSuiteLauncher:
    """Main launcher for the complete automation suite"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.textured_window = TexturedWindow(
            self.root, 
            "⚙️ Complete Unified Automation Suite", 
            1600, 700  # Wider but less tall
        )
        
        self.processes = {}
        self.create_interface()
        
        # Cleanup on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_interface(self):
        """Create the main launcher interface"""
        # Main container with gray background - optimized for wide layout
        main_frame = tk.Frame(self.root, bg='#606060', highlightthickness=0)
        main_frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)
        
        # Header
        self.create_header(main_frame)
        
        # Tool panels
        self.create_tool_panels(main_frame)
        
        # Status and control panel
        self.create_control_panel(main_frame)
    
    def create_header(self, parent):
        """Create beautiful header with gradient text effects"""
        header_frame = tk.Frame(parent, bg='#606060', highlightthickness=0)
        header_frame.pack(fill=tk.X, pady=(20, 40))
        
        # Main title
        title_label = tk.Label(header_frame,
                              text="⚙️ UNIFIED AUTOMATION SUITE",
                              font=('Segoe UI', 28, 'bold'),
                              fg='#C0C0C0',  # Light gray
                              bg='#606060',  # Medium gray
                              highlightthickness=0)
        title_label.pack()
        
        # Subtitle
        subtitle_label = tk.Label(header_frame,
                                 text="Professional Telegram Automation & SMS Marketplace with Mobile API",
                                 font=('Segoe UI', 14),
                                 fg='#D0D0D0',  # Light gray
                                 bg='#606060',  # Medium gray
                                 highlightthickness=0)
        subtitle_label.pack(pady=(10, 0))
        
        # Feature highlights - horizontal layout for wide interface
        features_frame = tk.Frame(header_frame, bg='#606060', highlightthickness=0)
        features_frame.pack(pady=(15, 0))
        
        features = [
            "◆ Premium Features", "◆ Multi-Market", "◆ Mobile API", 
            "◆ Performance Scaling", "◆ Revenue Optimization"
        ]
        
        for i, feature in enumerate(features):
            feature_label = tk.Label(features_frame,
                                   text=feature,
                                   font=('Segoe UI', 9, 'bold'),
                                   fg='#B0B0B0',  # Medium-light gray
                                   bg='#606060',  # Medium gray
                                   highlightthickness=0)
            feature_label.grid(row=0, column=i, padx=12)
    
    def create_tool_panels(self, parent):
        """Create tool launch panels"""
        tools_frame = tk.Frame(parent, bg='#606060', highlightthickness=0)
        tools_frame.pack(fill=tk.BOTH, expand=True, pady=10)  # Less vertical padding
        
        # Configure grid
        tools_frame.grid_columnconfigure(0, weight=1)
        tools_frame.grid_columnconfigure(1, weight=1)
        tools_frame.grid_rowconfigure(0, weight=1)
        
        # Telegram Automation Panel
        self.create_telegram_panel(tools_frame)
        
        # SMS Marketplace Panel
        self.create_sms_panel(tools_frame)
    
    def create_telegram_panel(self, parent):
        """Create Telegram automation panel with gradient background"""
        # Create semi-transparent background
        telegram_bg = tk.Frame(parent, bg='#505050', highlightthickness=2, 
                              highlightbackground='#808080', relief='groove')
        telegram_bg.grid(row=0, column=0, padx=(0, 10), pady=10, sticky='nsew')
        
        # Make background semi-transparent
        telegram_bg.configure(bg='#606060')
        
        # Content frame
        content_frame = tk.Frame(telegram_bg, bg='#606060', highlightthickness=0)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(content_frame,
                              text="📱 TELEGRAM AUTOMATION",
                              font=('Segoe UI', 16, 'bold'),  # Smaller font
                              fg='#808080',
                              bg='#606060',
                              highlightthickness=0)
        title_label.pack(pady=(0, 10))  # Less padding
        
        # Features list
        features = [
            "🤖 Account Management & Automation",
            "📊 Advanced Analytics & Monitoring", 
            "🔒 Session Management & Security",
            "🎯 Bulk Operations & Scheduling",
            "📈 Real-time Performance Tracking"
        ]
        
        for feature in features:
            feature_label = tk.Label(content_frame,
                                   text=feature,
                                   font=('Segoe UI', 11),
                                   fg='#E0E0E0',
                                   bg='#606060',
                                   anchor='w',
                                   highlightthickness=0)
            feature_label.pack(fill=tk.X, pady=2)
        
        # Status
        self.telegram_status = tk.Label(content_frame,
                                       text="Status: Not Running",
                                       font=('Segoe UI', 10, 'bold'),
                                       fg='#A0A0A0',
                                       bg='#606060',
                                       highlightthickness=0)
        self.telegram_status.pack(pady=(15, 0))
        
        # Launch button
        launch_btn = tk.Button(content_frame,
                              text="🚀 LAUNCH TELEGRAM SUITE",
                              font=('Segoe UI', 12, 'bold'),
                              bg='#808080',
                              fg='white',
                              activebackground='#229954',
                              activeforeground='white',
                              border=0,
                              padx=20,
                              pady=10,
                              command=self.launch_telegram_suite)
        launch_btn.pack(pady=(20, 0))
    
    def create_sms_panel(self, parent):
        """Create SMS marketplace panel with gradient background"""
        # Create semi-transparent background  
        sms_bg = tk.Frame(parent, bg='#505050', highlightthickness=2,
                         highlightbackground='#707070', relief='groove')
        sms_bg.grid(row=0, column=1, padx=(10, 0), pady=10, sticky='nsew')
        
        # Make background semi-transparent
        sms_bg.configure(bg='#606060')
        
        # Content frame
        content_frame = tk.Frame(sms_bg, bg='#606060', highlightthickness=0)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(content_frame,
                              text="💰 SMS MARKETPLACE",
                              font=('Segoe UI', 16, 'bold'),  # Smaller font
                              fg='#707070',
                              bg='#606060',
                              highlightthickness=0)
        title_label.pack(pady=(0, 10))  # Less padding
        
        # Features list
        features = [
            "🌍 Multi-Market Provider Support",
            "💎 Premium Subscription Tiers",
            "📱 Mobile API & Push Notifications",
            "⚡ Dynamic Pricing & Optimization", 
            "🎯 Voice Calls & Virtual Numbers"
        ]
        
        for feature in features:
            feature_label = tk.Label(content_frame,
                                   text=feature,
                                   font=('Segoe UI', 11),
                                   fg='#E0E0E0',
                                   bg='#606060',
                                   anchor='w',
                                   highlightthickness=0)
            feature_label.pack(fill=tk.X, pady=2)
        
        # Status
        self.sms_status = tk.Label(content_frame,
                                  text="Status: Not Running",
                                  font=('Segoe UI', 10, 'bold'),
                                  fg='#A0A0A0',
                                  bg='#606060',
                                  highlightthickness=0)
        self.sms_status.pack(pady=(15, 0))
        
        # Launch button
        launch_btn = tk.Button(content_frame,
                              text="🚀 LAUNCH SMS MARKETPLACE",
                              font=('Segoe UI', 12, 'bold'),
                              bg='#707070',
                              fg='white',
                              activebackground='#c0392b',
                              activeforeground='white',
                              border=0,
                              padx=20,
                              pady=10,
                              command=self.launch_sms_marketplace)
        launch_btn.pack(pady=(20, 0))
    
    def create_control_panel(self, parent):
        """Create control panel"""
        control_frame = tk.Frame(parent, bg='#606060', highlightthickness=0)
        control_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(20, 0))
        
        # Launch all button
        launch_all_btn = tk.Button(control_frame,
                                  text="🚀 LAUNCH COMPLETE SUITE",
                                  font=('Segoe UI', 14, 'bold'),
                                  bg='#707070',
                                  fg='white',
                                  activebackground='#8e44ad',
                                  activeforeground='white',
                                  border=0,
                                  padx=30,
                                  pady=15,
                                  command=self.launch_complete_suite)
        launch_all_btn.pack(side=tk.LEFT)
        
        # Stop all button
        stop_all_btn = tk.Button(control_frame,
                                text="🛑 STOP ALL",
                                font=('Segoe UI', 12, 'bold'),
                                bg='#707070',
                                fg='white',
                                activebackground='#c0392b',
                                activeforeground='white',
                                border=0,
                                padx=20,
                                pady=12,
                                command=self.stop_all)
        stop_all_btn.pack(side=tk.LEFT, padx=(20, 0))
        
        # Status display
        self.main_status = tk.Label(control_frame,
                                   text="Ready to launch suite",
                                   font=('Segoe UI', 12),
                                   fg='#808080',
                                   bg='#606060',
                                   highlightthickness=0)
        self.main_status.pack(side=tk.RIGHT, padx=(0, 20))
    
    def launch_telegram_suite(self):
        """Launch Telegram automation suite with textured background"""
        try:
            self.telegram_status.configure(text="Status: Launching...", fg='#A0A0A0')
            self.root.update()
            
            # Apply textured theme to Telegram GUI first
            self.apply_texture_to_telegram()
            
            # Launch in separate process
            telegram_thread = threading.Thread(target=self._start_telegram_process, daemon=True)
            telegram_thread.start()
            
        except Exception as e:
            messagebox.showerror("Launch Error", f"Failed to launch Telegram suite: {e}")
            self.telegram_status.configure(text="Status: Failed", fg='#707070')
    
    def apply_texture_to_telegram(self):
        """Apply gradient texture theme to Telegram GUI"""
        # This would modify the Telegram GUI to use textured backgrounds
        # Implementation would involve updating the enhanced_telegram_gui.py
        # to use TexturedWindow base class
        pass
    
    def launch_sms_marketplace(self):
        """Launch SMS marketplace with textured background"""
        try:
            self.sms_status.configure(text="Status: Launching...", fg='#A0A0A0')
            self.root.update()
            
            # Apply textured theme to SMS marketplace
            self.apply_texture_to_sms()
            
            # Launch SMS marketplace
            sms_thread = threading.Thread(target=self._start_sms_process, daemon=True)
            sms_thread.start()
            
        except Exception as e:
            messagebox.showerror("Launch Error", f"Failed to launch SMS marketplace: {e}")
            self.sms_status.configure(text="Status: Failed", fg='#707070')
    
    def apply_texture_to_sms(self):
        """Apply gradient texture theme to SMS marketplace"""
        # This would modify the SMS marketplace to use textured backgrounds
        pass
    
    def _start_telegram_process(self):
        """Start Telegram automation in separate process"""
        try:
            # Change to main directory and launch
            os.chdir('/home/nike/Desktop/TELEGRAM MAIN')
            process = subprocess.Popen([sys.executable, 'enhanced_telegram_gui.py'], 
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes['telegram'] = process
            
            self.root.after(0, lambda: self.telegram_status.configure(
                text="Status: Running ✓", fg='#808080'))
            
        except Exception as e:
            self.root.after(0, lambda: self.telegram_status.configure(
                text="Status: Error", fg='#707070'))
    
    def _start_sms_process(self):
        """Start SMS marketplace in separate process"""
        try:
            # Launch SMS marketplace from unified_automation_suite directory
            os.chdir('/home/nike/Desktop/TELEGRAM MAIN/unified_automation_suite')
            process = subprocess.Popen([sys.executable, 'marketplace_gui.py'],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes['sms'] = process
            
            self.root.after(0, lambda: self.sms_status.configure(
                text="Status: Running ✓", fg='#808080'))
            
        except Exception as e:
            self.root.after(0, lambda: self.sms_status.configure(
                text="Status: Error", fg='#707070'))
    
    def launch_complete_suite(self):
        """Launch the complete suite"""
        self.main_status.configure(text="Launching complete suite...", fg='#A0A0A0')
        self.root.update()
        
        # Launch both tools
        self.launch_telegram_suite()
        time.sleep(2)  # Brief delay
        self.launch_sms_marketplace()
        
        # Start mobile API server
        try:
            os.chdir('/home/nike/Desktop/TELEGRAM MAIN/unified_automation_suite')
            api_process = subprocess.Popen([sys.executable, 'mobile_app_api.py'],
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes['mobile_api'] = api_process
        except Exception as e:
            print(f"Failed to start mobile API: {e}")
        
        self.main_status.configure(text="Complete suite launched ✓", fg='#808080')
    
    def stop_all(self):
        """Stop all running processes"""
        for name, process in self.processes.items():
            try:
                process.terminate()
            except:
                pass
        
        self.processes.clear()
        self.telegram_status.configure(text="Status: Stopped", fg='#A0A0A0')
        self.sms_status.configure(text="Status: Stopped", fg='#A0A0A0')
        self.main_status.configure(text="All processes stopped", fg='#A0A0A0')
    
    def on_closing(self):
        """Handle window close"""
        self.stop_all()
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Start the launcher"""
        print("🚀 Starting Complete Unified Automation Suite...")
        print("🎨 Applying flat gray theme...")
        self.root.mainloop()

def main():
    """Main entry point"""
    try:
        launcher = CompleteSuiteLauncher()
        launcher.run()
        
    except Exception as e:
        print(f"❌ Error starting suite: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()