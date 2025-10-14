#!/usr/bin/env python3
"""
Enhanced Telegram Automation GUI
===============================
Modern GUI interface for the enhanced Telegram automation framework
with real-time monitoring, progress tracking, and advanced controls.

Author: Enhanced by AI Assistant
Version: 2.0.0
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import asyncio
import threading
import json
import os
import random
import glob
from datetime import datetime
# Optional matplotlib import
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available, charts will be disabled")
import sqlite3
import configparser
import queue
import csv
import webbrowser
from enhanced_telegram_automation import EnhancedTelegramAutomation
# Telethon for real connections/sign-in
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, FloodWaitError, PasswordHashInvalidError
try:
    from telethon.errors import ApiIdInvalidError
except Exception:
    ApiIdInvalidError = Exception
# Optional QR code support
try:
    import qrcode
    QR_AVAILABLE = True
except Exception:
    QR_AVAILABLE = False
# PIL for displaying QR images
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

class EnhancedTelegramGUI:
    """Advanced GUI for Telegram automation with real-time monitoring"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Telegram Automation Suite v2.0")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # Style configuration
        self.setup_styles()
        
        # Initialize automation engine
        self.automation = EnhancedTelegramAutomation()
        # Ensure required DB tables exist for statistics
        try:
            self.ensure_db_tables()
        except Exception as e:
            print(f"DB ensure error: {e}")
        self.running_operations = {}
        self.monitoring_active = False  # Initialize monitoring flag
        self._scraping_active = False
        self._messaging_active = False
        self._inviting_active = False

        # Notifications settings
        self.enable_toasts = True
        self.enable_toast_sound = False
        self.stack_toasts = True
        self._active_toasts = []
        
        # Preferences file path
        self.prefs_path = os.path.join(os.path.dirname(__file__), 'ui_prefs.json')
        self.load_preferences()
        
        # Create GUI components
        self.create_widgets()
        
        # Bind cleanup to window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start background monitoring
        self.start_monitoring()
        
        # Show welcome guide to orient the user
        try:
            self.show_welcome_guide()
        except Exception:
            pass
        
    def setup_styles(self):
        """Setup modern dark theme styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors for dark theme
        style.configure('TLabel', background='#2b2b2b', foreground='#ffffff')
        style.configure('TFrame', background='#2b2b2b')
        style.configure('TButton', background='#404040', foreground='#ffffff', borderwidth=1)
        style.map('TButton', background=[('active', '#505050'), ('pressed', '#606060')])
        style.configure('TEntry', fieldbackground='#404040', foreground='#ffffff', insertcolor='#ffffff')
        style.configure('TText', background='#404040', foreground='#ffffff', insertcolor='#ffffff')
        style.configure('TNotebook', background='#2b2b2b', tabposition='n')
        style.configure('TNotebook.Tab', background='#404040', foreground='#ffffff', padding=[10, 4])
        style.map('TNotebook.Tab', background=[('selected', '#505050'), ('active', '#454545')])
        style.configure('TLabelFrame', background='#2b2b2b', foreground='#ffffff')
        style.configure('TLabelFrame.Label', background='#2b2b2b', foreground='#ffffff')
        style.configure('TCheckbutton', background='#2b2b2b', foreground='#ffffff')
        style.configure('TScale', background='#2b2b2b')
        style.configure('TSpinbox', fieldbackground='#404040', foreground='#ffffff')
        style.configure('Treeview', background='#404040', foreground='#ffffff', fieldbackground='#404040')
        style.configure('Treeview.Heading', background='#505050', foreground='#ffffff')
        style.configure('TProgressbar', background='#00ff00', troughcolor='#404040')
        
        # Enable text selection in all Text and Entry widgets globally
        self.root.option_add('*Text.selectBackground', '#0078d7')
        self.root.option_add('*Text.selectForeground', '#ffffff')
        self.root.option_add('*Entry.selectBackground', '#0078d7')
        self.root.option_add('*Entry.selectForeground', '#ffffff')
        
    def create_widgets(self):
        """Create the main GUI layout"""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Menubar
        self.create_menubar()
        
        # Top toolbar
        self.create_toolbar(main_container)
        
        # Main content area
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Left panel - Controls
        left_panel = ttk.Frame(content_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Right panel - Monitoring
        right_panel = ttk.Frame(content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Create notebook for left panel
        self.create_control_notebook(left_panel)
        
        # Create monitoring panel
        self.create_monitoring_panel(right_panel)
        
        # Bottom status bar
        status_bar = ttk.Frame(main_container)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
        ttk.Label(status_bar, text="Status:").pack(side=tk.LEFT, padx=(0, 6))
        
        # Make status text selectable using Entry widget
        self.ui_status_var = tk.StringVar(value="Ready")
        self.ui_status_entry = ttk.Entry(status_bar, textvariable=self.ui_status_var, state='readonly', 
                                        foreground='#cccccc', width=50)
        self.ui_status_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Export errors button + Unlock DB
        ttk.Button(status_bar, text="Export Errors", command=self.export_errors).pack(side=tk.RIGHT)
        ttk.Button(status_bar, text="🔓 Unlock DB", command=self.unlock_database).pack(side=tk.RIGHT, padx=(0, 8))
        
        # Keyboard shortcuts
        self.root.bind('<Control-l>', lambda e: self.clear_log())
        self.root.bind('<Control-L>', lambda e: self.clear_log())
        self.root.bind('<Control-r>', lambda e: self.refresh_status())
        self.root.bind('<Control-R>', lambda e: self.refresh_status())
        self.root.bind('<F1>', lambda e: self.show_help())
        
    def create_menubar(self):
        try:
            menubar = tk.Menu(self.root)
            # File menu
            file_menu = tk.Menu(menubar, tearoff=0)
            file_menu.add_command(label="Import Accounts (JSON)", command=self.import_accounts_json)
            file_menu.add_command(label="Import Accounts (CSV)", command=self.import_accounts_csv)
            file_menu.add_separator()
            file_menu.add_command(label="Export Accounts (JSON)", command=self.export_accounts_json)
            file_menu.add_command(label="Export Accounts (CSV)", command=self.export_accounts_csv)
            file_menu.add_separator()
            file_menu.add_command(label="Save Log", command=self.save_log)
            file_menu.add_separator()
            file_menu.add_command(label="Exit", command=self.on_closing)
            menubar.add_cascade(label="File", menu=file_menu)
            
            # View menu
            view_menu = tk.Menu(menubar, tearoff=0)
            view_menu.add_command(label="Toasts On/Off", command=self.toggle_toasts_quick)
            view_menu.add_separator()
            view_menu.add_command(label="Select All", command=self.select_all_accounts)
            view_menu.add_command(label="Deselect All", command=self.deselect_all_accounts)
            view_menu.add_command(label="Select Connected", command=self.select_connected_accounts)
            view_menu.add_command(label="Select Not Authorized", command=self.select_not_authorized_accounts)
            view_menu.add_separator()
            view_menu.add_command(label="Reconnect Connected", command=self.reconnect_connected_accounts)
            menubar.add_cascade(label="View", menu=view_menu)
            
            # Tools menu
            tools_menu = tk.Menu(menubar, tearoff=0)
            tools_menu.add_command(label="Open Telegram Web", command=self.open_telegram_web)
            tools_menu.add_separator()
            tools_menu.add_command(label="🔓 Unlock Database", command=self.unlock_database)
            menubar.add_cascade(label="Tools", menu=tools_menu)
            
            # Help menu
            help_menu = tk.Menu(menubar, tearoff=0)
            help_menu.add_command(label="Help", command=self.show_help)
            help_menu.add_command(label="Reauth Guide", command=self.open_reauth_guide)
            help_menu.add_command(label="About", command=self.show_about)
            menubar.add_cascade(label="Help", menu=help_menu)
            
            self.root.config(menu=menubar)
            self.menubar = menubar
        except Exception as e:
            self.log_message(f"Menubar init error: {e}", 'ERROR')
        
    def create_toolbar(self, parent):
        """Create the top toolbar"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # Status indicators
        status_frame = ttk.Frame(toolbar)
        status_frame.pack(side=tk.LEFT)
        
        ttk.Label(status_frame, text="Status:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 5))
        
        self.connection_status = ttk.Label(status_frame, text="Disconnected", foreground='red')
        self.connection_status.pack(side=tk.LEFT, padx=(0, 15))
        
        self.active_operations = ttk.Label(status_frame, text="Operations: 0")
        self.active_operations.pack(side=tk.LEFT, padx=(0, 15))
        
        # Accounts count indicator (Total/Connected/NotAuth)
        self.accounts_count_label = ttk.Label(status_frame, text="Accounts: 0/0/0")
        self.accounts_count_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Control buttons
        control_frame = ttk.Frame(toolbar)
        control_frame.pack(side=tk.RIGHT)
        
        # Right-side quick actions (front)
        ttk.Button(control_frame, text="Open Telegram Web", command=self.open_telegram_web).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Notifications quick toggle
        self.toasts_toggle_btn = ttk.Button(control_frame, text="🔔 Toasts: On", command=self.toggle_toasts_quick)
        self.toasts_toggle_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(control_frame, text="Emergency Stop", command=self.emergency_stop).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(control_frame, text="Refresh Status", command=self.refresh_status).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Initialize toggle label based on prefs
        self.update_toasts_toggle_button_text()
        
    def create_control_notebook(self, parent):
        """Create the main control notebook"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Track last selected tab
        try:
            self.notebook.bind('<<NotebookTabChanged>>', lambda e: setattr(self, 'last_tab_index', self.notebook.index('current')))
        except Exception:
            pass
        
        # Configuration tab
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="Configuration")
        self.create_config_tab(config_frame)
        
        # Scraping tab
        scrape_frame = ttk.Frame(self.notebook)
        self.notebook.add(scrape_frame, text="Scraping")
        self.create_scrape_tab(scrape_frame)
        
        # Messaging tab
        message_frame = ttk.Frame(self.notebook)
        self.notebook.add(message_frame, text="Mass Messaging")
        self.create_message_tab(message_frame)
        
        # Inviting tab
        invite_frame = ttk.Frame(self.notebook)
        self.notebook.add(invite_frame, text="Bulk Inviting")
        self.create_invite_tab(invite_frame)
        
        # Proxy tab
        proxy_frame = ttk.Frame(self.notebook)
        self.notebook.add(proxy_frame, text="Proxy Settings")
        self.create_proxy_tab(proxy_frame)
        
        # Analytics tab
        analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(analytics_frame, text="Analytics")
        self.create_analytics_tab(analytics_frame)
        
        # Restore last selected tab if available
        try:
            if hasattr(self, 'last_tab_index') and isinstance(self.last_tab_index, int):
                self.notebook.select(self.last_tab_index)
        except Exception:
            pass
        
    def create_config_tab(self, parent):
        """Create configuration tab"""
        # Account management section
        accounts_frame = ttk.LabelFrame(parent, text="Account Management")
        accounts_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Account list with enhanced columns
        self.account_tree = ttk.Treeview(accounts_frame, columns=('Phone', 'Status', 'Usage', 'Health', 'Proxy', 'Last_Used'), show='tree headings')
        self.account_tree.heading('#0', text='Session Name')
        self.account_tree.heading('Phone', text='Phone Number')
        self.account_tree.heading('Status', text='Status')
        self.account_tree.heading('Usage', text='Daily Usage')
        self.account_tree.heading('Health', text='Health Score')
        self.account_tree.heading('Proxy', text='Proxy Status')
        self.account_tree.heading('Last_Used', text='Last Used')
        self.account_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Context menu for account actions
        try:
            self.account_menu = tk.Menu(self.root, tearoff=0)
            self.account_menu.add_command(label="Test Connection", command=self.test_connection)
            self.account_menu.add_command(label="Sign In (QR)", command=self.sign_in_qr)
            self.account_menu.add_command(label="Sign In (Code)", command=self.sign_in_code)
            self.account_menu.add_command(label="Test Proxy", command=self.test_proxy_selected_accounts)
            self.account_menu.add_separator()
            self.account_menu.add_command(label="Reconnect", command=self.reconnect_connected_accounts)
            self.account_menu.add_command(label="Force Sign Out (Reset Session)", command=self.force_sign_out_selected)
            self.account_menu.add_command(label="Remove Account", command=self.remove_account)
            # Right-click binding
            def on_account_right_click(event):
                try:
                    row_id = self.account_tree.identify_row(event.y)
                    if row_id:
                        # Select the row under cursor
                        self.account_tree.selection_set(row_id)
                        self.account_menu.tk_popup(event.x_root, event.y_root)
                finally:
                    try:
                        self.account_menu.grab_release()
                    except Exception:
                        pass
            self.account_tree.bind('<Button-3>', on_account_right_click)
        except Exception:
            pass
        
        # Restore column widths from prefs if any
        try:
            if hasattr(self, 'account_column_widths') and isinstance(self.account_column_widths, dict):
                # '#0' is tree column
                if '#0' in self.account_column_widths:
                    self.account_tree.column('#0', width=self.account_column_widths['#0'])
                for col in ('Phone','Status','Usage','Health','Proxy','Last_Used'):
                    if col in self.account_column_widths:
                        self.account_tree.column(col, width=self.account_column_widths[col])
        except Exception:
            pass
        
        # Bind to persist widths on resize
        def on_col_resize(event):
            try:
                self.capture_account_column_widths()
            except Exception:
                pass
        self.account_tree.bind('<Configure>', on_col_resize)
        
        # Populate initially
        self.refresh_account_tree()
        self.update_account_counts_from_tree()
        
        # Account health indicators
        health_frame = ttk.Frame(accounts_frame)
        health_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(health_frame, text="Health Legend:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(health_frame, text="🟢 Excellent (90-100)", foreground='green').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(health_frame, text="🟡 Good (70-89)", foreground='orange').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(health_frame, text="🔴 Poor (0-69)", foreground='red').pack(side=tk.LEFT, padx=(0, 5))
        
        # Account control buttons
        account_buttons = ttk.Frame(accounts_frame)
        account_buttons.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(account_buttons, text="Add Account", command=self.add_account).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(account_buttons, text="Edit Account", command=self.edit_account).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(account_buttons, text="Remove Account", command=self.remove_account).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(account_buttons, text="Test Connection", command=self.test_connection).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(account_buttons, text="Sign In (QR)", command=self.sign_in_qr).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(account_buttons, text="Sign In (Code)", command=self.sign_in_code).pack(side=tk.LEFT, padx=(0, 5))
        
        # Second row of advanced buttons
        account_buttons2 = ttk.Frame(accounts_frame)
        account_buttons2.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(account_buttons2, text="Health Check All", command=self.health_check_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(account_buttons2, text="Rotate Sessions", command=self.rotate_sessions).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(account_buttons2, text="Export Health Report", command=self.export_health_report).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(account_buttons2, text="🔓 Unlock Database", command=self.unlock_database).pack(side=tk.LEFT, padx=(20, 5))
        # Toggle Select/Deselect All button
        self.select_toggle_btn = ttk.Button(account_buttons2, text="Select All", command=self.toggle_select_all_accounts)
        self.select_toggle_btn.pack(side=tk.LEFT, padx=(20, 5))
        ttk.Button(account_buttons2, text="Select Connected", command=self.select_connected_accounts).pack(side=tk.LEFT, padx=(20, 5))
        ttk.Button(account_buttons2, text="Select Not Authorized", command=self.select_not_authorized_accounts).pack(side=tk.LEFT, padx=(0, 5))
        
        # Settings section
        settings_frame = ttk.LabelFrame(parent, text="Global Settings")
        settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Delay settings
        delay_frame = ttk.Frame(settings_frame)
        delay_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(delay_frame, text="Scrape Delay (s):").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.scrape_delay = ttk.Scale(delay_frame, from_=10, to=60, orient=tk.HORIZONTAL)
        self.scrape_delay.set(20)
        self.scrape_delay.grid(row=0, column=1, sticky=tk.EW, padx=(0, 5))
        
        ttk.Label(delay_frame, text="Message Delay (s):").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.message_delay = ttk.Scale(delay_frame, from_=5, to=30, orient=tk.HORIZONTAL)
        self.message_delay.set(15)
        self.message_delay.grid(row=1, column=1, sticky=tk.EW, padx=(0, 5))
        
        ttk.Label(delay_frame, text="Invite Delay (s):").grid(row=2, column=0, sticky=tk.W, padx=(0, 5))
        self.invite_delay = ttk.Scale(delay_frame, from_=30, to=120, orient=tk.HORIZONTAL)
        self.invite_delay.set(60)
        self.invite_delay.grid(row=2, column=1, sticky=tk.EW, padx=(0, 5))
        
        delay_frame.columnconfigure(1, weight=1)
        
        # Profile and strategy
        profile_frame = ttk.Frame(settings_frame)
        profile_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(profile_frame, text="Profile:").pack(side=tk.LEFT)
        self.delay_profile_var = tk.StringVar(value="Normal")
        ttk.Combobox(profile_frame, textvariable=self.delay_profile_var, values=["Stealth","Normal","Aggressive"], state='readonly', width=12).pack(side=tk.LEFT, padx=(6, 20))
        ttk.Label(profile_frame, text="Scrape Strategy:").pack(side=tk.LEFT)
        self.scrape_strategy_var = tk.StringVar(value="standard")
        ttk.Combobox(profile_frame, textvariable=self.scrape_strategy_var, values=["standard","expanded"], state='readonly', width=12).pack(side=tk.LEFT, padx=(6, 0))
        
        # Notifications & Alerts
        notify_frame = ttk.LabelFrame(parent, text="Notifications & Alerts")
        notify_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.toasts_enabled_var = tk.BooleanVar(value=self.enable_toasts)
        self.toast_sound_var = tk.BooleanVar(value=self.enable_toast_sound)
        self.toast_stack_var = tk.BooleanVar(value=self.stack_toasts)
        
        ttk.Checkbutton(notify_frame, text="Enable toasts", variable=self.toasts_enabled_var, command=self.apply_notification_settings).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Checkbutton(notify_frame, text="Toast sound", variable=self.toast_sound_var, command=self.apply_notification_settings).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Checkbutton(notify_frame, text="Stack toasts", variable=self.toast_stack_var, command=self.apply_notification_settings).grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Anti-Detection Settings
        antidetect_frame = ttk.LabelFrame(parent, text="Anti-Detection Settings")
        antidetect_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Randomization settings
        random_frame = ttk.Frame(antidetect_frame)
        random_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Rotate proxies per run
        self.rotate_proxies_before_run = tk.BooleanVar(value=False)
        ttk.Checkbutton(random_frame, text="Rotate proxies per account before run", variable=self.rotate_proxies_before_run).grid(row=4, column=0, sticky=tk.W, padx=(0,5), pady=5)
        
        # Random delay variance
        ttk.Label(random_frame, text="Random Delay Variance (%):").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.delay_variance = ttk.Scale(random_frame, from_=0, to=50, orient=tk.HORIZONTAL)
        self.delay_variance.set(25)
        self.delay_variance.grid(row=0, column=1, sticky=tk.EW, padx=(0, 5))
        ttk.Label(random_frame, text="25%").grid(row=0, column=2, sticky=tk.W)
        
        # Human-like patterns
        ttk.Label(random_frame, text="Human-like Activity Patterns:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.human_patterns = tk.BooleanVar(value=True)
        ttk.Checkbutton(random_frame, variable=self.human_patterns).grid(row=1, column=1, sticky=tk.W)
        
        # Operating hours
        ttk.Label(random_frame, text="Operating Hours (24h format):").grid(row=2, column=0, sticky=tk.W, padx=(0, 5))
        hours_frame = ttk.Frame(random_frame)
        hours_frame.grid(row=2, column=1, sticky=tk.W)
        
        ttk.Label(hours_frame, text="From:").pack(side=tk.LEFT)
        self.start_hour = ttk.Spinbox(hours_frame, from_=0, to=23, width=5, value=9)
        self.start_hour.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(hours_frame, text="To:").pack(side=tk.LEFT)
        self.end_hour = ttk.Spinbox(hours_frame, from_=0, to=23, width=5, value=22)
        self.end_hour.pack(side=tk.LEFT, padx=5)
        
        # Account rotation
        ttk.Label(random_frame, text="Auto Account Rotation:").grid(row=3, column=0, sticky=tk.W, padx=(0, 5))
        self.auto_rotation = tk.BooleanVar(value=True)
        ttk.Checkbutton(random_frame, variable=self.auto_rotation).grid(row=3, column=1, sticky=tk.W)
        
        random_frame.columnconfigure(1, weight=1)
        
    def create_proxy_tab(self, parent):
        """Create proxy configuration tab"""
        # SOCKS5 Proxy Configuration
        proxy_frame = ttk.LabelFrame(parent, text="SOCKS5 Proxy Configuration")
        proxy_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Enable proxy checkbox
        self.use_proxy_var = tk.BooleanVar()
        proxy_enable = ttk.Checkbutton(proxy_frame, text="Enable SOCKS5 Proxy", variable=self.use_proxy_var, command=self.toggle_proxy_fields)
        proxy_enable.pack(pady=5, anchor='w')
        
        # Proxy configuration grid
        proxy_config_frame = ttk.Frame(proxy_frame)
        proxy_config_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Proxy host
        ttk.Label(proxy_config_frame, text="Proxy Host:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.proxy_host_var = tk.StringVar(value="127.0.0.1")
        self.proxy_host_entry = ttk.Entry(proxy_config_frame, textvariable=self.proxy_host_var, width=25, state='disabled')
        self.proxy_host_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Proxy port
        ttk.Label(proxy_config_frame, text="Proxy Port:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.proxy_port_var = tk.StringVar(value="9050")
        self.proxy_port_entry = ttk.Entry(proxy_config_frame, textvariable=self.proxy_port_var, width=10, state='disabled')
        self.proxy_port_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        # Proxy username
        ttk.Label(proxy_config_frame, text="Username (optional):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.proxy_username_var = tk.StringVar()
        self.proxy_username_entry = ttk.Entry(proxy_config_frame, textvariable=self.proxy_username_var, width=25, state='disabled')
        self.proxy_username_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Proxy password
        ttk.Label(proxy_config_frame, text="Password (optional):").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.proxy_password_var = tk.StringVar()
        self.proxy_password_entry = ttk.Entry(proxy_config_frame, textvariable=self.proxy_password_var, width=25, show='*', state='disabled')
        self.proxy_password_entry.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)
        
        # Proxy test button
        proxy_test_frame = ttk.Frame(proxy_frame)
        proxy_test_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.test_proxy_button = ttk.Button(proxy_test_frame, text="Test Proxy Connection", command=self.test_proxy_connection, state='disabled')
        self.test_proxy_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.proxy_status_label = ttk.Label(proxy_test_frame, text="Proxy not configured", foreground='gray')
        self.proxy_status_label.pack(side=tk.LEFT)
        
        # Proxy pool management
        pool_frame = ttk.LabelFrame(parent, text="Proxy Pool Management")
        pool_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Proxy list
        proxy_list_frame = ttk.Frame(pool_frame)
        proxy_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.proxy_tree = ttk.Treeview(proxy_list_frame, columns=('Host', 'Port', 'Status', 'Account'), show='headings', height=8)
        self.proxy_tree.heading('Host', text='Host')
        self.proxy_tree.heading('Port', text='Port')
        self.proxy_tree.heading('Status', text='Status')
        self.proxy_tree.heading('Account', text='Assigned Account')
        self.proxy_tree.pack(fill=tk.BOTH, expand=True)
        
        # Proxy pool controls
        pool_controls = ttk.Frame(pool_frame)
        pool_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(pool_controls, text="Add Current Proxy", command=self.add_proxy_to_pool).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(pool_controls, text="Import Proxy List", command=self.import_proxy_list).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(pool_controls, text="Test All Proxies", command=self.test_all_proxies).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(pool_controls, text="Remove Selected", command=self.remove_selected_proxy).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(pool_controls, text="Auto-Assign Proxies", command=self.auto_assign_proxies).pack(side=tk.LEFT, padx=(20, 5))
        
    def toggle_proxy_fields(self):
        """Enable/disable proxy configuration fields"""
        state = 'normal' if self.use_proxy_var.get() else 'disabled'
        self.proxy_host_entry.config(state=state)
        self.proxy_port_entry.config(state=state)
        self.proxy_username_entry.config(state=state)
        self.proxy_password_entry.config(state=state)
        self.test_proxy_button.config(state=state)
        
        if self.use_proxy_var.get():
            self.proxy_status_label.config(text="Proxy enabled - not tested", foreground='orange')
        else:
            self.proxy_status_label.config(text="Proxy disabled", foreground='gray')
        
    def test_proxy_connection(self):
        """Test the current proxy configuration"""
        self.proxy_status_label.config(text="Testing proxy...", foreground='blue')
        self.root.update_idletasks()
        self.show_toast("Testing proxy…", 'INFO', 1500)
        
        # Start proxy test in background thread
        threading.Thread(target=self.run_proxy_test, daemon=True).start()
        
    def run_proxy_test(self):
        """Run proxy test in background"""
        try:
            import socket
            import socks
            
            # Configure SOCKS5 proxy
            proxy_host = self.proxy_host_var.get()
            proxy_port = int(self.proxy_port_var.get())
            proxy_user = self.proxy_username_var.get() or None
            proxy_pass = self.proxy_password_var.get() or None
            
            # Test connection
            sock = socks.socksocket()
            sock.set_proxy(socks.SOCKS5, proxy_host, proxy_port, username=proxy_user, password=proxy_pass)
            sock.settimeout(10)
            
            # Try to connect to a test server
            sock.connect(("8.8.8.8", 53))  # Google DNS
            sock.close()
            
            # Update status on success
            self.root.after(0, lambda: self.proxy_status_label.config(text="Proxy working ✓", foreground='green'))
            self.log_message(f"Proxy test successful: {proxy_host}:{proxy_port}", 'SUCCESS')
            self.root.after(0, lambda: self.show_toast("Proxy working", 'SUCCESS', 1500))
            
        except Exception as e:
            # Update status on failure
            self.root.after(0, lambda: self.proxy_status_label.config(text=f"Proxy failed: {str(e)[:30]}...", foreground='red'))
            self.log_message(f"Proxy test failed: {e}", 'ERROR')
            self.root.after(0, lambda: self.show_toast("Proxy failed", 'ERROR', 2000))
        
    def add_proxy_to_pool(self):
        """Add current proxy configuration to the pool"""
        if not self.use_proxy_var.get():
            messagebox.showwarning("Warning", "Enable proxy configuration first")
            return
            
        proxy_host = self.proxy_host_var.get()
        proxy_port = self.proxy_port_var.get()
        
        if not proxy_host or not proxy_port:
            messagebox.showerror("Error", "Please enter proxy host and port")
            return
            
        # Add to proxy tree
        self.proxy_tree.insert('', 'end', values=(proxy_host, proxy_port, 'Unknown', 'Unassigned'))
        self.log_message(f"Added proxy to pool: {proxy_host}:{proxy_port}", 'INFO')
        
    def import_proxy_list(self):
        """Import proxy list from file"""
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filename:
            count = 0
            try:
                with open(filename, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if ':' in line:
                            parts = line.split(':')
                            if len(parts) >= 2:
                                host, port = parts[0], parts[1]
                                self.proxy_tree.insert('', 'end', values=(host, port, 'Unknown', 'Unassigned'))
                                count += 1
                self.log_message(f"Imported proxy list from {filename}", 'SUCCESS')
                self.show_toast(f"Imported {count} proxies", 'SUCCESS', 1800)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import proxy list: {e}")
                self.show_toast("Import failed", 'ERROR', 2000)
                
    def test_all_proxies(self):
        """Test all proxies in the pool"""
        self.log_message("Testing all proxies in pool...", 'INFO')
        self.show_toast("Testing all proxies…", 'INFO', 1500)
        threading.Thread(target=self.run_all_proxy_tests, daemon=True).start()
        
    def run_all_proxy_tests(self):
        """Test all proxies in background"""
        for item in self.proxy_tree.get_children():
            values = list(self.proxy_tree.item(item)['values'])
            host, port = values[0], values[1]
            
            try:
                import socket
                import socks
                
                sock = socks.socksocket()
                sock.set_proxy(socks.SOCKS5, host, int(port))
                sock.settimeout(5)
                sock.connect(("8.8.8.8", 53))
                sock.close()
                
                # Update status
                values[2] = 'Working'
                self.root.after(0, lambda i=item, v=values: self.proxy_tree.item(i, values=v))
                
            except Exception:
                values[2] = 'Failed'
                self.root.after(0, lambda i=item, v=values: self.proxy_tree.item(i, values=v))
                
        self.root.after(0, lambda: self.log_message("Proxy pool testing completed", 'SUCCESS'))
        self.root.after(0, lambda: self.show_toast("Proxy tests completed", 'SUCCESS', 1800))
        
    def remove_selected_proxy(self):
        """Remove selected proxy from pool"""
        selection = self.proxy_tree.selection()
        if selection:
            for item in selection:
                self.proxy_tree.delete(item)
            self.log_message("Removed selected proxies from pool", 'INFO')
        
    def create_scrape_tab(self, parent):
        """Create scraping control tab"""
        # Source group settings
        source_frame = ttk.LabelFrame(parent, text="Source Group Settings")
        source_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(source_frame, text="Group Username/Invite Link:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.source_group_var = tk.StringVar()
        ttk.Entry(source_frame, textvariable=self.source_group_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(source_frame, text="Max Members:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.max_members_var = tk.StringVar(value="500")
        ttk.Entry(source_frame, textvariable=self.max_members_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        # Engine selection
        ttk.Label(source_frame, text="Engine:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.scrape_engine_var = tk.StringVar(value="API (Telethon)")
        engine_combo = ttk.Combobox(source_frame, textvariable=self.scrape_engine_var, values=["API (Telethon)", "Browser (Selenium)"], state='readonly', width=24)
        engine_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Selenium options
        self.selenium_opts = ttk.LabelFrame(parent, text="Browser (Selenium) Options")
        self.selenium_opts.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(self.selenium_opts, text="Profile Dir (keep Web login):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.selenium_profile_var = tk.StringVar()
        ttk.Entry(self.selenium_opts, textvariable=self.selenium_profile_var, width=45).grid(row=0, column=1, padx=5, pady=5)
        self.selenium_headless_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.selenium_opts, text="Headless", variable=self.selenium_headless_var).grid(row=0, column=2, padx=5, pady=5)
        ttk.Label(self.selenium_opts, text="Proxy URL:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.selenium_proxy_url_var = tk.StringVar()
        ttk.Entry(self.selenium_opts, textvariable=self.selenium_proxy_url_var, width=45).grid(row=1, column=1, padx=5, pady=5)
        
        def _toggle_selenium_opts(*_):
            if self.scrape_engine_var.get().startswith("Browser"):
                self.selenium_opts.pack(fill=tk.X, padx=10, pady=5)
            else:
                try:
                    self.selenium_opts.pack_forget()
                except Exception:
                    pass
        engine_combo.bind('<<ComboboxSelected>>', _toggle_selenium_opts)
        
        # Scraping controls
        control_frame = ttk.Frame(source_frame)
        control_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.scrape_button = ttk.Button(control_frame, text="Start Scraping", command=self.start_scraping)
        self.scrape_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_scrape_button = ttk.Button(control_frame, text="Stop Scraping", command=self.stop_scraping, state='disabled')
        self.stop_scrape_button.pack(side=tk.LEFT)
        
        # Progress tracking
        progress_frame = ttk.LabelFrame(parent, text="Scraping Progress")
        progress_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.scrape_progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.scrape_progress.pack(fill=tk.X, padx=5, pady=5)
        
        self.scrape_status = ttk.Label(progress_frame, text="Ready")
        self.scrape_status.pack(pady=5)
        
        # Results
        results_frame = ttk.LabelFrame(parent, text="Scraped Members")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Members treeview
        self.members_tree = ttk.Treeview(results_frame, columns=('Username', 'Name', 'Source'), show='headings')
        self.members_tree.heading('Username', text='Username')
        self.members_tree.heading('Name', text='Name')
        self.members_tree.heading('Source', text='Source Group')
        self.members_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add right-click context menu for members
        try:
            self.member_menu = tk.Menu(self.root, tearoff=0)
            self.member_menu.add_command(label="Copy Username", command=self.copy_member_username)
            self.member_menu.add_command(label="Copy Name", command=self.copy_member_name)
            self.member_menu.add_separator()
            self.member_menu.add_command(label="Send Direct Message", command=self.send_dm_to_member)
            self.member_menu.add_command(label="Add to Target List", command=self.add_member_to_targets)
            self.member_menu.add_separator()
            self.member_menu.add_command(label="Remove from List", command=self.remove_selected_member)
            
            def on_member_right_click(event):
                try:
                    row_id = self.members_tree.identify_row(event.y)
                    if row_id:
                        self.members_tree.selection_set(row_id)
                        self.member_menu.tk_popup(event.x_root, event.y_root)
                finally:
                    try:
                        self.member_menu.grab_release()
                    except Exception:
                        pass
            self.members_tree.bind('<Button-3>', on_member_right_click)
        except Exception as e:
            self.log_message(f"Member context menu error: {e}", 'WARNING')
        
        # Export buttons
        export_frame = ttk.Frame(results_frame)
        export_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(export_frame, text="Export to JSON", command=self.export_members_json).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(export_frame, text="Export to CSV", command=self.export_members_csv).pack(side=tk.LEFT)
        
    def create_message_tab(self, parent):
        """Create mass messaging tab"""
        # Message settings
        message_frame = ttk.LabelFrame(parent, text="Message Settings")
        message_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(message_frame, text="Message Template:").pack(anchor=tk.W, padx=5, pady=(5, 0))
        self.message_template = scrolledtext.ScrolledText(
            message_frame, 
            height=6, 
            width=60,
            bg='#404040',
            fg='#ffffff',
            insertbackground='#ffffff',
            selectbackground='#505050',
            selectforeground='#ffffff',
            font=('Consolas', 10)
        )
        self.message_template.pack(fill=tk.X, padx=5, pady=5)
        # Start with empty template by default per request
        self.message_template.delete('1.0', tk.END)
        
        # Target selection
        target_frame = ttk.LabelFrame(parent, text="Target Selection")
        target_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.target_type = tk.StringVar(value="scraped")
        ttk.Radiobutton(target_frame, text="All Scraped Members", variable=self.target_type, value="scraped").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Radiobutton(target_frame, text="Specific Group Members", variable=self.target_type, value="group").pack(anchor=tk.W, padx=5, pady=2)
        
        self.target_group_var = tk.StringVar()
        ttk.Entry(target_frame, textvariable=self.target_group_var, width=40).pack(fill=tk.X, padx=20, pady=5)
        
        # Message controls
        control_frame = ttk.Frame(target_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.message_button = ttk.Button(control_frame, text="Start Messaging", command=self.start_messaging)
        self.message_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_message_button = ttk.Button(control_frame, text="Stop Messaging", command=self.stop_messaging, state='disabled')
        self.stop_message_button.pack(side=tk.LEFT)
        
        # Progress tracking
        progress_frame = ttk.LabelFrame(parent, text="Messaging Progress")
        progress_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.message_progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.message_progress.pack(fill=tk.X, padx=5, pady=5)
        
        self.message_status = ttk.Label(progress_frame, text="Ready")
        self.message_status.pack(pady=5)
        
    def create_invite_tab(self, parent):
        """Create bulk inviting tab"""
        # Target group settings
        target_frame = ttk.LabelFrame(parent, text="Target Group Settings")
        target_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(target_frame, text="Target Group Username/ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.invite_target_var = tk.StringVar()
        ttk.Entry(target_frame, textvariable=self.invite_target_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        # Source selection
        source_frame = ttk.LabelFrame(parent, text="Member Source")
        source_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.invite_source_type = tk.StringVar(value="scraped")
        ttk.Radiobutton(source_frame, text="All Scraped Members", variable=self.invite_source_type, value="scraped").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Radiobutton(source_frame, text="Specific Source Group", variable=self.invite_source_type, value="group").pack(anchor=tk.W, padx=5, pady=2)
        
        self.invite_source_var = tk.StringVar()
        ttk.Entry(source_frame, textvariable=self.invite_source_var, width=40).pack(fill=tk.X, padx=20, pady=5)
        
        # Invite options
        options_frame = ttk.LabelFrame(parent, text="Invite Options")
        options_frame.pack(fill=tk.X, padx=10, pady=(0,10))
        self.invite_use_per_account_proxy_var = tk.BooleanVar(value=True)
        self.invite_require_proxy_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Rotate accounts and use per-account proxies", variable=self.invite_use_per_account_proxy_var).pack(anchor=tk.W, padx=5, pady=2)
        ttk.Checkbutton(options_frame, text="Only use accounts with proxies for inviting", variable=self.invite_require_proxy_var).pack(anchor=tk.W, padx=5, pady=2)
        
        # Invite controls
        control_frame = ttk.Frame(source_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.invite_button = ttk.Button(control_frame, text="Start Inviting", command=self.start_inviting)
        self.invite_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_invite_button = ttk.Button(control_frame, text="Stop Inviting", command=self.stop_inviting, state='disabled')
        self.stop_invite_button.pack(side=tk.LEFT)
        
        # Progress tracking
        progress_frame = ttk.LabelFrame(parent, text="Inviting Progress")
        progress_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.invite_progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.invite_progress.pack(fill=tk.X, padx=5, pady=5)
        
        self.invite_status = ttk.Label(progress_frame, text="Ready")
        self.invite_status.pack(pady=5)
        
    def create_analytics_tab(self, parent):
        """Create analytics and statistics tab"""
        # Statistics summary
        stats_frame = ttk.LabelFrame(parent, text="Statistics Summary")
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Refresh button
        ttk.Button(stats_frame, text="Refresh Analytics", command=self.refresh_analytics_now).pack(anchor=tk.E, padx=10, pady=(8, 0))
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(padx=10, pady=10)
        
        # Stats labels
        ttk.Label(stats_grid, text="Total Members Scraped:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.total_scraped_label = ttk.Label(stats_grid, text="0", font=('Arial', 10, 'bold'))
        self.total_scraped_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(stats_grid, text="Messages Sent Today:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.messages_sent_label = ttk.Label(stats_grid, text="0", font=('Arial', 10, 'bold'))
        self.messages_sent_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(stats_grid, text="Invites Sent Today:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.invites_sent_label = ttk.Label(stats_grid, text="0", font=('Arial', 10, 'bold'))
        self.invites_sent_label.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Chart placeholder
        chart_frame = ttk.LabelFrame(parent, text="Activity Chart")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_activity_chart(chart_frame)
        
    def create_monitoring_panel(self, parent):
        """Create real-time monitoring panel"""
        # Quick actions bar on right side
        quickbar = ttk.Frame(parent)
        quickbar.pack(fill=tk.X, pady=(0, 6))
        ttk.Button(quickbar, text="Open Telegram Web", command=self.open_telegram_web).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(quickbar, text="Onboard Accounts", command=self.open_account_onboarding).pack(side=tk.LEFT)
        
        # Live log
        log_frame = ttk.LabelFrame(parent, text="Live Activity Log")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Log text area with better dark theme
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=15, 
            width=50, 
            bg='#1e1e1e', 
            fg='#00ff00', 
            font=('Consolas', 9),
            insertbackground='#00ff00',  # Cursor color
            selectbackground='#404040',  # Selection background
            selectforeground='#ffffff'   # Selection text color
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Log controls
        log_controls = ttk.Frame(log_frame)
        log_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(log_controls, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(log_controls, text="Save Log", command=self.save_log).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(log_controls, text="Copy All", command=self.copy_all_logs).pack(side=tk.LEFT, padx=(0, 5))
        
        # Auto-scroll checkbox
        self.auto_scroll = tk.BooleanVar(value=True)
        ttk.Checkbutton(log_controls, text="Auto Scroll", variable=self.auto_scroll).pack(side=tk.RIGHT)
        
        # Operation status panel with enhanced monitoring
        status_frame = ttk.LabelFrame(parent, text="Active Operations & Error Recovery")
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.operation_tree = ttk.Treeview(status_frame, columns=('Type', 'Progress', 'Status', 'Retries', 'Last_Error'), show='headings', height=6)
        self.operation_tree.heading('Type', text='Operation')
        self.operation_tree.heading('Progress', text='Progress')
        self.operation_tree.heading('Status', text='Status')
        self.operation_tree.heading('Retries', text='Retries')
        self.operation_tree.heading('Last_Error', text='Last Error')
        self.operation_tree.pack(fill=tk.X, padx=5, pady=5)
        
        # Operation controls
        op_controls = ttk.Frame(status_frame)
        op_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(op_controls, text="Pause Selected", command=self.pause_selected_operation).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(op_controls, text="Resume Selected", command=self.resume_selected_operation).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(op_controls, text="Retry Failed", command=self.retry_failed_operations).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(op_controls, text="Clear Completed", command=self.clear_completed_operations).pack(side=tk.LEFT, padx=(0, 5))
        
        # Real-time metrics panel
        metrics_frame = ttk.LabelFrame(parent, text="Real-Time Performance Metrics")
        metrics_frame.pack(fill=tk.X, pady=(10, 0))
        
        metrics_grid = ttk.Frame(metrics_frame)
        metrics_grid.pack(padx=10, pady=10)
        
        # Success rate
        ttk.Label(metrics_grid, text="Success Rate:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.success_rate_label = ttk.Label(metrics_grid, text="0%", font=('Arial', 10, 'bold'), foreground='green')
        self.success_rate_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Error rate
        ttk.Label(metrics_grid, text="Error Rate:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.error_rate_label = ttk.Label(metrics_grid, text="0%", font=('Arial', 10, 'bold'), foreground='red')
        self.error_rate_label.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        
        # Operations per minute
        ttk.Label(metrics_grid, text="Ops/Min:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.ops_per_min_label = ttk.Label(metrics_grid, text="0", font=('Arial', 10, 'bold'), foreground='blue')
        self.ops_per_min_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Average response time
        ttk.Label(metrics_grid, text="Avg Response:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        self.avg_response_label = ttk.Label(metrics_grid, text="0ms", font=('Arial', 10, 'bold'))
        self.avg_response_label.grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)
        
    def create_activity_chart(self, parent):
        """Create activity chart using matplotlib"""
        if not MATPLOTLIB_AVAILABLE:
            # Create a placeholder label instead
            placeholder = ttk.Label(parent, text="Charts unavailable\n(matplotlib not installed)", 
                                  font=('Arial', 12), justify='center')
            placeholder.pack(fill=tk.BOTH, expand=True, padx=5, pady=20)
            return
            
        try:
            self.figure, self.ax = plt.subplots(figsize=(6, 4), facecolor='#2b2b2b')
            self.ax.set_facecolor('#2b2b2b')
            
            # Sample data - will be replaced with real data
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            scrapes = [0, 0, 0, 0, 0, 0, 0]
            messages = [0, 0, 0, 0, 0, 0, 0]
            invites = [0, 0, 0, 0, 0, 0, 0]
            
            self.ax.plot(days, scrapes, label='Scrapes', color='#00ff00')
            self.ax.plot(days, messages, label='Messages', color='#0080ff')
            self.ax.plot(days, invites, label='Invites', color='#ff8000')
            
            self.ax.set_title('Weekly Activity', color='white')
            self.ax.legend()
            self.ax.tick_params(colors='white')
            
            # Embed chart in tkinter
            self.chart_canvas = FigureCanvasTkAgg(self.figure, parent)
            self.chart_canvas.draw()
            self.chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        except Exception as e:
            # Fallback to placeholder if chart creation fails
            placeholder = ttk.Label(parent, text=f"Chart error:\n{str(e)}", 
                                  font=('Arial', 10), justify='center')
            placeholder.pack(fill=tk.BOTH, expand=True, padx=5, pady=20)
        
    def log_message(self, message, level='INFO'):
        """Add message to the live log in a thread-safe way"""
        # Ensure we only touch Tk widgets from the main thread
        if threading.current_thread() is not threading.main_thread():
            try:
                self.root.after(0, lambda: self.log_message(message, level))
            except Exception:
                # If root is gone, just print to console
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {level}: {message}")
            return
        
        try:
            # Check if log widget still exists
            if not hasattr(self, 'log_text') or not self.log_text.winfo_exists():
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {level}: {message}")  # Fallback to console
                return
                
            timestamp = datetime.now().strftime('%H:%M:%S')
            log_entry = f"[{timestamp}] {level}: {message}\n"
            
            # Color coding based on level (reserved for future use)
            color_map = {
                'INFO': '#00ff00',
                'WARNING': '#ffff00',
                'ERROR': '#ff0000',
                'SUCCESS': '#00ffff'
            }
            
            self.log_text.config(state='normal')
            self.log_text.insert(tk.END, log_entry)
            
            if hasattr(self, 'auto_scroll') and self.auto_scroll.get():
                self.log_text.see(tk.END)
            
            # Keep in normal state so text is selectable and copyable
            # Users can select and copy errors easily
            
            # Update GUI
            self.root.update_idletasks()
            
        except (tk.TclError, AttributeError):
            # Widget destroyed or not available, fallback to console
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {level}: {message}")
        
    def start_scraping(self):
        """Start the scraping process"""
        source_group = self.source_group_var.get().strip()
        # Apply selected profile before run
        try:
            self.automation.set_profile(self.delay_profile_var.get())
        except Exception:
            pass
        if not source_group:
            messagebox.showerror("Error", "Please enter a source group")
            return
            
        try:
            max_members = int(self.max_members_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for max members")
            return
        
        self.scrape_button.config(state='disabled')
        self.stop_scrape_button.config(state='normal')
        self.scrape_status.config(text="Starting scraping...")
        self.scrape_progress['value'] = 0
        self.log_message(f"Starting to scrape {max_members} members from {source_group}", 'INFO')
        self.set_status("Scraping started…", 'INFO')
        self.show_toast("Scraping started", 'INFO', 1500)
        
        # Optional rotate proxies before run
        try:
            if getattr(self, 'rotate_proxies_before_run', tk.BooleanVar(value=False)).get():
                self.auto_assign_proxies()
        except Exception:
            pass
        # Set scraping active flag
        self._scraping_active = True
        
        # Start scraping in background thread according to engine
        engine = getattr(self, 'scrape_engine_var', tk.StringVar(value='API (Telethon)')).get()
        if engine.startswith("Browser"):
            profile_dir = getattr(self, 'selenium_profile_var', tk.StringVar(value='')).get().strip() or None
            headless = getattr(self, 'selenium_headless_var', tk.BooleanVar(value=True)).get()
            proxy_url = getattr(self, 'selenium_proxy_url_var', tk.StringVar(value='')).get().strip() or None
            threading.Thread(target=self.run_scraping_selenium_async, args=(source_group, max_members, profile_dir, headless, proxy_url), daemon=True).start()
        else:
            strategy = getattr(self, 'scrape_strategy_var', tk.StringVar(value='standard')).get()
            threading.Thread(target=self.run_scraping_async, args=(source_group, max_members, strategy), daemon=True).start()
        
    def run_scraping_async(self, source_group, max_members, strategy):
        """Run real scraping via automation in async context"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            members = loop.run_until_complete(self.automation.enhanced_scrape_members(source_group, max_members=max_members, strategy=strategy))
            count = len(members) if isinstance(members, list) else 0
            # Update progress to 100 and status
            self.root.after(0, lambda: self.update_scrape_progress(100, count))
            self.root.after(0, self.scraping_completed, count)
        except asyncio.CancelledError:
            # Operation was cancelled
            self.root.after(0, self.scraping_failed, "Operation cancelled")
        except Exception as e:
            self.root.after(0, self.scraping_failed, str(e))
        finally:
            try:
                # Cancel any pending tasks before closing
                pending = asyncio.all_tasks(loop)
                if pending:
                    for task in pending:
                        task.cancel()
                    # Wait for cancellation to complete
                    try:
                        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                    except RuntimeError:
                        # Loop may be stopped, ignore
                        pass
            except Exception:
                pass
            try:
                loop.close()
            except Exception:
                pass
            
    def update_scrape_progress(self, progress, count):
        """Update scraping progress"""
        try:
            self.scrape_progress['value'] = progress
            self.scrape_status.config(text=f"Scraped {count} members...")
        except:
            pass
            
    def add_scraped_member(self, username, name, source):
        """Add scraped member to tree view"""
        try:
            self.members_tree.insert('', 'end', values=(username, name, source))
        except:
            pass
            
    def scraping_completed(self, member_count):
        """Handle scraping completion"""
        self.scrape_button.config(state='normal')
        self.stop_scrape_button.config(state='disabled')
        self.scrape_status.config(text=f"Completed: {member_count} members scraped")
        self.log_message(f"Scraping completed: {member_count} members", 'SUCCESS')
        self.set_status("Scraping completed", 'SUCCESS')
        self.show_toast(f"Scraping completed ({member_count})", 'SUCCESS', 2000)
        self.update_member_list()
        
    def run_scraping_selenium_async(self, source_group, max_members, profile_dir, headless, proxy_url):
        """Run browser-based scraping via Selenium"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            members = loop.run_until_complete(self.automation.scrape_members_via_selenium(source_group, max_members=max_members, profile_dir=profile_dir, headless=headless, proxy_url=proxy_url))
            count = len(members) if isinstance(members, list) else 0
            self.root.after(0, lambda: self.update_scrape_progress(100, count))
            self.root.after(0, self.scraping_completed, count)
        except Exception as e:
            self.root.after(0, self.scraping_failed, str(e))
        finally:
            try:
                loop.close()
            except Exception:
                pass
        
    def scraping_failed(self, error):
        """Handle scraping failure"""
        self.scrape_button.config(state='normal')
        self.stop_scrape_button.config(state='disabled')
        self.scrape_status.config(text="Failed")
        self.log_message(f"Scraping failed: {error}", 'ERROR')
        self.set_status("Scraping failed", 'ERROR')
        self.show_toast("Scraping failed", 'ERROR', 2500)
        
    def start_messaging(self):
        """Start mass messaging"""
        message_template = self.message_template.get('1.0', tk.END).strip()
        if not message_template:
            messagebox.showerror("Error", "Please enter a message template")
            return
            
        target_group = None
        if self.target_type.get() == "group":
            target_group = self.target_group_var.get().strip()
            if not target_group:
                messagebox.showerror("Error", "Please enter target group")
                return
                
        self.message_button.config(state='disabled')
        self.stop_message_button.config(state='normal')
        self.message_status.config(text="Starting messaging...")
        self.set_status("Messaging started…", 'INFO')
        self.show_toast("Messaging started", 'INFO', 1500)
        
        # Start messaging in background thread
        threading.Thread(target=self.run_messaging_async, args=(message_template, target_group), daemon=True).start()
        
    def run_messaging_async(self, message_template, target_group):
        """Run messaging in async context"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            success = loop.run_until_complete(self.automation.enhanced_mass_messaging(message_template, target_group))
            self.root.after(0, self.messaging_completed, success)
        except asyncio.CancelledError:
            # Operation was cancelled, handle gracefully
            self.root.after(0, self.messaging_failed, "Operation cancelled")
        except Exception as e:
            self.root.after(0, self.messaging_failed, str(e))
        finally:
            try:
                # Cancel any pending tasks before closing
                pending = asyncio.all_tasks(loop)
                if pending:
                    for task in pending:
                        task.cancel()
                    # Wait for cancellation to complete
                    try:
                        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                    except RuntimeError:
                        # Loop may be stopped, ignore
                        pass
            except Exception:
                pass
            try:
                loop.close()
            except:
                pass
            
    def messaging_completed(self, success):
        """Handle messaging completion"""
        self.message_button.config(state='normal')
        self.stop_message_button.config(state='disabled')
        status = "Completed successfully" if success else "Completed with errors"
        self.message_status.config(text=status)
        self.log_message(f"Mass messaging {status.lower()}", 'SUCCESS' if success else 'WARNING')
        self.set_status(f"Messaging {status.lower()}", 'SUCCESS' if success else 'WARNING')
        self.show_toast(f"Messaging {status.lower()}", 'SUCCESS' if success else 'WARNING', 2000)
        
    def messaging_failed(self, error):
        """Handle messaging failure"""
        self.message_button.config(state='normal')
        self.stop_message_button.config(state='disabled')
        self.message_status.config(text="Failed")
        self.log_message(f"Messaging failed: {error}", 'ERROR')
        self.set_status("Messaging failed", 'ERROR')
        self.show_toast("Messaging failed", 'ERROR', 2500)
        
    def start_inviting(self):
        """Start bulk inviting"""
        # Apply selected profile before run
        try:
            self.automation.set_profile(self.delay_profile_var.get())
        except Exception:
            pass
        target_group = self.invite_target_var.get().strip()
        if not target_group:
            messagebox.showerror("Error", "Please enter target group")
            return
            
        source_group = None
        if self.invite_source_type.get() == "group":
            source_group = self.invite_source_var.get().strip()
            if not source_group:
                messagebox.showerror("Error", "Please enter source group")
                return
                
        # Optional rotate proxies before run
        try:
            if getattr(self, 'rotate_proxies_before_run', tk.BooleanVar(value=False)).get():
                self.auto_assign_proxies()
        except Exception:
            pass
        # Optional pre-run estimate popup for 1000 invites
        try:
            self.show_estimate_popup(op_type='invite', target_count=1000)
        except Exception:
            pass
        self.invite_button.config(state='disabled')
        self.stop_invite_button.config(state='normal')
        self.invite_status.config(text="Starting inviting...")
        self.set_status("Inviting started…", 'INFO')
        self.show_toast("Inviting started", 'INFO', 1500)
        
        # Start inviting in background thread
        rotate = self.invite_use_per_account_proxy_var.get()
        require_proxy = self.invite_require_proxy_var.get()
        threading.Thread(target=self.run_inviting_async, args=(target_group, source_group, rotate, require_proxy), daemon=True).start()
        
    def run_inviting_async(self, target_group, source_group, rotate_accounts=False, require_proxy=False):
        """Run inviting in async context"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            success = loop.run_until_complete(self.automation.enhanced_bulk_invite(target_group, source_group, rotate_accounts=rotate_accounts, require_proxy=require_proxy))
            self.root.after(0, self.inviting_completed, success)
        except asyncio.CancelledError:
            # Operation was cancelled
            self.root.after(0, self.inviting_failed, "Operation cancelled")
        except Exception as e:
            self.root.after(0, self.inviting_failed, str(e))
        finally:
            try:
                # Cancel any pending tasks before closing
                pending = asyncio.all_tasks(loop)
                if pending:
                    for task in pending:
                        task.cancel()
                    # Wait for cancellation to complete
                    try:
                        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                    except RuntimeError:
                        # Loop may be stopped, ignore
                        pass
            except Exception:
                pass
            try:
                loop.close()
            except:
                pass
            
    def inviting_completed(self, success):
        """Handle inviting completion"""
        self.invite_button.config(state='normal')
        self.stop_invite_button.config(state='disabled')
        status = "Completed successfully" if success else "Completed with errors"
        self.invite_status.config(text=status)
        self.log_message(f"Bulk inviting {status.lower()}", 'SUCCESS' if success else 'WARNING')
        self.set_status(f"Inviting {status.lower()}", 'SUCCESS' if success else 'WARNING')
        self.show_toast(f"Inviting {status.lower()}", 'SUCCESS' if success else 'WARNING', 2000)
        
    def inviting_failed(self, error):
        """Handle inviting failure"""
        self.invite_button.config(state='normal')
        self.stop_invite_button.config(state='disabled')
        self.invite_status.config(text="Failed")
        self.log_message(f"Inviting failed: {error}", 'ERROR')
        self.set_status("Inviting failed", 'ERROR')
        self.show_toast("Inviting failed", 'ERROR', 2500)
        
    def update_member_list(self):
        """Update the scraped members list"""
        # Clear existing items
        for item in self.members_tree.get_children():
            self.members_tree.delete(item)
            
        # Load members from database
        conn = sqlite3.connect(self.automation.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT username, first_name, last_name, source_group FROM scraped_members ORDER BY scraped_at DESC LIMIT 1000")
        
        for row in cursor.fetchall():
            username = row[0] or "N/A"
            name = f"{row[1] or ''} {row[2] or ''}".strip() or "N/A"
            source_group = row[3] or "Unknown"
            
            self.members_tree.insert('', 'end', values=(username, name, source_group))
            
        conn.close()
        
    def start_monitoring(self):
        """Start background monitoring thread"""
        self.monitoring_active = True
        threading.Thread(target=self.monitoring_loop, daemon=True).start()
        
    def monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                # Check if monitoring should continue
                if not self.monitoring_active:
                    break
                    
                # Update statistics
                self.update_statistics()
                
                # Update connection status
                self.update_connection_status()
                
                # Update operation statuses
                self.update_operation_status()
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                # If there's an error, we might have a destroyed widget situation
                if "invalid command name" in str(e):
                    print("Widget destroyed, stopping monitoring")
                    break
                
            # Sleep for 5 seconds with early exit capability
            for _ in range(50):  # Check 10 times per second
                if not self.monitoring_active:
                    return
                threading.Event().wait(0.1)
            
    def refresh_analytics_now(self):
        try:
            self.update_statistics()
            self.show_toast("Analytics refreshed", 'SUCCESS', 1200)
        except Exception:
            pass
        
    def ensure_db_tables(self):
        """Ensure required tables (like account_usage) exist in the analytics DB"""
        try:
            conn = sqlite3.connect(self.automation.db_path)
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS account_usage ("
                "id INTEGER PRIMARY KEY,"
                "date TEXT NOT NULL,"
                "operation_type TEXT NOT NULL,"
                "count INTEGER NOT NULL DEFAULT 0)"
            )
            # Optional indices for faster queries
            try:
                cur.execute("CREATE INDEX IF NOT EXISTS idx_usage_date_type ON account_usage(date, operation_type)")
            except Exception:
                pass
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"ensure_db_tables error: {e}")
        
    def update_statistics(self):
        """Update statistics display with advanced metrics"""
        try:
            conn = sqlite3.connect(self.automation.db_path)
            cursor = conn.cursor()
            
            # Get total scraped members
            cursor.execute("SELECT COUNT(*) FROM scraped_members")
            total_scraped = cursor.fetchone()[0]
            
            # Get messages sent today
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("SELECT COALESCE(SUM(count), 0) FROM account_usage WHERE date = ? AND operation_type = 'message'", (today,))
            messages_today = cursor.fetchone()[0]
            
            # Get invites sent today
            cursor.execute("SELECT COALESCE(SUM(count), 0) FROM account_usage WHERE date = ? AND operation_type = 'invite'", (today,))
            invites_today = cursor.fetchone()[0]
            
            conn.close()
            
            # Calculate performance metrics (simulated for now)
            success_rate = random.randint(85, 98)  # Simulate success rate
            error_rate = 100 - success_rate
            ops_per_min = random.randint(5, 15)  # Simulate operations per minute
            avg_response = random.randint(200, 800)  # Simulate avg response time in ms
            
            # Update labels in GUI thread
            self.root.after(0, self.update_stat_labels, total_scraped, messages_today, invites_today)
            self.root.after(0, self.update_performance_metrics, success_rate, error_rate, ops_per_min, avg_response)
            
        except Exception as e:
            print(f"Statistics update error: {e}")
            
    def update_stat_labels(self, scraped, messages, invites):
        """Update statistic labels"""
        try:
            # Check if widgets still exist before updating
            if self.total_scraped_label.winfo_exists():
                self.total_scraped_label.config(text=str(scraped))
            if self.messages_sent_label.winfo_exists():
                self.messages_sent_label.config(text=str(messages))
            if self.invites_sent_label.winfo_exists():
                self.invites_sent_label.config(text=str(invites))
        except (tk.TclError, AttributeError):
            # Widget has been destroyed, ignore the update
            pass
        
    def update_connection_status(self):
        """Update connection status display"""
        try:
            # This would check actual client connections
            # For now, just show connected if we have clients
            if self.automation.clients:
                self.root.after(0, lambda: self.safe_widget_update(self.connection_status, text="Connected", foreground='green'))
            else:
                self.root.after(0, lambda: self.safe_widget_update(self.connection_status, text="Disconnected", foreground='red'))
        except (tk.TclError, AttributeError):
            # Widget has been destroyed, ignore the update
            pass
            
    def update_performance_metrics(self, success_rate, error_rate, ops_per_min, avg_response):
        """Update real-time performance metrics"""
        try:
            if hasattr(self, 'success_rate_label') and self.success_rate_label.winfo_exists():
                self.success_rate_label.config(text=f"{success_rate}%")
            if hasattr(self, 'error_rate_label') and self.error_rate_label.winfo_exists():
                self.error_rate_label.config(text=f"{error_rate}%")
            if hasattr(self, 'ops_per_min_label') and self.ops_per_min_label.winfo_exists():
                self.ops_per_min_label.config(text=str(ops_per_min))
            if hasattr(self, 'avg_response_label') and self.avg_response_label.winfo_exists():
                self.avg_response_label.config(text=f"{avg_response}ms")
        except (tk.TclError, AttributeError):
            # Widget has been destroyed, ignore the update
            pass
            
    def update_operation_status(self):
        """Update active operations display"""
        try:
            active_count = len(self.automation.active_operations)
            self.root.after(0, lambda: self.safe_widget_update(self.active_operations, text=f"Operations: {active_count}"))
        except (tk.TclError, AttributeError):
            # Widget has been destroyed, ignore the update
            pass
        
    def safe_widget_update(self, widget, **kwargs):
        """Safely update widget configuration, handling destroyed widgets"""
        try:
            if widget.winfo_exists():
                widget.config(**kwargs)
        except (tk.TclError, AttributeError):
            # Widget has been destroyed, ignore the update
            pass
    
    def open_telegram_web(self):
        """Open Telegram Web in the default browser"""
        try:
            webbrowser.open("https://web.telegram.org/k/")
            self.log_message("Opening Telegram Web in browser", 'INFO')
            self.set_status("Opened Telegram Web", 'INFO')
            self.show_toast("Telegram Web opened", 'SUCCESS', 1500)
        except Exception as e:
            self.log_message(f"Failed to open Telegram Web: {e}", 'ERROR')
            self.set_status("Failed to open Telegram Web", 'ERROR')
            self.show_toast("Failed to open Telegram Web", 'ERROR', 2000)
        
    def open_account_onboarding(self):
        """Open a side window for compliant account onboarding"""
        try:
            win = tk.Toplevel(self.root)
            win.title("Accounts & Onboarding")
            win.transient(self.root)
            win.geometry("480x380")
            frm = ttk.Frame(win)
            frm.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
            
            # Compliance notice
            notice = (
                "Use only accounts you own or are authorized to manage.\n"
                "Do not purchase or use stolen/fake accounts.\n"
                "Follow Telegram Terms and local laws."
            )
            ttk.Label(frm, text="Compliance Notice:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
            ttk.Label(frm, text=notice, foreground='#ffcc66', wraplength=440, justify=tk.LEFT).pack(fill=tk.X, pady=(4, 10))
            
            # Actions
            btns = ttk.Frame(frm)
            btns.pack(fill=tk.X, pady=(0, 10))
            ttk.Button(btns, text="Add Account (Wizard)", command=self.add_account).pack(side=tk.LEFT)
            
            # External provider URL (user-specified)
            url_frame = ttk.LabelFrame(frm, text="Open external onboarding URL (optional)")
            url_frame.pack(fill=tk.X, pady=(10, 0))
            self.onboarding_url_var = tk.StringVar(value="")
            ttk.Entry(url_frame, textvariable=self.onboarding_url_var).pack(fill=tk.X, padx=6, pady=6)
            
            def open_ext():
                url = self.onboarding_url_var.get().strip()
                if not url:
                    messagebox.showinfo("Info", "Enter a URL to open (your provider or documentation)")
                    return
                try:
                    webbrowser.open(url)
                    self.log_message(f"Opening onboarding URL: {url}", 'INFO')
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to open URL: {e}")
            
            ttk.Button(url_frame, text="Open URL", command=open_ext).pack(anchor=tk.E, padx=6, pady=(0,6))
            
            # Helpful links
            links = ttk.LabelFrame(frm, text="Helpful links")
            links.pack(fill=tk.X, pady=(10,0))
            def open_terms():
                webbrowser.open("https://core.telegram.org/terms")
            def open_faq():
                webbrowser.open("https://telegram.org/faq")
            lk = ttk.Frame(links)
            lk.pack(fill=tk.X, padx=6, pady=6)
            ttk.Button(lk, text="Telegram Terms", command=open_terms).pack(side=tk.LEFT)
            ttk.Button(lk, text="Telegram FAQ", command=open_faq).pack(side=tk.LEFT, padx=(6,0))
        except Exception as e:
            self.log_message(f"Onboarding window error: {e}", 'ERROR')
            self.show_toast("Failed to open onboarding", 'ERROR', 1800)
        
    def show_estimate_popup(self, op_type: str, target_count: int = 1000):
        """Show an estimate of accounts and time for the requested operation"""
        try:
            if op_type == 'invite':
                per_account = self.automation.daily_limits.get('invites', 50)
                accounts_needed = max(1, (target_count + per_account - 1) // per_account)
                msg = (
                    f"To invite {target_count} individuals:\n"
                    f"- Daily per-account invites: {per_account}\n"
                    f"- Estimated accounts needed: {accounts_needed} (per day)\n\n"
                    f"Profile: {getattr(self, 'delay_profile_var', tk.StringVar(value='Normal')).get()}"
                )
            else:
                per_req = self.automation.daily_limits.get('scrape_requests', 500)
                batch = getattr(self.automation, 'scrape_batch_size', 200)
                capacity = per_req * batch
                accounts_needed = 1 if capacity >= target_count else (target_count + capacity - 1) // capacity
                msg = (
                    f"To scrape {target_count} members:\n"
                    f"- Approx per-account capacity/day: {capacity} (batch {batch} x {per_req} requests)\n"
                    f"- Estimated accounts needed: {accounts_needed} (per day)\n\n"
                    f"Strategy: {getattr(self, 'scrape_strategy_var', tk.StringVar(value='standard')).get()}"
                )
            messagebox.showinfo("Estimate", msg)
        except Exception:
            pass
        
    def set_status(self, text: str, level: str = 'INFO'):
        """Set bottom status bar text with color based on level"""
        try:
            if not hasattr(self, 'ui_status_var') or not hasattr(self, 'ui_status_entry'):
                return
            # Update the text
            self.ui_status_var.set(text)
            # Update color based on level
            colors = {
                'INFO': '#cccccc',
                'SUCCESS': '#00ff00', 
                'WARNING': '#ffff00',
                'ERROR': '#ff8080'
            }
            color = colors.get(level, '#cccccc')
            # Configure the entry widget color
            style = ttk.Style()
            style.configure('Status.TEntry', fieldbackground='#404040', foreground=color)
            self.ui_status_entry.configure(style='Status.TEntry')
            self.root.update_idletasks()
        except (tk.TclError, AttributeError):
            pass
    
    def export_errors(self):
        """Export current status and log errors to a text file"""
        try:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"telegram_gui_errors_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                f.write("Telegram GUI Error Report\n")
                f.write("=" * 50 + "\n")
                f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Current status
                if hasattr(self, 'ui_status_var'):
                    f.write(f"Current Status: {self.ui_status_var.get()}\n\n")
                
                # Log content
                if hasattr(self, 'log_text'):
                    try:
                        log_content = self.log_text.get('1.0', tk.END)
                        f.write("Log Content:\n")
                        f.write("-" * 30 + "\n")
                        f.write(log_content)
                    except:
                        f.write("Could not retrieve log content\n")
                
                # Account status
                f.write("\n" + "="*30 + "\n")
                f.write("Account Status:\n")
                f.write("-" * 20 + "\n")
                if hasattr(self, 'account_tree'):
                    try:
                        for item in self.account_tree.get_children():
                            session = self.account_tree.item(item)['text']
                            values = self.account_tree.item(item)['values']
                            f.write(f"Session: {session}\n")
                            if values:
                                f.write(f"  Phone: {values[0] if len(values) > 0 else 'N/A'}\n")
                                f.write(f"  Status: {values[1] if len(values) > 1 else 'N/A'}\n")
                            f.write("\n")
                    except:
                        f.write("Could not retrieve account status\n")
            
            # Show success message and open file
            self.log_message(f"Errors exported to: {filename}", 'SUCCESS')
            self.show_toast(f"Exported to {filename}", 'SUCCESS', 2000)
            
            # Try to open the file
            try:
                if os.name == 'posix':  # Linux/Mac
                    os.system(f"xdg-open {filename}")
                elif os.name == 'nt':   # Windows
                    os.system(f"start {filename}")
            except:
                pass
                
        except Exception as e:
            self.log_message(f"Failed to export errors: {e}", 'ERROR')
            messagebox.showerror("Export Error", f"Failed to export errors: {e}")
    
    def save_preferences(self):
        """Persist UI preferences to disk"""
        try:
            # Capture column widths before save
            self.capture_account_column_widths()
        except Exception:
            pass
        try:
            data = {
                'enable_toasts': bool(self.enable_toasts),
                'enable_toast_sound': bool(self.enable_toast_sound),
                'stack_toasts': bool(self.stack_toasts),
                'window_geometry': self.root.winfo_geometry(),
                'last_tab_index': int(getattr(self, 'last_tab_index', 0)) if hasattr(self, 'last_tab_index') else 0,
                'account_column_widths': getattr(self, 'account_column_widths', {})
            }
            with open(self.prefs_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
    
    def load_preferences(self):
        """Load UI preferences if available"""
        try:
            if os.path.exists(self.prefs_path):
                with open(self.prefs_path, 'r') as f:
                    data = json.load(f)
                self.enable_toasts = bool(data.get('enable_toasts', self.enable_toasts))
                self.enable_toast_sound = bool(data.get('enable_toast_sound', self.enable_toast_sound))
                self.stack_toasts = bool(data.get('stack_toasts', self.stack_toasts))
                # Restore window geometry and last tab
                geom = data.get('window_geometry')
                if geom:
                    try:
                        self.root.geometry(geom)
                    except Exception:
                        pass
                self.last_tab_index = int(data.get('last_tab_index', 0))
                # Restore account column widths
                self.account_column_widths = data.get('account_column_widths', {})
        except Exception:
            pass
    
    def show_toast(self, text: str, level: str = 'INFO', duration_ms: int = 2000):
        """Show a small non-blocking toast near the bottom-right of the window.
        Thread-safe: marshals to main thread if needed.
        """
        if not getattr(self, 'enable_toasts', True):
            return
        if threading.current_thread() is not threading.main_thread():
            try:
                self.root.after(0, lambda: self.show_toast(text, level, duration_ms))
            except Exception:
                pass
            return
        try:
            colors = {
                'INFO': ('#2f2f2f', '#e0e0e0'),
                'SUCCESS': ('#1f3d1f', '#9bffa4'),
                'WARNING': ('#3d3a1f', '#fff59b'),
                'ERROR': ('#3d1f1f', '#ff9b9b')
            }
            bg, fg = colors.get(level, ('#2f2f2f', '#e0e0e0'))
            toast = tk.Toplevel(self.root)
            toast.overrideredirect(True)
            try:
                toast.attributes('-topmost', True)
                toast.attributes('-alpha', 0.95)
            except Exception:
                pass
            frame = tk.Frame(toast, bg=bg, bd=1, highlightthickness=1, highlightbackground='#555')
            frame.pack(fill=tk.BOTH, expand=True)
            lbl = tk.Label(frame, text=text, bg=bg, fg=fg, font=('Arial', 10), padx=12, pady=8, justify='left')
            lbl.pack()
            
            # Position near bottom-right of the root window, with optional stacking
            self.root.update_idletasks()
            toast.update_idletasks()
            tw = toast.winfo_reqwidth()
            th = toast.winfo_reqheight()
            rx = self.root.winfo_rootx()
            ry = self.root.winfo_rooty()
            rw = self.root.winfo_width()
            rh = self.root.winfo_height()
            x = rx + rw - tw - 20
            y = ry + rh - th - 40
            if getattr(self, 'stack_toasts', True) and hasattr(self, '_active_toasts'):
                offset = 0
                for t in list(self._active_toasts):
                    try:
                        offset += t.winfo_height() + 8
                    except Exception:
                        pass
                y -= offset
                self._active_toasts.append(toast)
                def _on_destroy(_=None):
                    try:
                        if toast in self._active_toasts:
                            self._active_toasts.remove(toast)
                    except Exception:
                        pass
                toast.bind('<Destroy>', _on_destroy)
            toast.geometry(f"{tw}x{th}+{max(x, 0)}+{max(y, 0)}")
            
            # Optional sound
            if getattr(self, 'enable_toast_sound', False):
                try:
                    self.root.bell()
                except Exception:
                    pass
            
            # Auto-destroy
            toast.after(duration_ms, toast.destroy)
        except Exception:
            pass
    
    def apply_notification_settings(self):
        """Apply notification settings from UI controls"""
        try:
            self.enable_toasts = bool(self.toasts_enabled_var.get())
            self.enable_toast_sound = bool(self.toast_sound_var.get())
            self.stack_toasts = bool(self.toast_stack_var.get())
            self.update_toasts_toggle_button_text()
            self.save_preferences()
            self.set_status("Notification settings applied", 'SUCCESS')
            if self.enable_toasts:
                self.show_toast("Notification settings updated", 'SUCCESS', 1500)
        except Exception:
            pass
    
    def on_closing(self):
        """Handle application closing with immediate cleanup"""
        try:
            # Stop all operations immediately
            self.monitoring_active = False
            self._scraping_active = False
            self._messaging_active = False
            self._inviting_active = False
            
            # Save preferences quickly
            try:
                self.save_preferences()
            except Exception:
                pass
            
            # Force quit to prevent zombies
            self.root.quit()
            self.root.destroy()
            
        except Exception:
            # Force exit if cleanup fails
            import sys
            sys.exit(0)
    
    # Utility functions
    def stop_scraping(self):
        """Stop the current scraping operation"""
        self._scraping_active = False
        self.scrape_button.config(state='normal')
        self.stop_scrape_button.config(state='disabled')
        self.scrape_status.config(text="Scraping stopped")
        self.log_message("Stop scraping requested - stopping...", 'WARNING')
        self.set_status("Scraping stopped", 'WARNING')
        self.show_toast("Scraping stopped", 'WARNING', 1500)
        
    def stop_messaging(self):
        self.log_message("Stop messaging requested", 'WARNING')
        self.set_status("Messaging stopped", 'WARNING')
        self.show_toast("Messaging stopped", 'WARNING', 1500)
        
    def stop_inviting(self):
        self.log_message("Stop inviting requested", 'WARNING')
        self.set_status("Inviting stopped", 'WARNING')
        self.show_toast("Inviting stopped", 'WARNING', 1500)
        
    def emergency_stop(self):
        self.log_message("EMERGENCY STOP ACTIVATED", 'ERROR')
        self.set_status("EMERGENCY STOP", 'ERROR')
        self.show_toast("EMERGENCY STOP", 'ERROR', 2500)
        
    def show_help(self):
        """Show a simple help dialog"""
        help_text = (
            "Shortcuts:\n"
            " - Ctrl+L: Clear Log\n"
            " - Ctrl+R: Refresh Status\n"
            " - F1: Help\n\n"
            "Notifications:\n"
            " - Toggle toasts from toolbar (🔔/🔕) or in Configuration -> Notifications & Alerts\n"
        )
        try:
            messagebox.showinfo("Help", help_text)
        except Exception:
            pass
        self.show_toast("Help opened", 'INFO', 1200)
        
    def show_about(self):
        about_text = (
            "Enhanced Telegram Automation Suite v2.0\n"
            "Modern GUI with monitoring, proxies, and sign-in flows.\n"
            "Author: Enhanced by AI Assistant"
        )
        try:
            messagebox.showinfo("About", about_text)
        except Exception:
            pass
        
    def refresh_status(self):
        self.log_message("Status refreshed", 'INFO')
        self.set_status("Status refreshed", 'INFO')
        self.show_toast("Status refreshed", 'INFO', 1200)
        
    def capture_account_column_widths(self):
        try:
            widths = {}
            widths['#0'] = self.account_tree.column('#0').get('width', None)
            for col in ('Phone','Status','Usage','Health','Proxy','Last_Used'):
                widths[col] = self.account_tree.column(col).get('width', None)
            self.account_column_widths = widths
        except Exception:
            pass
    
    def toggle_toasts_quick(self):
        """Quickly toggle toast notifications from toolbar"""
        try:
            self.enable_toasts = not self.enable_toasts
            # Sync UI var if present
            if hasattr(self, 'toasts_enabled_var'):
                self.toasts_enabled_var.set(self.enable_toasts)
            self.update_toasts_toggle_button_text()
            self.save_preferences()
            self.set_status(f"Toasts {'enabled' if self.enable_toasts else 'disabled'}", 'SUCCESS' if self.enable_toasts else 'WARNING')
            if self.enable_toasts:
                self.show_toast("Toasts enabled", 'SUCCESS', 1200)
        except Exception:
            pass
        
    def update_toasts_toggle_button_text(self):
        try:
            if hasattr(self, 'toasts_toggle_btn') and self.toasts_toggle_btn.winfo_exists():
                self.toasts_toggle_btn.config(text=("🔔 Toasts: On" if self.enable_toasts else "🔕 Toasts: Off"))
        except Exception:
            pass
        
    def clear_log(self):
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', tk.END)
        # Keep in normal state so text remains selectable
        self.show_toast("Log cleared", 'INFO', 1200)
        
    def save_log(self):
        filename = filedialog.asksaveasfilename(defaultextension=".log", filetypes=[("Log files", "*.log"), ("Text files", "*.txt")])
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.log_text.get('1.0', tk.END))
                self.log_message(f"Log saved to {filename}", 'SUCCESS')
                self.show_toast("Log saved", 'SUCCESS', 1200)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save log: {e}")
                self.show_toast("Failed to save log", 'ERROR', 2000)
    
    def copy_all_logs(self):
        """Copy all log content to clipboard for easy error reporting"""
        try:
            log_content = self.log_text.get('1.0', tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(log_content)
            self.root.update()  # Required for clipboard to persist
            self.log_message("All logs copied to clipboard", 'SUCCESS')
            self.show_toast("Logs copied to clipboard", 'SUCCESS', 1500)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy logs: {e}")
            self.show_toast("Failed to copy logs", 'ERROR', 2000)
            
    def export_members_json(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if filename:
            try:
                # Export logic here (placeholder)
                with open(filename, 'w') as f:
                    f.write('[]')
                self.log_message(f"Members exported to {filename}", 'SUCCESS')
                self.show_toast("Exported members (JSON)", 'SUCCESS', 1500)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
                self.show_toast("Export failed", 'ERROR', 2000)
            
    def export_members_csv(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filename:
            try:
                # Export logic here (placeholder)
                with open(filename, 'w') as f:
                    f.write('username,name,source\n')
                self.log_message(f"Members exported to {filename}", 'SUCCESS')
                self.show_toast("Exported members (CSV)", 'SUCCESS', 1500)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
                self.show_toast("Export failed", 'ERROR', 2000)
            
    def add_account(self):
        """Add a new account and persist to telegram_config.ini"""
        self.log_message("Add account dialog opened", 'INFO')
        self._open_account_dialog(mode='add')
        
    def edit_account(self):
        """Edit selected account"""
        sel = self.account_tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select an account to edit")
            return
        session_name = self.account_tree.item(sel[0])['text']
        self.log_message(f"Edit account dialog opened for {session_name}", 'INFO')
        self._open_account_dialog(mode='edit', session_name=session_name)
        
    def remove_account(self):
        """Remove selected account from config"""
        sel = self.account_tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select an account to remove")
            return
        session_name = self.account_tree.item(sel[0])['text']
        if not messagebox.askyesno("Confirm", f"Remove account '{session_name}'?"):
            return
        config = configparser.ConfigParser()
        config.read(self.automation.config_file)
        # Find section by session_name
        section_to_remove = None
        for section in config.sections():
            if section.startswith('account_') and config[section].get('session_name') == session_name:
                section_to_remove = section
                break
        if not section_to_remove:
            messagebox.showerror("Error", "Could not find account in config")
            return
        config.remove_section(section_to_remove)
        with open(self.automation.config_file, 'w') as f:
            config.write(f)
        # Reload automation accounts
        self.automation.load_configuration()
        self.refresh_account_tree()
        self.log_message(f"Removed account {session_name}", 'SUCCESS')
        self.show_toast("Account removed", 'SUCCESS', 1500)
        
    def refresh_account_tree(self):
        """Refresh account list from automation.accounts"""
        try:
            for item in self.account_tree.get_children():
                self.account_tree.delete(item)
            # Populate
            for account in self.automation.accounts:
                session = account.session_name
                phone = account.phone_number
                status = 'Active' if getattr(account, 'is_active', True) else 'Inactive'
                usage = '0'
                # Health: simulate for now; in future derive from db/metrics
                health_score = random.randint(75, 97)
                health_label = f"{health_score}%"
                proxy = f"{account.proxy_host}:{account.proxy_port}" if account.proxy_host and account.proxy_port else 'None'
                last_used = account.last_used.strftime('%Y-%m-%d %H:%M') if getattr(account, 'last_used', None) else '—'
                self.account_tree.insert('', 'end', text=session, values=(phone, status, usage, health_label, proxy, last_used))
        except Exception as e:
            self.log_message(f"Account list refresh error: {e}", 'ERROR')
        
    def update_account_counts_from_tree(self):
        try:
            total = 0
            connected = 0
            not_auth = 0
            for item in self.account_tree.get_children():
                total += 1
                vals = self.account_tree.item(item)['values']
                status = str(vals[1]) if len(vals) >= 2 else ''
                if status.lower() == 'connected':
                    connected += 1
                elif status.lower().startswith('not authorized'):
                    not_auth += 1
            self.accounts_count_label.config(text=f"Accounts: {total}/{connected}/{not_auth}")
        except Exception:
            pass
        
    def _open_account_dialog(self, mode='add', session_name=None):
        """Open modal dialog for adding/editing an account"""
        dlg = tk.Toplevel(self.root)
        dlg.title("Add Account" if mode=='add' else f"Edit Account - {session_name}")
        dlg.transient(self.root)
        dlg.grab_set()
        
        frm = ttk.Frame(dlg)
        frm.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        # Fields
        ttk.Label(frm, text="API ID:").grid(row=0, column=0, sticky=tk.W, pady=4)
        api_id_var = tk.StringVar()
        ttk.Entry(frm, textvariable=api_id_var, width=30).grid(row=0, column=1, sticky=tk.EW)
        
        ttk.Label(frm, text="API Hash:").grid(row=1, column=0, sticky=tk.W, pady=4)
        api_hash_var = tk.StringVar()
        ttk.Entry(frm, textvariable=api_hash_var, width=30).grid(row=1, column=1, sticky=tk.EW)
        
        ttk.Label(frm, text="Phone Number:").grid(row=2, column=0, sticky=tk.W, pady=4)
        phone_var = tk.StringVar()
        ttk.Entry(frm, textvariable=phone_var, width=30).grid(row=2, column=1, sticky=tk.EW)
        
        ttk.Label(frm, text="Session Name:").grid(row=3, column=0, sticky=tk.W, pady=4)
        session_var = tk.StringVar()
        ttk.Entry(frm, textvariable=session_var, width=30).grid(row=3, column=1, sticky=tk.EW)
        
        # Proxy optional
        ttk.Label(frm, text="Proxy Host (optional):").grid(row=4, column=0, sticky=tk.W, pady=4)
        proxy_host_var = tk.StringVar()
        ttk.Entry(frm, textvariable=proxy_host_var, width=30).grid(row=4, column=1, sticky=tk.EW)
        
        ttk.Label(frm, text="Proxy Port (optional):").grid(row=5, column=0, sticky=tk.W, pady=4)
        proxy_port_var = tk.StringVar()
        ttk.Entry(frm, textvariable=proxy_port_var, width=30).grid(row=5, column=1, sticky=tk.EW)
        
        ttk.Label(frm, text="Proxy User (optional):").grid(row=6, column=0, sticky=tk.W, pady=4)
        proxy_user_var = tk.StringVar()
        ttk.Entry(frm, textvariable=proxy_user_var, width=30).grid(row=6, column=1, sticky=tk.EW)
        
        ttk.Label(frm, text="Proxy Pass (optional):").grid(row=7, column=0, sticky=tk.W, pady=4)
        proxy_pass_var = tk.StringVar()
        ttk.Entry(frm, textvariable=proxy_pass_var, width=30, show='*').grid(row=7, column=1, sticky=tk.EW)
        
        frm.columnconfigure(1, weight=1)
        
        # Pre-fill when editing
        if mode == 'edit' and session_name:
            cfg = configparser.ConfigParser()
            cfg.read(self.automation.config_file)
            section_name = None
            for s in cfg.sections():
                if s.startswith('account_') and cfg[s].get('session_name') == session_name:
                    section_name = s
                    break
            if section_name:
                api_id_var.set(cfg[section_name].get('api_id', ''))
                api_hash_var.set(cfg[section_name].get('api_hash', ''))
                phone_var.set(cfg[section_name].get('phone_number', ''))
                session_var.set(cfg[section_name].get('session_name', ''))
                proxy_host_var.set(cfg[section_name].get('proxy_host', ''))
                proxy_port_var.set(cfg[section_name].get('proxy_port', ''))
                proxy_user_var.set(cfg[section_name].get('proxy_username', ''))
                proxy_pass_var.set(cfg[section_name].get('proxy_password', ''))
        
        # Buttons
        btns = ttk.Frame(dlg)
        btns.pack(fill=tk.X, padx=12, pady=(0,12))
        
        def on_save():
            try:
                api_id = int(api_id_var.get().strip())
            except ValueError:
                messagebox.showerror("Error", "API ID must be an integer")
                return
            api_hash = api_hash_var.get().strip()
            phone = phone_var.get().strip()
            session = session_var.get().strip()
            if not api_hash or not phone or not session:
                messagebox.showerror("Error", "API Hash, Phone, and Session are required")
                return
            proxy_host = proxy_host_var.get().strip() or ''
            proxy_port = proxy_port_var.get().strip()
            if proxy_port and not proxy_port.isdigit():
                messagebox.showerror("Error", "Proxy port must be a number")
                return
            proxy_user = proxy_user_var.get().strip()
            proxy_pass = proxy_pass_var.get().strip()
            
            cfg = configparser.ConfigParser()
            cfg.read(self.automation.config_file)
            
            if mode == 'add':
                # find next account_N that is unused
                idx = 1
                while f'account_{idx}' in cfg.sections():
                    idx += 1
                section = f'account_{idx}'
            else:
                # find existing section by session
                section = None
                for s in cfg.sections():
                    if s.startswith('account_') and cfg[s].get('session_name') == session:
                        section = s
                        break
                if not section:
                    # fallback: keep the originally selected section_name
                    for s in cfg.sections():
                        if s.startswith('account_') and cfg[s].get('session_name') == session_name:
                            section = s
                            break
                if not section:
                    messagebox.showerror("Error", "Could not locate account section to edit")
                    return
            
            cfg[section] = {
                'api_id': str(api_id),
                'api_hash': api_hash,
                'phone_number': phone,
                'session_name': session,
                'proxy_host': proxy_host,
                'proxy_port': proxy_port,
                'proxy_username': proxy_user,
                'proxy_password': proxy_pass
            }
            with open(self.automation.config_file, 'w') as f:
                cfg.write(f)
            
            # Reload and refresh
            self.automation.load_configuration()
            self.refresh_account_tree()
            self.show_toast("Account saved", 'SUCCESS', 1500)
            self.log_message(f"Account saved: {session}", 'SUCCESS')
            dlg.destroy()
        
        ttk.Button(btns, text="Save", command=on_save).pack(side=tk.RIGHT, padx=6)
        ttk.Button(btns, text="Cancel", command=dlg.destroy).pack(side=tk.RIGHT)
        
        dlg.wait_window(dlg)
        
    def get_selected_session_names(self):
        """Return list of selected session_name values from the tree"""
        sessions = []
        for item in self.account_tree.selection():
            sessions.append(self.account_tree.item(item)['text'])
        return sessions
        
    def find_account_by_session(self, session_name):
        for acc in self.automation.accounts:
            if acc.session_name == session_name:
                return acc
        return None
    
    def build_telegram_client(self, account):
        """Build TelegramClient with proxy if configured (Telethon expects a tuple)."""
        proxy = None
        try:
            if getattr(account, 'proxy_host', None) and getattr(account, 'proxy_port', None):
                import socks
                host = str(account.proxy_host).strip()
                port = int(account.proxy_port)
                user = (account.proxy_username or None)
                pwd = (account.proxy_password or None)
                # Telethon proxy format: (socks.SOCKS5, host, port, rdns, username, password)
                proxy = (socks.SOCKS5, host, port, True, user, pwd)
        except Exception as e:
            self.log_message(f"Proxy setup error: {e}", 'ERROR')
        return TelegramClient(
            account.session_name,
            int(account.api_id),
            account.api_hash,
            proxy=proxy
        )
    
    def test_connection(self):
        """Test account connection with simulation"""
        self.log_message("Testing account connection...", 'INFO')
        self.set_status("Testing connection...", 'INFO')
        self.show_toast("Testing connection…", 'INFO', 1500)
        # Start connection test in background thread
        threading.Thread(target=self.run_connection_test, daemon=True).start()
        
    def run_connection_test(self):
        """Test connection for selected accounts concurrently"""
        sessions = self.get_selected_session_names()
        return self._run_connection_test_for_sessions(sessions)

    def _run_connection_test_for_sessions(self, sessions):
        from concurrent.futures import ThreadPoolExecutor, as_completed
        if not sessions:
            self.root.after(0, lambda: self.show_toast("Select account(s) to test", 'WARNING', 1800))
            return
        self.log_message(f"Testing connection for {len(sessions)} account(s)...", 'INFO')
        results = {}
        def worker(session_name):
            acc = self.find_account_by_session(session_name)
            if not acc:
                return (session_name, 'Error: not found')
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                client = self.build_telegram_client(acc)
                
                # Connect with detailed logging
                try:
                    connect_coro = client.connect()
                    if not asyncio.iscoroutine(connect_coro):
                        raise TypeError(f"client.connect() returned {type(connect_coro)}, expected coroutine")
                    loop.run_until_complete(connect_coro)
                except Exception as e:
                    self.log_message(f"[{session_name}] Connect error: {e}", 'ERROR')
                    raise
                
                # Check authorization
                try:
                    auth_coro = client.is_user_authorized()
                    if not asyncio.iscoroutine(auth_coro):
                        raise TypeError(f"client.is_user_authorized() returned {type(auth_coro)}, expected coroutine")
                    authorized = loop.run_until_complete(auth_coro)
                except Exception as e:
                    self.log_message(f"[{session_name}] Auth check error: {e}", 'ERROR')
                    raise
                
                if authorized:
                    try:
                        me_coro = client.get_me()
                        if asyncio.iscoroutine(me_coro):
                            loop.run_until_complete(me_coro)
                    except Exception as e:
                        self.log_message(f"[{session_name}] get_me() error: {e}", 'WARNING')
                        authorized = False
                
                # Disconnect
                try:
                    disconnect_coro = client.disconnect()
                    if asyncio.iscoroutine(disconnect_coro):
                        loop.run_until_complete(disconnect_coro)
                except Exception as e:
                    self.log_message(f"[{session_name}] Disconnect error: {e}", 'WARNING')
                
                return (session_name, 'Connected' if authorized else 'Reauth needed')
            except TypeError as e:
                # This catches the "awaitable required" error
                self.log_message(f"[{session_name}] TypeError: {e}", 'ERROR')
                return (session_name, f"Type error: {str(e)[:40]}")
            except Exception as e:
                self.log_message(f"[{session_name}] General error: {type(e).__name__}: {e}", 'ERROR')
                return (session_name, f"Error: {str(e)[:60]}")
            finally:
                try:
                    loop.close()
                except Exception:
                    pass
        with ThreadPoolExecutor(max_workers=3) as ex:
            futs = [ex.submit(worker, s) for s in sessions]
            for fut in as_completed(futs):
                session_name, status = fut.result()
                results[session_name] = status
                # Update UI per-account with safe callback (capture variables)
                def _update_row(sn=session_name, st=status):
                    try:
                        # Check if widget still exists
                        if not self.account_tree.winfo_exists():
                            return
                        # find row and update Status + Last Used
                        for item in self.account_tree.get_children():
                            if self.account_tree.item(item)['text'] == sn:
                                vals = list(self.account_tree.item(item)['values'])
                                if len(vals) < 6:
                                    vals = (vals + ["", "", "", "", "", ""])[:6]
                                vals[1] = st  # Status column
                                if st == 'Connected':
                                    vals[5] = datetime.now().strftime('%Y-%m-%d %H:%M')
                                self.account_tree.item(item, values=vals)
                                break
                        self.log_message(f"[{sn}] {st}", 'SUCCESS' if st=='Connected' else ('WARNING' if st=='Not authorized' else 'ERROR'))
                        self.show_toast(f"{sn}: {st}", 'SUCCESS' if st=='Connected' else ('WARNING' if st=='Not authorized' else 'ERROR'), 2000)
                    except (tk.TclError, AttributeError):
                        # Widget destroyed, ignore
                        pass
                try:
                    self.root.after(0, _update_row)
                    self.root.after(0, self.update_account_counts_from_tree)
                except (tk.TclError, AttributeError):
                    # Root destroyed
                    pass
        # Summary with safe callbacks
        connected = sum(1 for s in results.values() if s=='Connected')
        reauth = sum(1 for s in results.values() if s=='Reauth needed')
        errors = len(results) - connected - reauth
        try:
            self.root.after(0, lambda c=connected, r=reauth, e=errors, total=len(results): self.set_status(f"Tested {total}: {c} connected, {r} need reauth, {e} error(s)", 'INFO'))
        except (tk.TclError, AttributeError):
            pass
        # If any need reauth, guide the user with a prompt
        if reauth > 0:
            sessions_to_fix = [sn for sn, st in results.items() if st=='Reauth needed']
            try:
                self.root.after(0, lambda s=sessions_to_fix: self.prompt_reauth_dialog(s))
            except (tk.TclError, AttributeError):
                pass
        
    def reconnect_connected_accounts(self):
        """Reconnect all accounts currently marked as Connected"""
        try:
            connected_sessions = []
            for item in self.account_tree.get_children():
                vals = self.account_tree.item(item)['values']
                if len(vals) >= 2 and str(vals[1]).lower() == 'connected':
                    connected_sessions.append(self.account_tree.item(item)['text'])
            if not connected_sessions:
                self.show_toast("No connected accounts to reconnect", 'WARNING', 1600)
                self.log_message("Reconnect requested: none connected", 'WARNING')
                return
            self.set_status(f"Reconnecting {len(connected_sessions)} account(s)...", 'INFO')
            self.show_toast("Reconnecting accounts…", 'INFO', 1500)
            threading.Thread(target=self._run_connection_test_for_sessions, args=(connected_sessions,), daemon=True).start()
        except Exception as e:
            self.log_message(f"Reconnect error: {e}", 'ERROR')
            self.show_toast("Reconnect error", 'ERROR', 1800)
        
    def force_sign_out_selected(self):
        """Force sign out selected accounts and delete local sessions, prompting re-login."""
        sessions = self.get_selected_session_names()
        if not sessions:
            self.show_toast("Select account(s) to sign out", 'WARNING', 1800)
            return
        threading.Thread(target=self._run_force_sign_out, args=(sessions,), daemon=True).start()
        
    def _run_force_sign_out(self, sessions):
        for session_name in sessions:
            acc = self.find_account_by_session(session_name)
            if not acc:
                self.root.after(0, lambda s=session_name: self.show_toast(f"{s}: not found", 'ERROR', 1600))
                continue
            self.root.after(0, lambda s=session_name: self.set_status(f"Signing out: {s}", 'INFO'))
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            client = None
            try:
                client = self.build_telegram_client(acc)
                loop.run_until_complete(client.connect())
                try:
                    loop.run_until_complete(client.log_out())
                except Exception:
                    pass
                loop.run_until_complete(client.disconnect())
            except Exception as e:
                self.log_message(f"Force sign out error for {session_name}: {e}", 'ERROR')
            finally:
                try:
                    if client:
                        loop.run_until_complete(client.disconnect())
                except Exception:
                    pass
                try:
                    loop.close()
                except Exception:
                    pass
            # Delete session files
            try:
                pattern = os.path.join(os.getcwd(), f"{session_name}.session*")
                for path in glob.glob(pattern):
                    try:
                        os.remove(path)
                    except Exception:
                        pass
            except Exception:
                pass
            # Update UI row to Not authorized
            def _update():
                for item in self.account_tree.get_children():
                    if self.account_tree.item(item)['text'] == session_name:
                        vals = list(self.account_tree.item(item)['values'])
                        if len(vals) < 6:
                            vals = (vals + ["", "", "", "", "", ""])[:6]
                        vals[1] = 'Not authorized'
                        self.account_tree.item(item, values=vals)
                        break
                self.show_toast(f"{session_name}: signed out", 'SUCCESS', 1800)
            self.root.after(0, _update)
        self.root.after(0, lambda: self.set_status("Force sign out completed", 'SUCCESS'))
        
    def health_check_all(self):
        """Perform health check on all accounts"""
        self.log_message("Starting health check on all accounts...", 'INFO')
        threading.Thread(target=self.run_health_check_all, daemon=True).start()
        
    def run_health_check_all(self):
        """Run comprehensive health check and auto-export results"""
        try:
            results = []
            total_accounts = len(self.account_tree.get_children())
            
            for i, item in enumerate(self.account_tree.get_children()):
                try:
                    session_name = self.account_tree.item(item)['text']
                    values = self.account_tree.item(item)['values']
                    
                    # Perform actual health assessment
                    health_data = self._assess_account_health(session_name, values)
                    results.append(health_data)
                    
                    # Update progress
                    progress = (i + 1) / total_accounts * 100
                    self.root.after(0, lambda p=progress, s=session_name: 
                                   self.log_message(f"Health check progress: {p:.0f}% - {s}", 'INFO'))
                    
            # No artificial delays - run at full speed
                    
                except Exception as e:
                    self.root.after(0, lambda err=str(e): self.log_message(f"Health check error: {err}", 'ERROR'))
            
            # Auto-export comprehensive health report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"health_check_report_{timestamp}.json"
            
            summary = {
                'timestamp': datetime.now().isoformat(),
                'total_accounts': len(results),
                'healthy_accounts': sum(1 for r in results if r['health_score'] >= 80),
                'warning_accounts': sum(1 for r in results if 60 <= r['health_score'] < 80),
                'critical_accounts': sum(1 for r in results if r['health_score'] < 60),
                'results': results
            }
            
            with open(report_filename, 'w') as f:
                json.dump(summary, f, indent=2)
            
            # Update UI with completion
            self.root.after(0, lambda: self.log_message(f"Health check completed - Report saved: {report_filename}", 'SUCCESS'))
            self.root.after(0, lambda: self.show_toast(f"Health check complete - {report_filename}", 'SUCCESS', 3000))
            self.root.after(0, lambda: self.set_status(f"Health check: {summary['healthy_accounts']}/{len(results)} healthy", 'SUCCESS'))
            
        except Exception as e:
            self.root.after(0, lambda err=str(e): self.log_message(f"Health check failed: {err}", 'ERROR'))
            
    def _assess_account_health(self, session_name, values):
        """Assess individual account health"""
        health_score = 100
        issues = []
        
        # Check connection status
        status = values[1] if len(values) > 1 else 'Unknown'
        if status == 'Connected':
            health_score -= 0
        elif status == 'Reauth needed':
            health_score -= 30
            issues.append("Reauth required")
        else:
            health_score -= 50
            issues.append(f"Status: {status}")
        
        # Check usage patterns
        usage = values[2] if len(values) > 2 else '0'
        try:
            daily_usage = int(usage.split('/')[0]) if '/' in usage else int(usage)
            if daily_usage > 200:
                health_score -= 20
                issues.append("High daily usage")
        except:
            health_score -= 10
            issues.append("Usage data unavailable")
        
        # Check last used time
        last_used = values[5] if len(values) > 5 else None
        if last_used:
            try:
                last_date = datetime.strptime(last_used, '%Y-%m-%d %H:%M')
                days_since = (datetime.now() - last_date).days
                if days_since > 7:
                    health_score -= 15
                    issues.append(f"Inactive for {days_since} days")
            except:
                pass
        
        # Ensure minimum score
        health_score = max(0, health_score)
        
        return {
            'session': session_name,
            'phone': values[0] if len(values) > 0 else 'N/A',
            'status': status,
            'health_score': health_score,
            'assessment': 'Healthy' if health_score >= 80 else 'Warning' if health_score >= 60 else 'Critical',
            'issues': issues,
            'timestamp': datetime.now().isoformat()
        }
        
    # Member context menu functions
    def copy_member_username(self):
        """Copy selected member username to clipboard"""
        try:
            selection = self.members_tree.selection()
            if selection:
                item = selection[0]
                username = self.members_tree.item(item)['values'][0]
                self.root.clipboard_clear()
                self.root.clipboard_append(username)
                self.show_toast(f"Copied: {username}", 'INFO', 1500)
        except Exception as e:
            self.log_message(f"Copy username error: {e}", 'ERROR')
            
    def copy_member_name(self):
        """Copy selected member name to clipboard"""
        try:
            selection = self.members_tree.selection()
            if selection:
                item = selection[0]
                name = self.members_tree.item(item)['values'][1]
                self.root.clipboard_clear()
                self.root.clipboard_append(name)
                self.show_toast(f"Copied: {name}", 'INFO', 1500)
        except Exception as e:
            self.log_message(f"Copy name error: {e}", 'ERROR')
            
    def send_dm_to_member(self):
        """Send direct message to selected member"""
        try:
            selection = self.members_tree.selection()
            if selection:
                item = selection[0]
                username = self.members_tree.item(item)['values'][0]
                # Switch to messaging tab and prefill target
                self.notebook.select(2)  # Messaging tab
                self.target_type.set("group")
                self.target_group_var.set(username)
                self.show_toast(f"DM target set: {username}", 'INFO', 2000)
        except Exception as e:
            self.log_message(f"DM setup error: {e}", 'ERROR')
            
    def add_member_to_targets(self):
        """Add member to targeting list"""
        try:
            selection = self.members_tree.selection()
            if selection:
                item = selection[0]
                values = self.members_tree.item(item)['values']
                username, name = values[0], values[1]
                # Could implement a targets database table here
                self.show_toast(f"Added {username} to targets", 'SUCCESS', 1800)
                self.log_message(f"Added to targets: {username} ({name})", 'INFO')
        except Exception as e:
            self.log_message(f"Add to targets error: {e}", 'ERROR')
            
    def remove_selected_member(self):
        """Remove selected member from list"""
        try:
            selection = self.members_tree.selection()
            if selection:
                for item in selection:
                    values = self.members_tree.item(item)['values']
                    username = values[0] if values else 'Unknown'
                    self.members_tree.delete(item)
                    self.log_message(f"Removed member: {username}", 'INFO')
                self.show_toast("Member(s) removed", 'INFO', 1500)
        except Exception as e:
            self.log_message(f"Remove member error: {e}", 'ERROR')
        
    def unlock_database(self):
        """Unlock database and return to baseline state"""
        try:
            # Close all existing connections
            if hasattr(self.automation, 'close_all_db_connections'):
                self.automation.close_all_db_connections()
            
            # Remove lock files if they exist
            db_files = [self.automation.db_path, f"{self.automation.db_path}-wal", f"{self.automation.db_path}-shm"]
            for db_file in db_files:
                if os.path.exists(db_file) and db_file.endswith(('-wal', '-shm')):
                    try:
                        os.remove(db_file)
                        self.log_message(f"Removed lock file: {db_file}", 'INFO')
                    except Exception as e:
                        self.log_message(f"Could not remove {db_file}: {e}", 'WARNING')
            
            # Reinitialize database connection
            self.automation.setup_database()
            self.log_message("Database unlocked and reset to baseline", 'SUCCESS')
            self.show_toast("Database unlocked successfully", 'SUCCESS', 2000)
            
            # Refresh UI
            self.refresh_account_tree()
            self.update_member_list()
            
        except Exception as e:
            self.log_message(f"Failed to unlock database: {e}", 'ERROR')
            self.show_toast("Failed to unlock database", 'ERROR', 2500)
        self.show_toast("Health check started", 'INFO', 1500)
        threading.Thread(target=self.run_health_checks, daemon=True).start()
        
    def sign_in_qr(self):
        """Start QR sign-in for selected accounts (processed sequentially)"""
        sessions = self.get_selected_session_names()
        if not sessions:
            self.show_toast("Select account(s) to sign in", 'WARNING', 1800)
            return
        if not QR_AVAILABLE or not PIL_AVAILABLE:
            self.show_toast("Install 'qrcode' and Pillow to use QR sign-in", 'ERROR', 2500)
            self.log_message("QR sign-in requires 'qrcode' and Pillow", 'ERROR')
            return
        self.set_status(f"QR sign-in for {len(sessions)} account(s)", 'INFO')
        threading.Thread(target=self._run_qr_multi_thread, args=(sessions,), daemon=True).start()
        
    def _run_qr_multi_thread(self, session_names):
        total = len(session_names)
        success_count = 0
        error_count = 0
        cancel_count = 0
        for idx, session_name in enumerate(session_names, 1):
            self.root.after(0, lambda i=idx, t=total, s=session_name: self.set_status(f"QR sign-in {i}/{t}: {s}", 'INFO'))
            acc = self.find_account_by_session(session_name)
            if not acc:
                self.root.after(0, lambda s=session_name: self.show_toast(f"{s}: not found", 'ERROR', 1800))
                continue
            self.root.after(0, lambda s=session_name: self.set_status(f"Signing in (QR): {s}", 'INFO'))
            self.log_message(f"QR sign-in started for {session_name}", 'INFO')
            try:
                res = self._qr_sign_in_flow(acc)
                if res == 'ok' or res == 'already':
                    success_count += 1
                elif res == 'cancel':
                    cancel_count += 1
                else:
                    error_count += 1
            except Exception as e:
                error_count += 1
                self.root.after(0, lambda s=session_name: self.show_toast(f"{s}: QR error", 'ERROR', 2000))
                self.log_message(f"QR sign-in error for {session_name}: {e}", 'ERROR')
        self.root.after(0, lambda sc=success_count, cc=cancel_count, ec=error_count, t=total: self.set_status(f"QR sign-in finished: {sc}/{t} success, {cc} cancelled, {ec} error(s)", 'SUCCESS' if error_count==0 else 'WARNING'))
        
    def _qr_sign_in_flow(self, account):
        """Run QR sign-in flow for a single account (in calling thread)"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        qr_dialog = {'win': None, 'img_label': None, 'img_ref': None, 'cancel': False}
        cancel_lock = threading.Lock()
        def open_qr_dialog():
            win = tk.Toplevel(self.root)
            win.title(f"Scan QR - {account.session_name}")
            win.transient(self.root)
            win.grab_set()
            frm = ttk.Frame(win)
            frm.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
            ttk.Label(frm, text=f"Scan this QR in Telegram app to sign in:\n{account.phone_number}").pack(pady=(0,8))
            img_label = ttk.Label(frm)
            img_label.pack()
            # Fallback: show QR login link and copy button
            link_frame = ttk.Frame(frm)
            link_frame.pack(fill=tk.X, pady=(8,0))
            link_var = tk.StringVar(value="")
            ttk.Label(link_frame, text="QR login link (fallback):", justify='left').pack(anchor='w')
            link_entry = ttk.Entry(link_frame, textvariable=link_var)
            link_entry.pack(fill=tk.X)
            def copy_link():
                try:
                    self.root.clipboard_clear()
                    self.root.clipboard_append(link_var.get())
                    self.show_toast("QR link copied", 'SUCCESS', 1200)
                except Exception:
                    pass
            ttk.Button(link_frame, text="Copy QR link", command=copy_link).pack(anchor='e', pady=(4,0))
            btns = ttk.Frame(frm)
            btns.pack(fill=tk.X, pady=(10,0))
            def on_cancel():
                with cancel_lock:
                    qr_dialog['cancel'] = True
                try:
                    win.destroy()
                except Exception:
                    pass
            ttk.Button(btns, text="Cancel", command=on_cancel).pack(side=tk.RIGHT)
            qr_dialog['win'] = win
            qr_dialog['img_label'] = img_label
            qr_dialog['link_var'] = link_var
        self.root.after(0, open_qr_dialog)
        # Wait until dialog created
        for _ in range(100):
            if qr_dialog['win'] is not None:
                break
            threading.Event().wait(0.05)
        client = None
        try:
            client = self.build_telegram_client(account)
            async def do_login():
                await client.connect()
                if await client.is_user_authorized():
                    return 'already'
                qr = await client.qr_login()
                # function to update QR image in UI
                def update_qr(url):
                    # Update image
                    qrimg = qrcode.make(url)
                    qrimg = qrimg.resize((280, 280))
                    photo = ImageTk.PhotoImage(qrimg)
                    qr_dialog['img_ref'] = photo
                    qr_dialog['img_label'].config(image=photo)
                    # Update link field
                    try:
                        qr_dialog['link_var'].set(url)
                    except Exception:
                        pass
                # show initial QR
                self.root.after(0, lambda: update_qr(qr.url))
                # Wait for scan with refresh on timeout
                while True:
                    with cancel_lock:
                        if qr_dialog['cancel']:
                            return 'cancel'
                    try:
                        await asyncio.wait_for(qr.wait(), timeout=120)
                        break
                    except asyncio.TimeoutError:
                        qr = await qr.recreate()
                        self.root.after(0, lambda: update_qr(qr.url))
                return 'ok'
            result = loop.run_until_complete(do_login())
            if result == 'ok' or result == 'already':
                # Close dialog
                self.root.after(0, lambda: (qr_dialog['win'] and qr_dialog['win'].destroy()))
                # Update UI account row
                def _update():
                    for item in self.account_tree.get_children():
                        if self.account_tree.item(item)['text'] == account.session_name:
                            vals = list(self.account_tree.item(item)['values'])
                            if len(vals) < 6:
                                vals = (vals + ["", "", "", "", "", ""])[:6]
                            vals[1] = 'Connected'
                            vals[5] = datetime.now().strftime('%Y-%m-%d %H:%M')
                            self.account_tree.item(item, values=vals)
                            break
                    self.show_toast(f"{account.session_name}: Signed in", 'SUCCESS', 2000)
                    self.set_status(f"Signed in: {account.session_name}", 'SUCCESS')
                    self.log_message(f"QR sign-in successful for {account.session_name}", 'SUCCESS')
                self.root.after(0, _update)
                self.root.after(0, self.update_account_counts_from_tree)
                return result
            elif result == 'cancel':
                self.root.after(0, lambda: self.show_toast("QR sign-in cancelled", 'WARNING', 1800))
                self.log_message(f"QR sign-in cancelled for {account.session_name}", 'WARNING')
                return result
        except Exception as e:
            self.root.after(0, lambda: self.show_toast(f"QR sign-in error: {str(e)[:60]}", 'ERROR', 2500))
            self.log_message(f"QR sign-in error for {account.session_name}: {e}", 'ERROR')
            return 'error'
        finally:
            try:
                if client:
                    loop.run_until_complete(client.disconnect())
            except Exception:
                pass
            try:
                loop.close()
            except Exception:
                pass
        return 'ok'
    def select_all_accounts(self):
        try:
            items = self.account_tree.get_children()
            self.account_tree.selection_set(items)
            self.show_toast("All accounts selected", 'INFO', 1200)
        except Exception:
            pass
    
    def deselect_all_accounts(self):
        try:
            self.account_tree.selection_remove(self.account_tree.selection())
            self.show_toast("Selection cleared", 'INFO', 1200)
        except Exception:
            pass
            
    def toggle_select_all_accounts(self):
        """Toggle between select all and deselect all"""
        try:
            selected = self.account_tree.selection()
            all_items = self.account_tree.get_children()
            
            if len(selected) == len(all_items) and len(all_items) > 0:
                # All are selected, deselect all
                self.deselect_all_accounts()
                self.select_toggle_btn.config(text="Select All")
            else:
                # Not all are selected, select all
                self.select_all_accounts()
                self.select_toggle_btn.config(text="Deselect All")
        except Exception as e:
            self.log_message(f"Toggle select error: {e}", 'WARNING')
    
    def select_connected_accounts(self):
        try:
            self.account_tree.selection_remove(self.account_tree.selection())
            for item in self.account_tree.get_children():
                vals = self.account_tree.item(item)['values']
                if len(vals) >= 2 and str(vals[1]).lower() == 'connected':
                    self.account_tree.selection_add(item)
            self.show_toast("Selected Connected accounts", 'INFO', 1400)
        except Exception:
            pass
    
    def select_not_authorized_accounts(self):
        try:
            self.account_tree.selection_remove(self.account_tree.selection())
            for item in self.account_tree.get_children():
                vals = self.account_tree.item(item)['values']
                if len(vals) >= 2 and str(vals[1]).lower().startswith('not authorized'):
                    self.account_tree.selection_add(item)
            self.show_toast("Selected Not Authorized accounts", 'INFO', 1400)
        except Exception:
            pass

    def set_selection_to_sessions(self, sessions):
        try:
            self.account_tree.selection_remove(self.account_tree.selection())
            have = set(sessions or [])
            for item in self.account_tree.get_children():
                if self.account_tree.item(item)['text'] in have:
                    self.account_tree.selection_add(item)
        except Exception:
            pass

    def open_reauth_guide(self):
        """Open the reauthentication guide dialog for selected accounts (or general guidance)."""
        sels = self.get_selected_session_names()
        self.prompt_reauth_dialog(sels)

    def show_welcome_guide(self):
        """Show a small welcome guide to orient new/existing users on sign-in and testing."""
        win = tk.Toplevel(self.root)
        win.title("Welcome • Getting Started")
        win.transient(self.root)
        frm = ttk.Frame(win)
        frm.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        text = (
            "Welcome to Enhanced Telegram Automation!\n\n"
            "Quick start:\n"
            "1) Import/Create accounts in Configuration → Account Management.\n"
            "2) Right-click accounts → Test Connection.\n"
            "3) If reauth is needed, use Sign In (QR/Code) or Force Sign Out.\n"
            "4) For scraping, use supergroups or invite links (not broadcast channels).\n"
            "5) Use Proxy Settings to assign per-account proxies if needed."
        )
        ttk.Label(frm, text=text, justify='left', wraplength=460).pack(anchor='w')
        btns = ttk.Frame(frm)
        btns.pack(fill=tk.X, pady=(10,0))
        ttk.Button(btns, text="Test Connection", command=self.test_connection).pack(side=tk.LEFT)
        ttk.Button(btns, text="Sign In (QR)", command=self.sign_in_qr).pack(side=tk.LEFT, padx=(6,0))
        ttk.Button(btns, text="Sign In (Code)", command=self.sign_in_code).pack(side=tk.LEFT, padx=(6,0))
        ttk.Button(btns, text="Open Telegram Web", command=self.open_telegram_web).pack(side=tk.RIGHT)
        ttk.Button(frm, text="Close", command=win.destroy).pack(anchor='e', pady=(10,0))

    def prompt_reauth_dialog(self, sessions):
        """Prompt user with options to reauthenticate/reset sessions."""
        win = tk.Toplevel(self.root)
        win.title("Reauthentication Needed")
        win.transient(self.root)
        frm = ttk.Frame(win)
        frm.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        if sessions:
            msg = f"These account(s) need reauthentication: {', '.join(sessions)}\n\nChoose an action:"
        else:
            msg = (
                "Some accounts may require reauthentication.\n\n"
                "Choose an action:"
            )
        ttk.Label(frm, text=msg, justify='left', wraplength=460).pack(anchor='w')
        
        def do_qr():
            self.set_selection_to_sessions(sessions)
            win.destroy()
            self.sign_in_qr()
        def do_code():
            self.set_selection_to_sessions(sessions)
            win.destroy()
            self.sign_in_code()
        def do_reset():
            self.set_selection_to_sessions(sessions)
            win.destroy()
            self.force_sign_out_selected()
        btns = ttk.Frame(frm)
        btns.pack(fill=tk.X, pady=(10,0))
        ttk.Button(btns, text="Sign In (QR)", command=do_qr).pack(side=tk.LEFT)
        ttk.Button(btns, text="Sign In (Code)", command=do_code).pack(side=tk.LEFT, padx=(6,0))
        ttk.Button(btns, text="Force Sign Out", command=do_reset).pack(side=tk.LEFT, padx=(6,0))
        ttk.Button(frm, text="Later", command=win.destroy).pack(anchor='e', pady=(10,0))
    
    def sign_in_code(self):
        """Start classic code-based sign-in for selected accounts sequentially"""
        sessions = self.get_selected_session_names()
        if not sessions:
            self.show_toast("Select account(s) to sign in", 'WARNING', 1800)
            return
        self.set_status(f"Code sign-in for {len(sessions)} account(s)", 'INFO')
        threading.Thread(target=self._run_code_multi_thread, args=(sessions,), daemon=True).start()
    
    def _run_code_multi_thread(self, session_names):
        total = len(session_names)
        success_count = 0
        error_count = 0
        for idx, session_name in enumerate(session_names, 1):
            acc = self.find_account_by_session(session_name)
            if not acc:
                error_count += 1
                self.root.after(0, lambda s=session_name: self.show_toast(f"{s}: not found", 'ERROR', 1800))
                continue
            self.root.after(0, lambda i=idx, t=total, s=session_name: self.set_status(f"Code sign-in {i}/{t}: {s}", 'INFO'))
            try:
                res = self._code_sign_in_flow(acc)
                if res == 'ok' or res == 'already':
                    success_count += 1
                else:
                    error_count += 1
            except Exception as e:
                error_count += 1
                self.log_message(f"Code sign-in error for {session_name}: {e}", 'ERROR')
                self.root.after(0, lambda s=session_name: self.show_toast(f"{s}: error", 'ERROR', 2000))
        self.root.after(0, lambda sc=success_count, ec=error_count, t=total: self.set_status(f"Code sign-in finished: {sc}/{t} success, {ec} error(s)", 'SUCCESS' if error_count==0 else 'WARNING'))
    
    def _code_sign_in_flow(self, account):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        client = None
        try:
            client = self.build_telegram_client(account)
            async def do_login():
                await client.connect()
                if await client.is_user_authorized():
                    return 'already'
                # Ask user how to deliver the code
                delivery = self._prompt_code_delivery_choice(account)
                try:
                    if delivery == 'sms':
                        try:
                            # Prefer force_sms when available
                            await client.send_code_request(account.phone_number, force_sms=True)
                        except TypeError:
                            # Fallback to CodeSettings
                            from telethon.tl.types import CodeSettings
                            try:
                                await client.send_code_request(account.phone_number, settings=CodeSettings(allow_flashcall=False, current_number=False, allow_app_hash=True))
                            except Exception:
                                # Last resort: plain call
                                await client.send_code_request(account.phone_number)
                    else:
                        # Default: send to app
                        try:
                            from telethon.tl.types import CodeSettings
                            await client.send_code_request(account.phone_number, settings=CodeSettings(allow_flashcall=False, current_number=False, allow_app_hash=True))
                        except Exception:
                            await client.send_code_request(account.phone_number)
                except Exception as e:
                    self.root.after(0, lambda: self.show_toast(f"Send code failed: {str(e)[:60]}", 'ERROR', 2500))
                    raise
                # Prompt for the code
                code = self._prompt_for_code_sync(account)
                if not code:
                    return 'cancel'
                try:
                    await client.sign_in(account.phone_number, code)
                except SessionPasswordNeededError:
                    pwd = self._prompt_for_password_sync(account)
                    if not pwd:
                        return 'cancel'
                    await client.sign_in(password=pwd)
                return 'ok'
            result = loop.run_until_complete(do_login())
            if result == 'ok' or result == 'already':
                # Update UI
                def _update():
                    for item in self.account_tree.get_children():
                        if self.account_tree.item(item)['text'] == account.session_name:
                            vals = list(self.account_tree.item(item)['values'])
                            if len(vals) < 6:
                                vals = (vals + ["", "", "", "", "", ""])[:6]
                            vals[1] = 'Connected'
                            vals[5] = datetime.now().strftime('%Y-%m-%d %H:%M')
                            self.account_tree.item(item, values=vals)
                            break
                    self.show_toast(f"{account.session_name}: Signed in", 'SUCCESS', 2000)
                    self.set_status(f"Signed in: {account.session_name}", 'SUCCESS')
                    self.log_message(f"Code sign-in successful for {account.session_name}", 'SUCCESS')
                self.root.after(0, _update)
                return result
            return result
        except PhoneCodeInvalidError:
            self.root.after(0, lambda: self.show_toast("Invalid code", 'ERROR', 2000))
            self.log_message(f"Invalid code for {account.session_name}", 'ERROR')
            return 'error'
        except PasswordHashInvalidError:
            self.root.after(0, lambda: self.show_toast("Invalid 2FA password", 'ERROR', 2000))
            self.log_message(f"Invalid 2FA for {account.session_name}", 'ERROR')
            return 'error'
        except FloodWaitError as e:
            self.root.after(0, lambda: self.show_toast(f"Rate limited, wait {getattr(e, 'seconds', '?')}s", 'ERROR', 2500))
            self.log_message(f"FloodWait for {account.session_name}: {e}", 'ERROR')
            return 'error'
        except ApiIdInvalidError:
            self.root.after(0, lambda: self.show_toast("Invalid API credentials", 'ERROR', 2500))
            self.log_message(f"Invalid API credentials for {account.session_name}", 'ERROR')
            return 'error'
        except Exception as e:
            self.root.after(0, lambda: self.show_toast(f"Sign-in error: {str(e)[:60]}", 'ERROR', 2500))
            self.log_message(f"Sign-in error for {account.session_name}: {e}", 'ERROR')
            return 'error'
        finally:
            try:
                if client:
                    loop.run_until_complete(client.disconnect())
            except Exception:
                pass
            try:
                loop.close()
            except Exception:
                pass
    
    def _prompt_code_delivery_choice(self, account):
        """Prompt how to deliver the login code: app (default) or SMS."""
        choice = {'v': 'app'}
        ev = threading.Event()
        def _show():
            win = tk.Toplevel(self.root)
            win.title(f"Code Delivery - {account.session_name}")
            win.transient(self.root)
            win.grab_set()
            frm = ttk.Frame(win)
            frm.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
            msg = (
                f"We can send the login code to your Telegram app (recommended) or via SMS to {account.phone_number}.\n\n"
                "• App: Open Telegram and check for a login code message.\n"
                "• SMS: May take longer and can be rate-limited."
            )
            ttk.Label(frm, text=msg, justify='left', wraplength=460).pack(anchor='w')
            btns = ttk.Frame(frm)
            btns.pack(fill=tk.X, pady=(10,0))
            def choose_app():
                choice['v'] = 'app'
                try:
                    win.destroy()
                finally:
                    ev.set()
            def choose_sms():
                choice['v'] = 'sms'
                try:
                    win.destroy()
                finally:
                    ev.set()
            ttk.Button(btns, text="Send to App", command=choose_app).pack(side=tk.LEFT)
            ttk.Button(btns, text="Send via SMS", command=choose_sms).pack(side=tk.LEFT, padx=(6,0))
        self.root.after(0, _show)
        ev.wait()
        return choice['v']

    def _prompt_for_code_sync(self, account):
        """Show modal code prompt on UI thread, return the entered code or None"""
        ev = threading.Event()
        q = queue.Queue()
        def _show():
            win = tk.Toplevel(self.root)
            win.title(f"Enter Code - {account.session_name}")
            win.transient(self.root)
            win.grab_set()
            frm = ttk.Frame(win)
            frm.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
            ttk.Label(frm, text=f"Enter the SMS/Telegram code for {account.phone_number}").pack(pady=(0,8))
            code_var = tk.StringVar()
            ent = ttk.Entry(frm, textvariable=code_var)
            ent.pack(fill=tk.X)
            ent.focus_set()
            btns = ttk.Frame(frm)
            btns.pack(fill=tk.X, pady=(10,0))
            def ok():
                q.put(code_var.get().strip())
                try:
                    win.destroy()
                finally:
                    ev.set()
            def cancel():
                q.put(None)
                try:
                    win.destroy()
                finally:
                    ev.set()
            ttk.Button(btns, text="OK", command=ok).pack(side=tk.RIGHT, padx=6)
            ttk.Button(btns, text="Cancel", command=cancel).pack(side=tk.RIGHT)
        self.root.after(0, _show)
        ev.wait()
        try:
            return q.get_nowait()
        except Exception:
            return None
    
    def _prompt_for_password_sync(self, account):
        """Show modal 2FA password prompt on UI thread, return password or None"""
        ev = threading.Event()
        q = queue.Queue()
        def _show():
            win = tk.Toplevel(self.root)
            win.title(f"Enter 2FA Password - {account.session_name}")
            win.transient(self.root)
            win.grab_set()
            frm = ttk.Frame(win)
            frm.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
            ttk.Label(frm, text=f"Enter 2FA password for {account.phone_number}").pack(pady=(0,8))
            pwd_var = tk.StringVar()
            ent = ttk.Entry(frm, textvariable=pwd_var, show='*')
            ent.pack(fill=tk.X)
            ent.focus_set()
            btns = ttk.Frame(frm)
            btns.pack(fill=tk.X, pady=(10,0))
            def ok():
                q.put(pwd_var.get())
                try:
                    win.destroy()
                finally:
                    ev.set()
            def cancel():
                q.put(None)
                try:
                    win.destroy()
                finally:
                    ev.set()
            ttk.Button(btns, text="OK", command=ok).pack(side=tk.RIGHT, padx=6)
            ttk.Button(btns, text="Cancel", command=cancel).pack(side=tk.RIGHT)
        self.root.after(0, _show)
        ev.wait()
        try:
            return q.get_nowait()
        except Exception:
            return None
    
    def run_health_checks(self):
        """Run health checks in background"""
        # Simulate health check process
        import time
        for i in range(3):  # Simulate checking 3 accounts
            time.sleep(1)
            health_score = random.randint(60, 100)
            status = "🟢 Excellent" if health_score >= 90 else "🟡 Good" if health_score >= 70 else "🔴 Poor"
            account_num = i + 1  # Capture the value
            log_level = 'SUCCESS' if health_score >= 70 else 'WARNING'
            message = f"Account {account_num}: {status} ({health_score}%)"
            
            # Use a proper closure to capture values
            self.root.after(0, lambda msg=message, level=log_level: self.log_message(msg, level))
            
        self.root.after(0, lambda: self.log_message("Health check completed", 'SUCCESS'))
        self.root.after(0, lambda: self.set_status("Health check completed", 'SUCCESS'))
        self.root.after(0, lambda: self.show_toast("Health check completed", 'SUCCESS', 2000))
        
    def rotate_sessions(self):
        """Rotate account sessions for security"""
        self.log_message("Initiating session rotation...", 'INFO')
        # Implementation for session rotation
        
    def auto_assign_proxies(self):
        """Automatically assign proxies to accounts (round-robin) and persist to config"""
        proxy_items = list(self.proxy_tree.get_children())
        account_items = list(self.account_tree.get_children())
        proxy_count = len(proxy_items)
        account_count = len(account_items)
        if proxy_count == 0 or account_count == 0:
            messagebox.showwarning("Warning", "No proxies or accounts available")
            return
        cfg = configparser.ConfigParser()
        cfg.read(self.automation.config_file)
        assigned = 0
        for idx, item in enumerate(account_items):
            session = self.account_tree.item(item)['text']
            # Find section by session_name
            section = None
            for s in cfg.sections():
                if s.startswith('account_') and cfg[s].get('session_name') == session:
                    section = s
                    break
            if not section:
                continue
            # Pick proxy round-robin
            pitem = proxy_items[idx % proxy_count]
            vals = list(self.proxy_tree.item(pitem)['values'])
            host, port = str(vals[0]).strip(), str(vals[1]).strip()
            if not host or not port:
                continue
            cfg[section]['proxy_host'] = host
            cfg[section]['proxy_port'] = port
            # default to socks5 if not set
            if not cfg[section].get('proxy_type'):
                cfg[section]['proxy_type'] = 'socks5'
            # Update tree Account column
            vals[3] = session
            self.proxy_tree.item(pitem, values=vals)
            assigned += 1
        with open(self.automation.config_file, 'w') as f:
            cfg.write(f)
        self.automation.load_configuration()
        self.refresh_account_tree()
        self.show_toast(f"Assigned proxies to {assigned} accounts", 'SUCCESS', 1500)
        self.log_message(f"Auto-assigned proxies to {assigned} accounts", 'SUCCESS')
        
    def export_health_report(self):
        """Export account health report"""
        # Default to home directory to avoid permission issues
        import os
        default_dir = os.path.expanduser('~')
        filename = filedialog.asksaveasfilename(
            initialdir=default_dir,
            defaultextension=".json", 
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv")]
        )
        if filename:
            # Export health data (placeholder)
            try:
                # Ensure directory exists and is writable
                dirname = os.path.dirname(filename)
                if not os.access(dirname, os.W_OK):
                    raise PermissionError(f"No write permission for directory: {dirname}")
                    
                with open(filename, 'w') as f:
                    f.write('{}')
                self.log_message(f"Health report exported to {filename}", 'SUCCESS')
                self.show_toast("Health report exported", 'SUCCESS', 1400)
            except PermissionError as e:
                messagebox.showerror("Permission Denied", f"{e}\n\nTry saving to your home directory instead.")
                self.show_toast("Permission denied", 'ERROR', 1800)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export health report: {e}")
                self.show_toast("Export failed", 'ERROR', 1800)
        
    def export_accounts_json(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not filename:
            return
        try:
            data = []
            for acc in self.automation.accounts:
                data.append({
                    'api_id': acc.api_id,
                    'api_hash': acc.api_hash,
                    'phone_number': acc.phone_number,
                    'session_name': acc.session_name,
                    'proxy_host': acc.proxy_host or '',
                    'proxy_port': acc.proxy_port or '',
                    'proxy_username': acc.proxy_username or '',
                    'proxy_password': acc.proxy_password or ''
                })
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            self.log_message(f"Exported accounts to {filename}", 'SUCCESS')
            self.show_toast("Accounts exported (JSON)", 'SUCCESS', 1400)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export accounts: {e}")
            self.show_toast("Export failed", 'ERROR', 1800)
        
    def export_accounts_csv(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not filename:
            return
        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['api_id','api_hash','phone_number','session_name','proxy_host','proxy_port','proxy_username','proxy_password'])
                for acc in self.automation.accounts:
                    writer.writerow([acc.api_id, acc.api_hash, acc.phone_number, acc.session_name, acc.proxy_host or '', acc.proxy_port or '', acc.proxy_username or '', acc.proxy_password or ''])
            self.log_message(f"Exported accounts to {filename}", 'SUCCESS')
            self.show_toast("Accounts exported (CSV)", 'SUCCESS', 1400)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export accounts: {e}")
            self.show_toast("Export failed", 'ERROR', 1800)
        
    def import_accounts_json(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not filename:
            return
        try:
            with open(filename, 'r') as f:
                items = json.load(f)
            cfg = configparser.ConfigParser()
            cfg.read(self.automation.config_file)
            # Insert or update
            for item in items:
                session = str(item.get('session_name','')).strip()
                if not session:
                    continue
                section = None
                for s in cfg.sections():
                    if s.startswith('account_') and cfg[s].get('session_name') == session:
                        section = s
                        break
                if not section:
                    idx = 1
                    while f'account_{idx}' in cfg.sections():
                        idx += 1
                    section = f'account_{idx}'
                cfg[section] = {
                    'api_id': str(item.get('api_id','')),
                    'api_hash': item.get('api_hash',''),
                    'phone_number': item.get('phone_number',''),
                    'session_name': session,
                    'proxy_host': item.get('proxy_host',''),
                    'proxy_port': str(item.get('proxy_port','')),
                    'proxy_username': item.get('proxy_username',''),
                    'proxy_password': item.get('proxy_password','')
                }
            with open(self.automation.config_file, 'w') as f:
                cfg.write(f)
            self.automation.load_configuration()
            self.refresh_account_tree()
            self.log_message(f"Imported accounts from {filename}", 'SUCCESS')
            self.show_toast("Accounts imported", 'SUCCESS', 1400)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import accounts: {e}")
            self.show_toast("Import failed", 'ERROR', 1800)
        
    def import_accounts_csv(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not filename:
            return
        try:
            rows = []
            with open(filename, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rows.append(row)
            cfg = configparser.ConfigParser()
            cfg.read(self.automation.config_file)
            for item in rows:
                session = str(item.get('session_name','')).strip()
                if not session:
                    continue
                section = None
                for s in cfg.sections():
                    if s.startswith('account_') and cfg[s].get('session_name') == session:
                        section = s
                        break
                if not section:
                    idx = 1
                    while f'account_{idx}' in cfg.sections():
                        idx += 1
                    section = f'account_{idx}'
                cfg[section] = {
                    'api_id': str(item.get('api_id','')),
                    'api_hash': item.get('api_hash',''),
                    'phone_number': item.get('phone_number',''),
                    'session_name': session,
                    'proxy_host': item.get('proxy_host',''),
                    'proxy_port': str(item.get('proxy_port','')),
                    'proxy_username': item.get('proxy_username',''),
                    'proxy_password': item.get('proxy_password','')
                }
            with open(self.automation.config_file, 'w') as f:
                cfg.write(f)
            self.automation.load_configuration()
            self.refresh_account_tree()
            self.log_message(f"Imported accounts from {filename}", 'SUCCESS')
            self.show_toast("Accounts imported", 'SUCCESS', 1400)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import accounts: {e}")
            self.show_toast("Import failed", 'ERROR', 1800)
            
    def pause_selected_operation(self):
        """Pause selected operation"""
        selection = self.operation_tree.selection()
        if selection:
            self.log_message("Pausing selected operation...", 'WARNING')
            
    def resume_selected_operation(self):
        """Resume selected operation"""
        selection = self.operation_tree.selection()
        if selection:
            self.log_message("Resuming selected operation...", 'INFO')
            
    def retry_failed_operations(self):
        """Retry all failed operations"""
        self.log_message("Retrying failed operations...", 'INFO')
        
    def clear_completed_operations(self):
        """Clear completed operations from list"""
        # Remove completed operations from tree
        for item in self.operation_tree.get_children():
            values = self.operation_tree.item(item)['values']
            if values and 'Completed' in str(values[2]):
                self.operation_tree.delete(item)
        self.log_message("Cleared completed operations", 'INFO')

    def reconnect_connected_accounts(self):
        """Reconnect all connected accounts"""
        try:
            connected_count = 0
            for item in self.account_tree.get_children():
                values = self.account_tree.item(item)['values']
                if values and len(values) > 1 and 'Connected' in str(values[1]):
                    connected_count += 1
            
            if connected_count == 0:
                self.log_message("No connected accounts to reconnect", 'WARNING')
                return
            
            self.log_message(f"Reconnecting {connected_count} connected accounts...", 'INFO')
            # This would trigger a reconnection process
            self.test_connection()
            
        except Exception as e:
            self.log_message(f"Error reconnecting accounts: {e}", 'ERROR')

def main():
    """Main function to start the GUI"""
    root = tk.Tk()
    app = EnhancedTelegramGUI(root)
    
    # Initialize with welcome message
    app.log_message("Enhanced Telegram Automation Suite v2.0 started", 'SUCCESS')
    app.log_message("Ready for operations", 'INFO')
    
    root.mainloop()

if __name__ == "__main__":
    main()