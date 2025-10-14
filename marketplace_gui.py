#!/usr/bin/env python3
"""
SMS Marketplace GUI - Professional Implementation
==============================================
Full-featured SMS marketplace with real API integration, crypto payments, and bulk purchasing.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
import random
import threading
import time
import csv
import json
from datetime import datetime
from typing import List, Dict, Optional

# Import our new modules
from sms_providers import provider_manager, PhoneNumber, ProviderStatus
from crypto_payments import payment_processor, CryptoType, PaymentStatus

# Professional dark theme (matching TGram.Pro)
BG_COLOR = "#2c3e50"  # Dark blue-gray background
FG_COLOR = "#ecf0f1"  # Light text
FRAME_COLOR = "#34495e"  # Darker blue-gray frames
BUTTON_COLOR = "#3498db"  # Professional blue buttons
BUTTON_HOVER = "#2980b9"  # Darker blue on hover
ACCENT_COLOR = "#e74c3c"  # Red accent for important items
SUCCESS_COLOR = "#27ae60"  # Green for success
WARNING_COLOR = "#f39c12"  # Orange for warnings

class SMSMarketplaceGUI:
    def __init__(self, root=None):
        if root is None:
            self.root = tk.Tk()
            self.standalone = True
        else:
            self.root = root
            self.standalone = False
            
        # Initialize state variables
        self.available_numbers = []
        self.purchased_numbers = []
        self.current_payments = {}
        self.auto_refresh_enabled = tk.BooleanVar(value=True)
        self.refresh_thread = None
        self.refresh_running = False
        
        # Price filtering
        self.min_price = tk.DoubleVar(value=0.0)
        self.max_price = tk.DoubleVar(value=10.0)
        
        # Bulk purchase settings
        self.bulk_quantity = tk.IntVar(value=1)
        self.bulk_progress = tk.DoubleVar(value=0.0)
        
        self.setup_gui()
        self.start_auto_refresh()
        
    def setup_gui(self):
        """Setup the marketplace GUI"""
        if self.standalone:
            self.root.title("SMS Number Marketplace")
            self.root.geometry("900x700")  # Larger for phone number display
            self.root.configure(bg=BG_COLOR)
            
        # Configure professional dark theme
        style = ttk.Style()
        
        # Configure dark theme styles
        style.theme_use('clam')  # Use clam theme as base
        
        # Configure Frame styles (simplified to avoid layout conflicts)
        style.configure('TFrame', background=BG_COLOR, borderwidth=0)
        style.configure('TLabelFrame', 
                       background=BG_COLOR, 
                       foreground=FG_COLOR,
                       borderwidth=2)
        style.configure('TLabelFrame.Label', 
                       background=BG_COLOR, 
                       foreground=FG_COLOR,
                       font=('Segoe UI', 10, 'bold'))
        
        # Configure Button styles
        style.configure('TButton',
                       background=BUTTON_COLOR,
                       foreground='white',
                       borderwidth=1,
                       focuscolor='none',
                       font=('Segoe UI', 9))
        style.map('TButton',
                 background=[('active', BUTTON_HOVER),
                           ('pressed', BUTTON_HOVER)],
                 foreground=[('active', 'white'),
                           ('pressed', 'white')])
        
        # Configure Label styles
        style.configure('TLabel',
                       background=BG_COLOR,
                       foreground=FG_COLOR,
                       font=('Segoe UI', 9))
        
        # Configure Entry styles
        style.configure('TEntry',
                       fieldbackground=FRAME_COLOR,
                       foreground=FG_COLOR,
                       borderwidth=1,
                       insertcolor=FG_COLOR)
        
        # Configure Combobox styles
        style.configure('TCombobox',
                       fieldbackground=FRAME_COLOR,
                       background=FRAME_COLOR,
                       foreground=FG_COLOR,
                       arrowcolor=FG_COLOR,
                       borderwidth=1)
        style.map('TCombobox',
                 fieldbackground=[('readonly', FRAME_COLOR)],
                 selectbackground=[('readonly', BUTTON_COLOR)])
        
        # Configure Treeview styles
        style.configure('Treeview',
                       background=FRAME_COLOR,
                       foreground=FG_COLOR,
                       fieldbackground=FRAME_COLOR,
                       borderwidth=1,
                       font=('Consolas', 9))
        style.configure('Treeview.Heading',
                       background=BUTTON_COLOR,
                       foreground='white',
                       relief='flat',
                       font=('Segoe UI', 9, 'bold'))
        style.map('Treeview',
                 background=[('selected', BUTTON_COLOR)],
                 foreground=[('selected', 'white')])
        
        # Configure Notebook styles
        style.configure('TNotebook',
                       background=BG_COLOR,
                       borderwidth=0,
                       tabmargins=[2, 5, 2, 0])
        style.configure('TNotebook.Tab',
                       background=FRAME_COLOR,
                       foreground=FG_COLOR,
                       padding=[20, 8],
                       font=('Segoe UI', 9, 'bold'))
        style.map('TNotebook.Tab',
                 background=[('selected', BUTTON_COLOR),
                           ('active', BUTTON_HOVER)],
                 foreground=[('selected', 'white'),
                           ('active', 'white')])
        
        # Configure Progressbar styles
        style.configure('Horizontal.TProgressbar',
                       background=SUCCESS_COLOR,
                       troughcolor=FRAME_COLOR,
                       borderwidth=0,
                       lightcolor=SUCCESS_COLOR,
                       darkcolor=SUCCESS_COLOR)
        
        # Main frame with dark theme
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Title with dark theme
        title_label = ttk.Label(main_frame, text="📱 SMS Number Marketplace", 
                               font=("Segoe UI", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Provider selection with dark theme
        provider_frame = ttk.LabelFrame(main_frame, text="SMS Provider")
        provider_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.provider_var = tk.StringVar(value="SMS-Activate")
        providers = ["SMS-Activate", "5SIM", "GetSMSCode", "SMSPool", "SMSHUB", "Grizzly-SMS"]
        
        for i, provider in enumerate(providers):
            ttk.Radiobutton(provider_frame, text=provider, variable=self.provider_var, 
                          value=provider, command=self.refresh_numbers_manual).grid(row=0, column=i, padx=10, pady=10)
        
        # Configuration frame with dark theme
        config_frame = ttk.LabelFrame(main_frame, text="Configuration")
        config_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Country and Service selection
        ttk.Label(config_frame, text="Country:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=8)
        self.country_var = tk.StringVar(value="United States")
        country_combo = ttk.Combobox(config_frame, textvariable=self.country_var, 
                                   values=["United States", "United Kingdom", "Canada", "Germany", "France", "Russia", "Poland", "Netherlands", "Sweden", "Norway"], 
                                   state="readonly")
        country_combo.grid(row=0, column=1, padx=10, pady=8, sticky=tk.EW)
        country_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_numbers_manual())
        
        ttk.Label(config_frame, text="Service:").grid(row=0, column=2, sticky=tk.W, padx=10, pady=8)
        self.service_var = tk.StringVar(value="Telegram")
        service_combo = ttk.Combobox(config_frame, textvariable=self.service_var,
                                   values=["Telegram", "WhatsApp", "Discord", "Twitter", "Instagram", "Signal", "Viber", "WeChat"], 
                                   state="readonly")
        service_combo.grid(row=0, column=3, padx=10, pady=8, sticky=tk.EW)
        service_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_numbers_manual())
        
        config_frame.columnconfigure(1, weight=1)
        config_frame.columnconfigure(3, weight=1)
        
        # Advanced Filtering Frame with dark theme
        filter_frame = ttk.LabelFrame(main_frame, text="Advanced Filters")
        filter_frame.pack(fill=tk.X, pady=(0, 15))
        
        filter_row1 = ttk.Frame(filter_frame)
        filter_row1.pack(fill=tk.X, padx=10, pady=8)
        
        ttk.Label(filter_row1, text="Price Range:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(filter_row1, text="$").pack(side=tk.LEFT)
        min_price_entry = ttk.Entry(filter_row1, textvariable=self.min_price, width=8)
        min_price_entry.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(filter_row1, text="to $").pack(side=tk.LEFT, padx=(5, 0))
        max_price_entry = ttk.Entry(filter_row1, textvariable=self.max_price, width=8)
        max_price_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Button(filter_row1, text="Apply Filter", command=self.apply_filters).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(filter_row1, text="Clear Filter", command=self.clear_filters).pack(side=tk.LEFT)
        
        auto_refresh_cb = ttk.Checkbutton(filter_row1, text="Auto-Refresh (30s)", 
                                        variable=self.auto_refresh_enabled, 
                                        command=self.toggle_auto_refresh)
        auto_refresh_cb.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Notebook for different tabs with dark theme
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Available Numbers Tab with dark theme
        numbers_tab = ttk.Frame(notebook)
        notebook.add(numbers_tab, text="Available Numbers")
        
        # Numbers display with tree view for better formatting
        numbers_frame = ttk.Frame(numbers_tab)
        numbers_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # TreeView for numbers with dark theme
        columns = ('number', 'provider', 'country', 'service', 'price', 'status')
        self.numbers_tree = ttk.Treeview(numbers_frame, columns=columns, show='headings', height=12)
        
        # Define headings
        self.numbers_tree.heading('number', text='Phone Number')
        self.numbers_tree.heading('provider', text='Provider')
        self.numbers_tree.heading('country', text='Country')
        self.numbers_tree.heading('service', text='Service')
        self.numbers_tree.heading('price', text='Price ($)')
        self.numbers_tree.heading('status', text='Status')
        
        # Define column widths
        self.numbers_tree.column('number', width=180)
        self.numbers_tree.column('provider', width=120)
        self.numbers_tree.column('country', width=120)
        self.numbers_tree.column('service', width=100)
        self.numbers_tree.column('price', width=80)
        self.numbers_tree.column('status', width=100)
        
        # Scrollbars for TreeView
        v_scrollbar = ttk.Scrollbar(numbers_frame, orient=tk.VERTICAL, command=self.numbers_tree.yview)
        h_scrollbar = ttk.Scrollbar(numbers_frame, orient=tk.HORIZONTAL, command=self.numbers_tree.xview)
        self.numbers_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.numbers_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        numbers_frame.grid_rowconfigure(0, weight=1)
        numbers_frame.grid_columnconfigure(0, weight=1)
        
        # Purchased Numbers Tab with dark theme
        purchased_tab = ttk.Frame(notebook)
        notebook.add(purchased_tab, text="Purchased Numbers")
        
        purchased_frame = ttk.Frame(purchased_tab)
        purchased_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        purchased_columns = ('number', 'provider', 'country', 'service', 'price', 'purchase_time', 'sms_status')
        self.purchased_tree = ttk.Treeview(purchased_frame, columns=purchased_columns, show='headings', height=12)
        
        self.purchased_tree.heading('number', text='Phone Number')
        self.purchased_tree.heading('provider', text='Provider')
        self.purchased_tree.heading('country', text='Country')
        self.purchased_tree.heading('service', text='Service')
        self.purchased_tree.heading('price', text='Price ($)')
        self.purchased_tree.heading('purchase_time', text='Purchase Time')
        self.purchased_tree.heading('sms_status', text='SMS Status')
        
        self.purchased_tree.column('number', width=180)
        self.purchased_tree.column('provider', width=120)
        self.purchased_tree.column('country', width=120)
        self.purchased_tree.column('service', width=100)
        self.purchased_tree.column('price', width=80)
        self.purchased_tree.column('purchase_time', width=140)
        self.purchased_tree.column('sms_status', width=100)
        
        v_scrollbar2 = ttk.Scrollbar(purchased_frame, orient=tk.VERTICAL, command=self.purchased_tree.yview)
        self.purchased_tree.configure(yscrollcommand=v_scrollbar2.set)
        
        self.purchased_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar2.grid(row=0, column=1, sticky='ns')
        
        purchased_frame.grid_rowconfigure(0, weight=1)
        purchased_frame.grid_columnconfigure(0, weight=1)
        
        # Crypto Payments Tab with dark theme
        crypto_tab = ttk.Frame(notebook)
        notebook.add(crypto_tab, text="Crypto Payments")
        
        self.setup_crypto_tab(crypto_tab)
        
        # Control buttons with enhanced functionality and dark theme
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Row 1: Main actions with dark theme
        button_row1 = ttk.Frame(button_frame)
        button_row1.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(button_row1, text="🔄 Refresh Numbers", command=self.refresh_numbers_manual).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_row1, text="💰 Purchase Selected", command=self.purchase_selected).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_row1, text="📱 Get SMS Code", command=self.get_sms_for_selected).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_row1, text="❌ Cancel Number", command=self.cancel_selected).pack(side=tk.LEFT, padx=(0, 20))
        
        # Balance display with dark theme
        self.balance_label = ttk.Label(button_row1, text="Checking balances...")
        self.balance_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Row 2: Bulk and export actions with dark theme
        button_row2 = ttk.Frame(button_frame)
        button_row2.pack(fill=tk.X, pady=(5, 0))
        
        # Bulk purchase controls with dark theme
        ttk.Label(button_row2, text="Bulk Qty:").pack(side=tk.LEFT, padx=(0, 5))
        bulk_spinner = ttk.Spinbox(button_row2, from_=1, to=50, width=5, textvariable=self.bulk_quantity)
        bulk_spinner.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_row2, text="📦 Bulk Purchase", command=self.bulk_purchase).pack(side=tk.LEFT, padx=(0, 10))
        
        # Progress bar for bulk operations with dark theme
        self.bulk_progress_bar = ttk.Progressbar(button_row2, variable=self.bulk_progress, maximum=100, length=200)
        self.bulk_progress_bar.pack(side=tk.LEFT, padx=(10, 10))
        
        ttk.Button(button_row2, text="💾 Export Data", command=self.export_data).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_row2, text="📊 Provider Stats", command=self.show_provider_stats).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Status display with dark theme
        status_frame = ttk.LabelFrame(main_frame, text="Activity Log")
        status_frame.pack(fill=tk.X, pady=(0, 0))
        
        self.status_text = tk.Text(status_frame, height=8, state=tk.DISABLED, 
                                  bg=FRAME_COLOR, fg=FG_COLOR, 
                                  font=("Consolas", 9), wrap=tk.WORD,
                                  insertbackground=FG_COLOR,
                                  selectbackground=BUTTON_COLOR,
                                  selectforeground='white')
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Initialize with demo numbers
        self.current_number = None
        self.current_purchase_id = None
        self.available_numbers = []
        
        # Load initial numbers
        self.refresh_numbers_manual()
        
        # Load initial data
        self.update_balance_display()
        self.refresh_numbers_auto()
        
        self.log_message("📱 Professional SMS Marketplace initialized")
        self.log_message("💡 Real API integration with crypto payments enabled")
        
    def setup_crypto_tab(self, crypto_tab):
        """Setup cryptocurrency payment interface"""
        crypto_frame = ttk.Frame(crypto_tab)
        crypto_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Payment Request Section with dark theme
        payment_frame = ttk.LabelFrame(crypto_frame, text="Create Payment")
        payment_frame.pack(fill=tk.X, pady=(0, 15))
        
        payment_row = ttk.Frame(payment_frame)
        payment_row.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(payment_row, text="Amount (USD):").pack(side=tk.LEFT, padx=(0, 10))
        self.payment_amount = tk.DoubleVar(value=50.0)
        amount_entry = ttk.Entry(payment_row, textvariable=self.payment_amount, width=10)
        amount_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(payment_row, text="Crypto:").pack(side=tk.LEFT, padx=(0, 10))
        self.crypto_type = tk.StringVar(value="BTC")
        crypto_combo = ttk.Combobox(payment_row, textvariable=self.crypto_type, 
                                   values=["BTC", "ETH", "USDT", "LTC", "XMR"], 
                                   state="readonly", width=8)
        crypto_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Button(payment_row, text="🔗 Create Payment", command=self.create_crypto_payment).pack(side=tk.LEFT)
        
        # Balance Display with dark theme
        balance_frame = ttk.LabelFrame(crypto_frame, text="Crypto Balances")
        balance_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.balance_tree = ttk.Treeview(balance_frame, columns=('crypto', 'balance', 'usd_value'), show='headings', height=5)
        self.balance_tree.heading('crypto', text='Cryptocurrency')
        self.balance_tree.heading('balance', text='Balance')
        self.balance_tree.heading('usd_value', text='USD Value')
        
        self.balance_tree.column('crypto', width=150)
        self.balance_tree.column('balance', width=150)
        self.balance_tree.column('usd_value', width=150)
        
        self.balance_tree.pack(fill=tk.X, padx=10, pady=10)
        
        # Payment History with dark theme
        history_frame = ttk.LabelFrame(crypto_frame, text="Payment History")
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        history_columns = ('payment_id', 'amount_usd', 'crypto_type', 'amount_crypto', 'status', 'created_at')
        self.payment_tree = ttk.Treeview(history_frame, columns=history_columns, show='headings', height=8)
        
        self.payment_tree.heading('payment_id', text='Payment ID')
        self.payment_tree.heading('amount_usd', text='USD Amount')
        self.payment_tree.heading('crypto_type', text='Crypto')
        self.payment_tree.heading('amount_crypto', text='Crypto Amount')
        self.payment_tree.heading('status', text='Status')
        self.payment_tree.heading('created_at', text='Created')
        
        self.payment_tree.column('payment_id', width=120)
        self.payment_tree.column('amount_usd', width=80)
        self.payment_tree.column('crypto_type', width=60)
        self.payment_tree.column('amount_crypto', width=120)
        self.payment_tree.column('status', width=80)
        self.payment_tree.column('created_at', width=130)
        
        payment_scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.payment_tree.yview)
        self.payment_tree.configure(yscrollcommand=payment_scrollbar.set)
        
        self.payment_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        payment_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Update crypto data
        self.update_crypto_balances()
        self.update_payment_history()
        
    def log_message(self, message):
        """Add message to status display"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        
    def refresh_numbers_auto(self):
        """Auto refresh numbers using real APIs"""
        if not self.refresh_running:
            return
            
        threading.Thread(target=self._refresh_numbers_thread, daemon=True).start()
        
    def refresh_numbers_manual(self):
        """Manual refresh triggered by button"""
        threading.Thread(target=self._refresh_numbers_thread, daemon=True).start()
        
    def _refresh_numbers_thread(self):
        """Background thread for refreshing numbers"""
        try:
            provider = self.provider_var.get()
            country = self.country_var.get()
            service = self.service_var.get()
            
            self.root.after(0, lambda: self.log_message(f"🔄 Refreshing numbers from {provider}"))
            self.root.after(0, lambda: self.log_message(f"📍 {country} | 🔧 {service}"))
            
            # Get real numbers from provider APIs
            if provider in provider_manager.get_all_providers():
                provider_obj = provider_manager.get_provider(provider)
                if provider_obj:
                    numbers = provider_obj.get_available_numbers(country, service)
                else:
                    numbers = self._generate_demo_numbers(provider, country, service)
            else:
                numbers = self._generate_demo_numbers(provider, country, service)
            
            # Apply price filters
            filtered_numbers = []
            for number in numbers:
                if self.min_price.get() <= number.price <= self.max_price.get():
                    filtered_numbers.append(number)
            
            self.available_numbers = filtered_numbers
            
            # Update UI on main thread
            self.root.after(0, lambda: self._update_numbers_display())
            self.root.after(0, lambda: self.log_message(f"✅ Found {len(filtered_numbers)} available numbers"))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.log_message(f"❌ Error refreshing numbers: {error_msg}"))
            
    def _generate_demo_numbers(self, provider: str, country: str, service: str) -> List[PhoneNumber]:
        """Generate demo numbers when API is not available"""
        country_codes = {
            "United States": "+1", "United Kingdom": "+44", "Canada": "+1",
            "Germany": "+49", "France": "+33", "Russia": "+7",
            "Poland": "+48", "Netherlands": "+31", "Sweden": "+46", "Norway": "+47"
        }
        
        country_code = country_codes.get(country, "+1")
        numbers = []
        
        for i in range(random.randint(10, 20)):
            if country_code == "+1":
                number = f"{country_code}-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}"
            elif country_code == "+44":
                number = f"{country_code}-{random.randint(7000,7999)}-{random.randint(100000,999999)}"
            elif country_code in ["+49", "+33", "+31"]:
                number = f"{country_code}-{random.randint(100,999)}-{random.randint(1000000,9999999)}"
            else:
                number = f"{country_code}-{random.randint(900,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}"
            
            price = round(random.uniform(0.15, 2.50), 2)
            status = random.choice(["available", "available", "available", "reserved"])
            
            phone_number = PhoneNumber(
                number=number,
                provider=provider,
                country=country,
                service=service,
                price=price,
                status=status
            )
            numbers.append(phone_number)
            
        return numbers
        
    def _update_numbers_display(self):
        """Update the numbers TreeView display"""
        # Clear existing items
        for item in self.numbers_tree.get_children():
            self.numbers_tree.delete(item)
            
        # Add new items
        for number in self.available_numbers:
            status_display = number.status.title()
            
            item = self.numbers_tree.insert('', 'end', values=(
                number.number,
                number.provider,
                number.country,
                number.service,
                f"${number.price:.2f}",
                status_display
            ))
            
            # Color coding based on status
            if number.status == "reserved":
                self.numbers_tree.item(item, tags=('reserved',))
            elif number.status == "in_use":
                self.numbers_tree.item(item, tags=('in_use',))
            else:
                self.numbers_tree.item(item, tags=('available',))
                
        # Configure tags for coloring with dark theme
        self.numbers_tree.tag_configure('available', background=SUCCESS_COLOR, foreground='white')
        self.numbers_tree.tag_configure('reserved', background=WARNING_COLOR, foreground='white')
        self.numbers_tree.tag_configure('in_use', background=ACCENT_COLOR, foreground='white')
        
    # Enhanced functionality methods
    def start_auto_refresh(self):
        """Start the auto-refresh system"""
        self.refresh_running = True
        self._schedule_next_refresh()
        
    def _schedule_next_refresh(self):
        """Schedule the next auto refresh"""
        if self.auto_refresh_enabled.get() and self.refresh_running:
            self.root.after(30000, self._auto_refresh_callback)  # 30 seconds
            
    def _auto_refresh_callback(self):
        """Auto refresh callback"""
        if self.auto_refresh_enabled.get() and self.refresh_running:
            self.refresh_numbers_auto()
            self._schedule_next_refresh()
            
    def toggle_auto_refresh(self):
        """Toggle auto refresh on/off"""
        if self.auto_refresh_enabled.get():
            self.log_message("✅ Auto-refresh enabled (30s intervals)")
            self._schedule_next_refresh()
        else:
            self.log_message("❌ Auto-refresh disabled")
            
    def apply_filters(self):
        """Apply price and other filters"""
        self.log_message(f"🔍 Applying filters: ${self.min_price.get():.2f} - ${self.max_price.get():.2f}")
        self._refresh_numbers_thread()
        
    def clear_filters(self):
        """Clear all filters"""
        self.min_price.set(0.0)
        self.max_price.set(10.0)
        self.log_message("🎆 Filters cleared")
        self._refresh_numbers_thread()
        
    def purchase_selected(self):
        """Purchase selected phone number with crypto payment"""
        selection = self.numbers_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a phone number to purchase.")
            return
            
        item = selection[0]
        values = self.numbers_tree.item(item)['values']
        
        if len(values) < 6:
            messagebox.showerror("Error", "Invalid selection.")
            return
            
        number = values[0]
        provider = values[1]
        price = float(values[4].replace('$', ''))
        
        # Find the PhoneNumber object
        selected_phone = None
        for phone in self.available_numbers:
            if phone.number == number:
                selected_phone = phone
                break
                
        if not selected_phone or selected_phone.status != "available":
            messagebox.showwarning("Unavailable", f"Number {number} is no longer available.")
            return
            
        # Show crypto payment dialog
        self._show_crypto_payment_dialog(selected_phone)
        
    def _show_crypto_payment_dialog(self, phone_number: PhoneNumber):
        """Show cryptocurrency payment dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Purchase {phone_number.number}")
        dialog.geometry("500x600")
        dialog.configure(bg=BG_COLOR)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Payment details
        details_frame = ttk.LabelFrame(dialog, text="Purchase Details")
        details_frame.pack(fill=tk.X, padx=15, pady=15)
        
        ttk.Label(details_frame, text=f"Number: {phone_number.number}").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Label(details_frame, text=f"Provider: {phone_number.provider}").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Label(details_frame, text=f"Country: {phone_number.country}").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Label(details_frame, text=f"Price: ${phone_number.price:.2f}").pack(anchor=tk.W, padx=10, pady=5)
        
        # Crypto selection
        crypto_frame = ttk.LabelFrame(dialog, text="Cryptocurrency Payment")
        crypto_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        crypto_var = tk.StringVar(value="BTC")
        for crypto in ["BTC", "ETH", "USDT", "LTC", "XMR"]:
            ttk.Radiobutton(crypto_frame, text=crypto, variable=crypto_var, value=crypto).pack(anchor=tk.W, padx=10, pady=2)
            
        # Payment info display
        self.payment_info_frame = ttk.LabelFrame(dialog, text="Payment Information")
        self.payment_info_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        def create_payment():
            try:
                crypto_type = CryptoType(crypto_var.get())
                payment_request = payment_processor.create_payment_request(
                    phone_number.price, crypto_type, 
                    {'phone_number': phone_number.number, 'provider': phone_number.provider}
                )
                
                self._show_payment_info(payment_request)
                self.current_payments[payment_request.payment_id] = (payment_request, phone_number)
                
            except Exception as e:
                messagebox.showerror("Payment Error", f"Failed to create payment: {e}")
                
        def cancel_payment():
            dialog.destroy()
            
        ttk.Button(button_frame, text="Create Payment", command=create_payment).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=cancel_payment).pack(side=tk.LEFT)
        
    def _show_payment_info(self, payment_request):
        """Display payment information in dialog"""
        # Clear previous info
        for widget in self.payment_info_frame.winfo_children():
            widget.destroy()
            
        ttk.Label(self.payment_info_frame, text=f"Payment ID: {payment_request.payment_id}").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Label(self.payment_info_frame, text=f"Amount: {payment_request.amount_crypto:.8f} {payment_request.crypto_type.value}").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Label(self.payment_info_frame, text=f"USD Value: ${payment_request.amount_usd:.2f}").pack(anchor=tk.W, padx=10, pady=5)
        
        # Wallet address (copyable)
        address_frame = ttk.Frame(self.payment_info_frame)
        address_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(address_frame, text="Send to address:").pack(anchor=tk.W)
        address_text = tk.Text(address_frame, height=3, wrap=tk.WORD)
        address_text.insert('1.0', payment_request.wallet_address)
        address_text.config(state=tk.DISABLED)
        address_text.pack(fill=tk.X, pady=(5, 0))
        
        # QR code info
        ttk.Label(self.payment_info_frame, text=f"QR Code: {payment_request.qr_code_data[:50]}...").pack(anchor=tk.W, padx=10, pady=5)
        
        # Expiry info
        ttk.Label(self.payment_info_frame, text=f"Expires: {payment_request.expires_at}").pack(anchor=tk.W, padx=10, pady=5)
        
        # Status monitoring
        status_label = ttk.Label(self.payment_info_frame, text=f"Status: {payment_request.status.value}")
        status_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # Start monitoring payment
        self._monitor_payment(payment_request.payment_id, status_label)
        
    def _monitor_payment(self, payment_id: str, status_label: ttk.Label):
        """Monitor payment status"""
        def check_status():
            try:
                payment = payment_processor.check_payment_status(payment_id)
                if payment:
                    status_label.config(text=f"Status: {payment.status.value}")
                    
                    if payment.status == PaymentStatus.CONFIRMED:
                        # Payment confirmed, complete purchase
                        if payment_id in self.current_payments:
                            _, phone_number = self.current_payments[payment_id]
                            self._complete_purchase(phone_number, payment)
                            del self.current_payments[payment_id]
                        return  # Stop monitoring
                        
                    elif payment.status in [PaymentStatus.FAILED, PaymentStatus.EXPIRED, PaymentStatus.CANCELLED]:
                        return  # Stop monitoring
                        
                # Continue monitoring if still pending
                self.root.after(10000, check_status)  # Check every 10 seconds
                
            except Exception as e:
                self.log_message(f"❌ Payment monitoring error: {e}")
                
        check_status()
        
    def _complete_purchase(self, phone_number: PhoneNumber, payment):
        """Complete the purchase after payment confirmation"""
        # Use real API to purchase number
        try:
            provider_obj = provider_manager.get_provider(phone_number.provider)
            if provider_obj:
                purchased_number = provider_obj.purchase_number(phone_number.country, phone_number.service)
                if purchased_number:
                    phone_number = purchased_number
            
            # Add to purchased numbers
            self.purchased_numbers.append(phone_number)
            self._update_purchased_display()
            
            # Log successful purchase
            self.log_message(f"✅ Successfully purchased {phone_number.number}")
            self.log_message(f"💵 Payment confirmed: {payment.transaction_hash[:16]}...")
            
            # Update RAG database
            purchase_id = self.log_to_rag_database(phone_number.number, phone_number.provider, "purchased")
            
        except Exception as e:
            self.log_message(f"❌ Purchase completion error: {e}")
            
    def bulk_purchase(self):
        """Bulk purchase multiple numbers"""
        quantity = self.bulk_quantity.get()
        if quantity < 1:
            messagebox.showwarning("Invalid Quantity", "Please enter a quantity of at least 1.")
            return
            
        available_numbers = [n for n in self.available_numbers if n.status == "available"]
        
        if len(available_numbers) < quantity:
            messagebox.showwarning("Insufficient Numbers", f"Only {len(available_numbers)} numbers available.")
            return
            
        # Calculate total cost
        selected_numbers = available_numbers[:quantity]
        total_cost = sum(n.price for n in selected_numbers)
        
        if not messagebox.askyesno("Bulk Purchase", f"Purchase {quantity} numbers for ${total_cost:.2f}?"):
            return
            
        # Start bulk purchase process
        threading.Thread(target=self._bulk_purchase_thread, args=(selected_numbers,), daemon=True).start()
        
    def _bulk_purchase_thread(self, numbers: List[PhoneNumber]):
        """Background bulk purchase processing"""
        try:
            total = len(numbers)
            completed = 0
            
            for i, number in enumerate(numbers):
                self.root.after(0, lambda p=int((i/total)*100): self.bulk_progress.set(p))
                
                # Simulate purchase process
                time.sleep(1)  # Rate limiting
                
                try:
                    provider_obj = provider_manager.get_provider(number.provider)
                    if provider_obj:
                        purchased = provider_obj.purchase_number(number.country, number.service)
                        if purchased:
                            self.purchased_numbers.append(purchased)
                            completed += 1
                            
                except Exception as e:
                    self.root.after(0, lambda: self.log_message(f"❌ Bulk purchase error for {number.number}: {e}"))
                    
            # Update progress to 100%
            self.root.after(0, lambda: self.bulk_progress.set(100))
            self.root.after(0, lambda: self._update_purchased_display())
            self.root.after(0, lambda: self.log_message(f"🎉 Bulk purchase complete: {completed}/{total} numbers purchased"))
            
            # Reset progress after 3 seconds
            self.root.after(3000, lambda: self.bulk_progress.set(0))
            
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"❌ Bulk purchase error: {e}"))
            self.root.after(0, lambda: self.bulk_progress.set(0))
            
    def _update_purchased_display(self):
        """Update purchased numbers display"""
        # Clear existing items
        for item in self.purchased_tree.get_children():
            self.purchased_tree.delete(item)
            
        # Add purchased numbers
        for number in self.purchased_numbers:
            sms_status = "Pending" if not number.sms_code else "Received"
            
            self.purchased_tree.insert('', 'end', values=(
                number.number,
                number.provider,
                number.country,
                number.service,
                f"${number.price:.2f}",
                number.purchase_time or "N/A",
                sms_status
            ))
            
    def get_sms_for_selected(self):
        """Get SMS code for selected purchased number"""
        selection = self.purchased_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a purchased number.")
            return
            
        item = selection[0]
        number = self.purchased_tree.item(item)['values'][0]
        
        # Find the PhoneNumber object
        selected_phone = None
        for phone in self.purchased_numbers:
            if phone.number == number:
                selected_phone = phone
                break
                
        if not selected_phone or not selected_phone.activation_id:
            messagebox.showwarning("No Activation", "No activation ID found for this number.")
            return
            
        # Get SMS code using provider API
        threading.Thread(target=self._get_sms_thread, args=(selected_phone,), daemon=True).start()
        
    def _get_sms_thread(self, phone_number: PhoneNumber):
        """Background SMS retrieval"""
        try:
            self.root.after(0, lambda: self.log_message(f"📱 Waiting for SMS on {phone_number.number}..."))
            
            provider_obj = provider_manager.get_provider(phone_number.provider)
            if provider_obj and phone_number.activation_id:
                # Poll for SMS code
                for attempt in range(30):  # 30 attempts, 10 seconds each = 5 minutes
                    sms_code = provider_obj.get_sms_code(phone_number.activation_id)
                    
                    if sms_code:
                        phone_number.sms_code = sms_code.code
                        self.root.after(0, lambda: self._update_purchased_display())
                        self.root.after(0, lambda: self.log_message(f"📨 SMS received: {sms_code.code}"))
                        return
                        
                    time.sleep(10)  # Wait 10 seconds between checks
                    
            self.root.after(0, lambda: self.log_message(f"⏰ SMS timeout for {phone_number.number}"))
            
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"❌ SMS retrieval error: {e}"))
            
    def cancel_selected(self):
        """Cancel selected purchased number"""
        selection = self.purchased_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a purchased number to cancel.")
            return
            
        item = selection[0]
        number = self.purchased_tree.item(item)['values'][0]
        
        # Find the PhoneNumber object
        selected_phone = None
        for phone in self.purchased_numbers:
            if phone.number == number:
                selected_phone = phone
                break
                
        if not selected_phone or not selected_phone.activation_id:
            messagebox.showwarning("Cannot Cancel", "No activation ID found for this number.")
            return
            
        if messagebox.askyesno("Cancel Number", f"Cancel number {number}? This may result in a partial refund."):
            self._cancel_number(selected_phone)
            
    def _cancel_number(self, phone_number: PhoneNumber):
        """Cancel a purchased number"""
        try:
            provider_obj = provider_manager.get_provider(phone_number.provider)
            if provider_obj and phone_number.activation_id:
                success = provider_obj.cancel_activation(phone_number.activation_id)
                
                if success:
                    # Remove from purchased numbers
                    self.purchased_numbers.remove(phone_number)
                    self._update_purchased_display()
                    self.log_message(f"✅ Successfully cancelled {phone_number.number}")
                else:
                    self.log_message(f"❌ Failed to cancel {phone_number.number}")
            else:
                self.log_message(f"❌ Cannot cancel {phone_number.number} - provider not available")
                
        except Exception as e:
            self.log_message(f"❌ Cancel error: {e}")
            
    # Export functionality
    def export_data(self):
        """Export purchased numbers and transaction data"""
        if not self.purchased_numbers:
            messagebox.showwarning("No Data", "No purchased numbers to export.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            if file_path.endswith('.json'):
                self._export_json(file_path)
            else:
                self._export_csv(file_path)
                
            self.log_message(f"💾 Exported data to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {e}")
            
    def _export_csv(self, file_path: str):
        """Export data as CSV"""
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([
                'Phone Number', 'Provider', 'Country', 'Service', 
                'Price', 'Purchase Time', 'SMS Code', 'Activation ID', 'Status'
            ])
            
            # Write data
            for number in self.purchased_numbers:
                writer.writerow([
                    number.number,
                    number.provider,
                    number.country,
                    number.service,
                    number.price,
                    number.purchase_time or '',
                    number.sms_code or '',
                    number.activation_id or '',
                    number.status
                ])
                
    def _export_json(self, file_path: str):
        """Export data as JSON"""
        data = []
        
        for number in self.purchased_numbers:
            data.append({
                'number': number.number,
                'provider': number.provider,
                'country': number.country,
                'service': number.service,
                'price': number.price,
                'purchase_time': number.purchase_time,
                'sms_code': number.sms_code,
                'activation_id': number.activation_id,
                'status': number.status
            })
            
        with open(file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False)
            
    # Provider statistics and analytics
    def show_provider_stats(self):
        """Show provider statistics window"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Provider Statistics")
        stats_window.geometry("600x500")
        stats_window.configure(bg=BG_COLOR)
        stats_window.transient(self.root)
        
        # Calculate statistics
        stats = self._calculate_provider_stats()
        
        # Create notebook for different stat categories
        notebook = ttk.Notebook(stats_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Provider performance tab
        perf_tab = ttk.Frame(notebook)
        notebook.add(perf_tab, text="Provider Performance")
        
        perf_tree = ttk.Treeview(perf_tab, columns=('provider', 'total', 'success_rate', 'avg_price'), show='headings')
        perf_tree.heading('provider', text='Provider')
        perf_tree.heading('total', text='Total Numbers')
        perf_tree.heading('success_rate', text='Success Rate')
        perf_tree.heading('avg_price', text='Avg Price')
        
        for provider, data in stats['providers'].items():
            perf_tree.insert('', 'end', values=(
                provider,
                data['total'],
                f"{data['success_rate']:.1f}%",
                f"${data['avg_price']:.2f}"
            ))
            
        perf_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Country statistics tab
        country_tab = ttk.Frame(notebook)
        notebook.add(country_tab, text="Country Statistics")
        
        country_tree = ttk.Treeview(country_tab, columns=('country', 'count', 'avg_price'), show='headings')
        country_tree.heading('country', text='Country')
        country_tree.heading('count', text='Count')
        country_tree.heading('avg_price', text='Avg Price')
        
        for country, data in stats['countries'].items():
            country_tree.insert('', 'end', values=(
                country,
                data['count'],
                f"${data['avg_price']:.2f}"
            ))
            
        country_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Overall statistics
        overall_frame = ttk.LabelFrame(stats_window, text="Overall Statistics")
        overall_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        ttk.Label(overall_frame, text=f"Total Numbers Purchased: {stats['total_numbers']}").pack(anchor=tk.W, padx=10, pady=2)
        ttk.Label(overall_frame, text=f"Total Spent: ${stats['total_spent']:.2f}").pack(anchor=tk.W, padx=10, pady=2)
        ttk.Label(overall_frame, text=f"Average Price: ${stats['avg_price']:.2f}").pack(anchor=tk.W, padx=10, pady=2)
        ttk.Label(overall_frame, text=f"SMS Success Rate: {stats['sms_success_rate']:.1f}%").pack(anchor=tk.W, padx=10, pady=2)
        
    def _calculate_provider_stats(self) -> Dict:
        """Calculate comprehensive statistics"""
        stats = {
            'providers': {},
            'countries': {},
            'total_numbers': len(self.purchased_numbers),
            'total_spent': 0.0,
            'avg_price': 0.0,
            'sms_success_rate': 0.0
        }
        
        if not self.purchased_numbers:
            return stats
            
        # Provider stats
        for number in self.purchased_numbers:
            provider = number.provider
            country = number.country
            
            # Initialize provider stats
            if provider not in stats['providers']:
                stats['providers'][provider] = {
                    'total': 0,
                    'success': 0,
                    'total_price': 0.0,
                    'success_rate': 0.0,
                    'avg_price': 0.0
                }
                
            # Initialize country stats
            if country not in stats['countries']:
                stats['countries'][country] = {
                    'count': 0,
                    'total_price': 0.0,
                    'avg_price': 0.0
                }
                
            # Update provider stats
            stats['providers'][provider]['total'] += 1
            stats['providers'][provider]['total_price'] += number.price
            
            if number.sms_code:
                stats['providers'][provider]['success'] += 1
                
            # Update country stats
            stats['countries'][country]['count'] += 1
            stats['countries'][country]['total_price'] += number.price
            
            # Update overall stats
            stats['total_spent'] += number.price
            
        # Calculate rates and averages
        stats['avg_price'] = stats['total_spent'] / stats['total_numbers']
        
        sms_success = sum(1 for n in self.purchased_numbers if n.sms_code)
        stats['sms_success_rate'] = (sms_success / stats['total_numbers']) * 100
        
        # Calculate provider averages
        for provider_data in stats['providers'].values():
            provider_data['success_rate'] = (provider_data['success'] / provider_data['total']) * 100
            provider_data['avg_price'] = provider_data['total_price'] / provider_data['total']
            
        # Calculate country averages
        for country_data in stats['countries'].values():
            country_data['avg_price'] = country_data['total_price'] / country_data['count']
            
        return stats
        
    # Cryptocurrency functions
    def create_crypto_payment(self):
        """Create a new cryptocurrency payment"""
        try:
            amount = self.payment_amount.get()
            if amount <= 0:
                messagebox.showwarning("Invalid Amount", "Please enter a positive amount.")
                return
                
            crypto_type = CryptoType(self.crypto_type.get())
            
            payment_request = payment_processor.create_payment_request(amount, crypto_type)
            
            # Show payment dialog
            self._show_crypto_payment_window(payment_request)
            
            self.update_payment_history()
            
        except Exception as e:
            messagebox.showerror("Payment Error", f"Failed to create payment: {e}")
            
    def _show_crypto_payment_window(self, payment_request):
        """Show cryptocurrency payment window"""
        pay_window = tk.Toplevel(self.root)
        pay_window.title(f"Payment - {payment_request.crypto_type.value}")
        pay_window.geometry("500x600")
        pay_window.configure(bg=BG_COLOR)
        pay_window.transient(self.root)
        pay_window.grab_set()
        
        # Payment details
        details_frame = ttk.LabelFrame(pay_window, text="Payment Details")
        details_frame.pack(fill=tk.X, padx=15, pady=15)
        
        ttk.Label(details_frame, text=f"Payment ID: {payment_request.payment_id}").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Label(details_frame, text=f"Amount: {payment_request.amount_crypto:.8f} {payment_request.crypto_type.value}").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Label(details_frame, text=f"USD Value: ${payment_request.amount_usd:.2f}").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Label(details_frame, text=f"Expires: {payment_request.expires_at}").pack(anchor=tk.W, padx=10, pady=5)
        
        # Wallet address
        address_frame = ttk.LabelFrame(pay_window, text="Send Payment To")
        address_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        address_text = tk.Text(address_frame, height=3, wrap=tk.WORD)
        address_text.insert('1.0', payment_request.wallet_address)
        address_text.config(state=tk.DISABLED)
        address_text.pack(fill=tk.X, padx=10, pady=10)
        
        # Status
        status_frame = ttk.LabelFrame(pay_window, text="Payment Status")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        status_label = ttk.Label(status_frame, text=f"Status: {payment_request.status.value}")
        status_label.pack(padx=10, pady=10)
        
        # Monitor payment status
        self._monitor_crypto_payment(payment_request.payment_id, status_label)
        
        # Close button
        ttk.Button(pay_window, text="Close", command=pay_window.destroy).pack(pady=15)
        
    def _monitor_crypto_payment(self, payment_id: str, status_label: ttk.Label):
        """Monitor crypto payment status"""
        def check_status():
            try:
                payment = payment_processor.check_payment_status(payment_id)
                if payment:
                    status_label.config(text=f"Status: {payment.status.value}")
                    
                    if payment.status == PaymentStatus.CONFIRMED:
                        self.log_message(f"✅ Payment confirmed: {payment_id}")
                        self.update_crypto_balances()
                        return  # Stop monitoring
                        
                    elif payment.status in [PaymentStatus.FAILED, PaymentStatus.EXPIRED, PaymentStatus.CANCELLED]:
                        return  # Stop monitoring
                        
                # Continue monitoring if still pending
                self.root.after(15000, check_status)  # Check every 15 seconds
                
            except Exception as e:
                self.log_message(f"❌ Payment monitoring error: {e}")
                
        check_status()
        
    def update_crypto_balances(self):
        """Update cryptocurrency balance display"""
        try:
            # Clear existing balances
            for item in self.balance_tree.get_children():
                self.balance_tree.delete(item)
                
            # Get current balances
            balances = payment_processor.get_balances()
            
            total_usd = 0.0
            for balance in balances:
                self.balance_tree.insert('', 'end', values=(
                    balance.crypto_type.value,
                    f"{balance.balance:.8f}",
                    f"${balance.usd_value:.2f}"
                ))
                total_usd += balance.usd_value
                
            # Update balance label in main interface
            if hasattr(self, 'balance_label'):
                self.balance_label.config(text=f"Total Balance: ${total_usd:.2f}")
                
        except Exception as e:
            self.log_message(f"❌ Error updating crypto balances: {e}")
            
    def update_payment_history(self):
        """Update payment history display"""
        try:
            # Clear existing payments
            for item in self.payment_tree.get_children():
                self.payment_tree.delete(item)
                
            # Get payment history
            payments = payment_processor.get_payment_history()
            
            for payment in payments:
                self.payment_tree.insert('', 'end', values=(
                    payment.payment_id,
                    f"${payment.amount_usd:.2f}",
                    payment.crypto_type.value,
                    f"{payment.amount_crypto:.8f}",
                    payment.status.value,
                    payment.created_at
                ))
                
        except Exception as e:
            self.log_message(f"❌ Error updating payment history: {e}")
            
    def update_balance_display(self):
        """Update provider balance display"""
        try:
            balances = provider_manager.get_balances()
            balance_text = " | ".join([f"{name}: ${balance:.2f}" for name, balance in balances.items()])
            
            if hasattr(self, 'balance_label'):
                self.balance_label.config(text=balance_text if balance_text else "Balances: Loading...")
                
            # Schedule next update
            self.root.after(60000, self.update_balance_display)  # Update every minute
            
        except Exception as e:
            if hasattr(self, 'balance_label'):
                self.balance_label.config(text="Balance: Error")
            
    def __del__(self):
        """Cleanup when GUI is destroyed"""
        self.refresh_running = False
        
        
        
        
        
        
    def log_to_rag_database(self, phone_number, provider, status="purchased"):
        """Log marketplace purchase to RAG database for scraper integration"""
        try:
            import sqlite3
            import json
            from datetime import datetime
            
            # Create/connect to RAG database
            conn = sqlite3.connect('rag_marketplace.db')
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS marketplace_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone_number TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    status TEXT NOT NULL,
                    service TEXT NOT NULL,
                    country TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    telegram_account_id TEXT,
                    scraper_status TEXT DEFAULT 'pending',
                    metadata TEXT
                )
            ''')
            
            # Insert purchase record
            metadata = json.dumps({
                'provider': provider,
                'service': self.service_var.get(),
                'country': self.country_var.get(),
                'purchase_time': datetime.now().isoformat()
            })
            
            cursor.execute('''
                INSERT INTO marketplace_log 
                (phone_number, provider, status, service, country, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (phone_number, provider, status, self.service_var.get(), self.country_var.get(), metadata))
            
            conn.commit()
            purchase_id = cursor.lastrowid
            conn.close()
            
            self.log_message(f"📊 Logged to RAG database: ID {purchase_id}", )
            
            # Trigger auto-insertion to Telegram scraper
            self.auto_insert_to_telegram_scraper(phone_number, purchase_id)
            
            return purchase_id
            
        except Exception as e:
            self.log_message(f"RAG database error: {e}")
            return None
            
    def auto_insert_to_telegram_scraper(self, phone_number, purchase_id):
        """Automatically insert purchased number to Telegram Scraper"""
        try:
            import subprocess
            import json
            
            # Check if Telegram GUI is running and accessible
            account_data = {
                'phone': phone_number,
                'purchase_id': purchase_id,
                'source': 'marketplace_auto',
                'status': 'ready_for_setup'
            }
            
            # Write to shared data file for Telegram scraper to pick up
            with open('marketplace_to_telegram.json', 'a') as f:
                f.write(json.dumps(account_data) + '\n')
                
            self.log_message(f"🔄 Auto-inserted {phone_number} to Telegram scraper queue")
            
            # Update RAG database with insertion status
            conn = sqlite3.connect('rag_marketplace.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE marketplace_log SET scraper_status = ? WHERE id = ?', 
                         ('inserted', purchase_id))
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.log_message(f"Auto-insertion error: {e}")
            
    def get_marketplace_users_for_scraper(self):
        """Get users from marketplace for automatic scraper insertion"""
        try:
            import sqlite3
            
            conn = sqlite3.connect('rag_marketplace.db')
            cursor = conn.cursor()
            
            # Get pending users
            cursor.execute('''
                SELECT phone_number, provider, service, country, timestamp, id
                FROM marketplace_log 
                WHERE scraper_status = 'pending' OR scraper_status = 'inserted'
                ORDER BY timestamp DESC
                LIMIT 50
            ''')
            
            users = cursor.fetchall()
            conn.close()
            
            return users
            
        except Exception as e:
            self.log_message(f"RAG retrieval error: {e}")
            return []
            
    def update_scraper_status(self, purchase_id, status):
        """Update scraper status in RAG database"""
        try:
            import sqlite3
            
            conn = sqlite3.connect('rag_marketplace.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE marketplace_log SET scraper_status = ? WHERE id = ?', 
                         (status, purchase_id))
            conn.commit()
            conn.close()
            
            self.log_message(f"Updated purchase {purchase_id} status to: {status}")
            
        except Exception as e:
            self.log_message(f"Status update error: {e}")
        
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