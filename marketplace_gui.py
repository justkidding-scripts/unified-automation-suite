#!/usr/bin/env python3
"""
SMS Marketplace GUI - Simple Implementation
==========================================
Basic SMS marketplace interface for the automation suite.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging

# Color scheme - 15% lighter black
BG_COLOR = "#2b2b2b"  # Lighter than pure black
FG_COLOR = "white"
BUTTON_COLOR = "#404040"
ACCENT_COLOR = "#0078d4"

class SMSMarketplaceGUI:
    def __init__(self, root=None):
        if root is None:
            self.root = tk.Tk()
            self.standalone = True
        else:
            self.root = root
            self.standalone = False
            
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the marketplace GUI"""
        if self.standalone:
            self.root.title("SMS Marketplace")
            self.root.geometry("720x540")  # 10% smaller
            self.root.configure(bg=BG_COLOR)
        
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title - Single instance only
        title_label = ttk.Label(main_frame, text="SMS Number Marketplace", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Provider selection
        provider_frame = ttk.LabelFrame(main_frame, text="SMS Provider")
        provider_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.provider_var = tk.StringVar(value="SMS-Activate")
        providers = ["SMS-Activate", "5SIM", "GetSMSCode", "SMSPool"]
        
        for i, provider in enumerate(providers):
            ttk.Radiobutton(provider_frame, text=provider, variable=self.provider_var, 
                          value=provider).grid(row=0, column=i, padx=10, pady=5)
        
        # Number selection
        number_frame = ttk.LabelFrame(main_frame, text="Phone Number Options")
        number_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(number_frame, text="Country:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.country_var = tk.StringVar(value="United States")
        country_combo = ttk.Combobox(number_frame, textvariable=self.country_var, 
                                   values=["United States", "United Kingdom", "Germany", "France", "Russia"])
        country_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(number_frame, text="Service:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.service_var = tk.StringVar(value="Telegram")
        service_combo = ttk.Combobox(number_frame, textvariable=self.service_var,
                                   values=["Telegram", "WhatsApp", "Discord", "Twitter", "Instagram"])
        service_combo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        number_frame.columnconfigure(1, weight=1)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Get Number", command=self.get_number).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Get SMS Code", command=self.get_sms).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel Number", command=self.cancel_number).pack(side=tk.LEFT)
        
        # Status display
        status_frame = ttk.LabelFrame(main_frame, text="Status")
        status_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.status_text = tk.Text(status_frame, height=10, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_message("SMS Marketplace initialized")
        self.log_message("Select provider and configure options above")
        
    def log_message(self, message):
        """Add message to status display"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        
    def get_number(self):
        """Get a phone number"""
        provider = self.provider_var.get()
        country = self.country_var.get()
        service = self.service_var.get()
        
        self.log_message(f"Requesting number from {provider}")
        self.log_message(f"Country: {country}, Service: {service}")
        
        # Simulate API call
        import time
        self.root.after(1000, lambda: self.log_message("Number acquired: +1-555-0123 (Demo)"))
        self.log_message("⏳ Contacting API...")
        
    def get_sms(self):
        """Get SMS code"""
        self.log_message("Waiting for SMS code...")
        self.log_message("⏳ Checking for incoming messages...")
        
        # Simulate SMS arrival
        self.root.after(3000, lambda: self.log_message("📱 SMS received: 12345 (Demo)"))
        
    def cancel_number(self):
        """Cancel the current number"""
        self.log_message("❌ Number cancelled")
        
    def run(self):
        """Run the standalone GUI"""
        if self.standalone:
            self.root.mainloop()

def main():
    """Main entry point"""
    logging.basicConfig(level=logging.INFO)
    app = SMSMarketplaceGUI()
    app.run()

if __name__ == "__main__":
    main()