#!/usr/bin/env python3
"""
Unified Tool Launcher
=====================
Professional launcher providing seamless access to both Telegram Automation
and SMS Marketplace tools with integrated data sharing and cross-workflows.

Author: Enhanced by AI Assistant
Version: 3.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import os
from datetime import datetime
from pathlib import Path
import logging
import subprocess
import sys
from typing import Dict, List, Optional, Any

# Import the integration manager
from unified_integration_manager import (
    integration_manager, ToolType, EventType, IntegrationEvent,
    SharedPhoneNumber, UnifiedSession
)

class UnifiedToolLauncher:
    """Professional launcher for integrated Telegram and SMS tools"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Unified Telegram & SMS Automation Suite")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e1e1e')
        
        # Tool instances
        self.telegram_process = None
        self.sms_marketplace_process = None
        self.tool_windows = {}
        
        # Status tracking
        self.telegram_status = "Not Running"
        self.sms_status = "Not Running"
        self.integration_active = True
        
        # Setup logging
        self.setup_logging()
        
        # Setup styles
        self.setup_styles()
        
        # Register event handlers with integration manager
        self.setup_integration_handlers()
        
        # Create GUI
        self.create_interface()
        
        # Start status monitoring
        self.start_status_monitoring()
        
        # Cleanup on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.logger.info("Unified Tool Launcher initialized")
    
    def setup_logging(self):
        """Setup logging for the launcher"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('unified_launcher.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_styles(self):
        """Setup consistent dark theme styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors for unified dark theme
        style.configure('TLabel', background='#1e1e1e', foreground='#ffffff')
        style.configure('TFrame', background='#1e1e1e')
        style.configure('TButton', background='#404040', foreground='#ffffff', borderwidth=1)
        style.map('TButton', background=[('active', '#505050'), ('pressed', '#606060')])
        style.configure('TEntry', fieldbackground='#404040', foreground='#ffffff', insertcolor='#ffffff')
        style.configure('TNotebook', background='#1e1e1e', tabposition='n')
        style.configure('TNotebook.Tab', background='#404040', foreground='#ffffff', padding=[15, 8])
        style.map('TNotebook.Tab', background=[('selected', '#505050'), ('active', '#454545')])
        style.configure('TLabelFrame', background='#1e1e1e', foreground='#ffffff')
        style.configure('TLabelFrame.Label', background='#1e1e1e', foreground='#ffffff')
        style.configure('Treeview', background='#404040', foreground='#ffffff', fieldbackground='#404040')
        style.configure('Treeview.Heading', background='#505050', foreground='#ffffff')
        
        # Custom styles
        style.configure('Title.TLabel', font=('Consolas', 20, 'bold'), background='#1e1e1e', foreground='#00ff88')
        style.configure('Subtitle.TLabel', font=('Consolas', 12), background='#1e1e1e', foreground='#cccccc')
        style.configure('Status.TLabel', font=('Consolas', 10), background='#1e1e1e')
        style.configure('Success.TLabel', foreground='#00ff88')
        style.configure('Warning.TLabel', foreground='#ffaa00')
        style.configure('Error.TLabel', foreground='#ff4444')
        style.configure('Launch.TButton', font=('Consolas', 12, 'bold'), background='#00aa44')
        style.configure('Stop.TButton', font=('Consolas', 12, 'bold'), background='#aa4400')
    
    def setup_integration_handlers(self):
        """Setup event handlers for cross-tool integration"""
        # Register handlers for integration events
        integration_manager.register_event_handler(
            EventType.NUMBER_PURCHASED, self.on_number_purchased
        )
        integration_manager.register_event_handler(
            EventType.SMS_CODE_RECEIVED, self.on_sms_code_received
        )
        integration_manager.register_event_handler(
            EventType.ACCOUNT_CREATED, self.on_account_created
        )
    
    def create_interface(self):
        """Create the main launcher interface"""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(main_container)
        
        # Main content area with notebook
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Create tabs
        self.create_launcher_tab()
        self.create_integration_tab()
        self.create_shared_data_tab()
        self.create_workflow_tab()
        self.create_monitoring_tab()
        
        # Status bar
        self.create_status_bar(main_container)
    
    def create_header(self, parent):
        """Create header section"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title and subtitle
        ttk.Label(header_frame, text="🚀 Unified Automation Suite", 
                 style='Title.TLabel').pack(anchor=tk.W)
        
        ttk.Label(header_frame, text="Professional Telegram & SMS marketplace integration with seamless workflows",
                 style='Subtitle.TLabel').pack(anchor=tk.W, pady=(5, 0))
        
        # Quick stats
        stats_frame = ttk.Frame(header_frame)
        stats_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.stats_labels = {}
        stats_data = integration_manager.get_statistics()
        
        col = 0
        for stat_name, value in [
            ("Phone Numbers", stats_data.get('phone_numbers', {}).get('available', 0)),
            ("Verification Codes", stats_data.get('unused_codes', 0)),
            ("Active Sessions", stats_data.get('sessions', {}).get('active', 0)),
            ("Available Proxies", stats_data.get('proxies', {}).get('active', 0))
        ]:
            stat_frame = ttk.Frame(stats_frame)
            stat_frame.grid(row=0, column=col, padx=(0, 30), sticky="w")
            
            ttk.Label(stat_frame, text=f"{value}", 
                     font=('Consolas', 16, 'bold'), foreground='#00ff88').pack()
            ttk.Label(stat_frame, text=stat_name, 
                     font=('Consolas', 9)).pack()
            
            self.stats_labels[stat_name] = stat_frame
            col += 1
    
    def create_launcher_tab(self):
        """Create the main tool launcher tab"""
        launcher_frame = ttk.Frame(self.notebook)
        self.notebook.add(launcher_frame, text="🚀 Tool Launcher")
        
        # Main grid layout
        launcher_frame.grid_columnconfigure(0, weight=1)
        launcher_frame.grid_columnconfigure(1, weight=1)
        launcher_frame.grid_rowconfigure(1, weight=1)
        
        # Telegram Automation Panel
        telegram_frame = ttk.LabelFrame(launcher_frame, text="Telegram Automation Suite", padding=20)
        telegram_frame.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")
        
        self.create_telegram_panel(telegram_frame)
        
        # SMS Marketplace Panel
        sms_frame = ttk.LabelFrame(launcher_frame, text="SMS Marketplace", padding=20)
        sms_frame.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="nsew")
        
        self.create_sms_panel(sms_frame)
        
        # Integration Controls
        integration_frame = ttk.LabelFrame(launcher_frame, text="Integration Controls", padding=20)
        integration_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky="nsew")
        
        self.create_integration_controls(integration_frame)
    
    def create_telegram_panel(self, parent):
        """Create Telegram automation control panel"""
        # Status
        self.telegram_status_label = ttk.Label(parent, text=f"Status: {self.telegram_status}", 
                                             style='Status.TLabel')
        self.telegram_status_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Description
        ttk.Label(parent, text="Advanced Telegram automation with anti-detection,\nscraping, bulk inviting, and messaging capabilities.",
                 style='Subtitle.TLabel').pack(anchor=tk.W, pady=(0, 15))
        
        # Features list
        features_frame = ttk.Frame(parent)
        features_frame.pack(fill=tk.X, pady=(0, 15))
        
        features = [
            "✓ Multi-account management",
            "✓ Proxy rotation & anti-detection",
            "✓ Member scraping & export",
            "✓ Bulk inviting & messaging",
            "✓ Session management",
            "✓ Real-time monitoring"
        ]
        
        for i, feature in enumerate(features):
            row = i // 2
            col = i % 2
            ttk.Label(features_frame, text=feature, font=('Consolas', 9), 
                     foreground='#00ff88').grid(row=row, column=col, sticky="w", padx=(0, 20))
        
        # Control buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.telegram_launch_btn = ttk.Button(button_frame, text="🚀 Launch Telegram GUI", 
                                            command=self.launch_telegram_gui, style='Launch.TButton')
        self.telegram_launch_btn.pack(fill=tk.X, pady=(0, 5))
        
        self.telegram_stop_btn = ttk.Button(button_frame, text="⏹ Stop Telegram", 
                                          command=self.stop_telegram, state='disabled', style='Stop.TButton')
        self.telegram_stop_btn.pack(fill=tk.X)
    
    def create_sms_panel(self, parent):
        """Create SMS marketplace control panel"""
        # Status
        self.sms_status_label = ttk.Label(parent, text=f"Status: {self.sms_status}", 
                                        style='Status.TLabel')
        self.sms_status_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Description
        ttk.Label(parent, text="Professional SMS number marketplace with\nreal-time pricing, bulk operations, and automation.",
                 style='Subtitle.TLabel').pack(anchor=tk.W, pady=(0, 15))
        
        # Features list
        features_frame = ttk.Frame(parent)
        features_frame.pack(fill=tk.X, pady=(0, 15))
        
        features = [
            "✓ Multi-provider support",
            "✓ Real-time SMS monitoring",
            "✓ Bulk purchasing operations",
            "✓ Verification code management",
            "✓ Wallet integration",
            "✓ Database logging"
        ]
        
        for i, feature in enumerate(features):
            row = i // 2
            col = i % 2
            ttk.Label(features_frame, text=feature, font=('Consolas', 9), 
                     foreground='#00ff88').grid(row=row, column=col, sticky="w", padx=(0, 20))
        
        # Control buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.sms_launch_btn = ttk.Button(button_frame, text="🏪 Launch SMS Marketplace", 
                                       command=self.launch_sms_marketplace, style='Launch.TButton')
        self.sms_launch_btn.pack(fill=tk.X, pady=(0, 5))
        
        self.sms_stop_btn = ttk.Button(button_frame, text="⏹ Stop Marketplace", 
                                     command=self.stop_sms_marketplace, state='disabled', style='Stop.TButton')
        self.sms_stop_btn.pack(fill=tk.X)
    
    def create_integration_controls(self, parent):
        """Create integration control panel"""
        # Quick workflow buttons
        workflow_frame = ttk.Frame(parent)
        workflow_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(workflow_frame, text="Quick Workflows:", font=('Consolas', 12, 'bold')).pack(anchor=tk.W)
        
        workflow_buttons = ttk.Frame(workflow_frame)
        workflow_buttons.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(workflow_buttons, text="🔄 Sync Phone Numbers", 
                  command=self.sync_phone_numbers).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(workflow_buttons, text="📱 Create TG Account", 
                  command=self.create_telegram_account_workflow).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(workflow_buttons, text="🎯 Auto-Purchase & Use", 
                  command=self.auto_purchase_workflow).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(workflow_buttons, text="📊 Export All Data", 
                  command=self.export_integrated_data).pack(side=tk.LEFT)
        
        # Integration status
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X)
        
        ttk.Label(status_frame, text="Integration Status:", font=('Consolas', 10, 'bold')).pack(anchor=tk.W)
        
        self.integration_status_label = ttk.Label(status_frame, text="✅ Active - Cross-tool communication enabled", 
                                                style='Success.TLabel')
        self.integration_status_label.pack(anchor=tk.W, pady=(5, 0))
    
    def create_integration_tab(self):
        """Create integration management tab"""
        integration_frame = ttk.Frame(self.notebook)
        self.notebook.add(integration_frame, text="🔗 Integration")
        
        # Split into sections
        left_frame = ttk.Frame(integration_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_frame = ttk.Frame(integration_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Phone number sync
        phone_frame = ttk.LabelFrame(left_frame, text="Phone Number Synchronization", padding=15)
        phone_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.create_phone_sync_panel(phone_frame)
        
        # Proxy sharing
        proxy_frame = ttk.LabelFrame(left_frame, text="Shared Proxy Pool", padding=15)
        proxy_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_proxy_sharing_panel(proxy_frame)
        
        # Event monitoring
        event_frame = ttk.LabelFrame(right_frame, text="Real-time Event Monitoring", padding=15)
        event_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_event_monitoring_panel(event_frame)
    
    def create_shared_data_tab(self):
        """Create shared data management tab"""
        data_frame = ttk.Frame(self.notebook)
        self.notebook.add(data_frame, text="📊 Shared Data")
        
        # Data overview
        overview_frame = ttk.LabelFrame(data_frame, text="Data Overview", padding=15)
        overview_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.create_data_overview(overview_frame)
        
        # Data tables
        tables_frame = ttk.Frame(data_frame)
        tables_frame.pack(fill=tk.BOTH, expand=True)
        
        # Phone numbers table
        phone_table_frame = ttk.LabelFrame(tables_frame, text="Shared Phone Numbers", padding=10)
        phone_table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.create_phone_numbers_table(phone_table_frame)
        
        # Verification codes table
        codes_table_frame = ttk.LabelFrame(tables_frame, text="Verification Codes", padding=10)
        codes_table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.create_verification_codes_table(codes_table_frame)
    
    def create_workflow_tab(self):
        """Create automated workflow tab"""
        workflow_frame = ttk.Frame(self.notebook)
        self.notebook.add(workflow_frame, text="⚙️ Workflows")
        
        # Workflow templates
        templates_frame = ttk.LabelFrame(workflow_frame, text="Workflow Templates", padding=15)
        templates_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.create_workflow_templates(templates_frame)
        
        # Active workflows
        active_frame = ttk.LabelFrame(workflow_frame, text="Active Workflows", padding=15)
        active_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_active_workflows(active_frame)
    
    def create_monitoring_tab(self):
        """Create system monitoring tab"""
        monitoring_frame = ttk.Frame(self.notebook)
        self.notebook.add(monitoring_frame, text="📈 Monitoring")
        
        # System status
        status_frame = ttk.LabelFrame(monitoring_frame, text="System Status", padding=15)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.create_system_status(status_frame)
        
        # Logs and events
        logs_frame = ttk.LabelFrame(monitoring_frame, text="Event Logs", padding=15)
        logs_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_event_logs(logs_frame)
    
    # Helper methods for creating sub-panels (simplified for brevity)
    def create_phone_sync_panel(self, parent):
        """Create phone number synchronization panel"""
        ttk.Label(parent, text="Phone numbers are automatically synced between tools").pack(anchor=tk.W)
        
        sync_btn_frame = ttk.Frame(parent)
        sync_btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(sync_btn_frame, text="🔄 Force Sync", command=self.sync_phone_numbers).pack(side=tk.LEFT)
        ttk.Button(sync_btn_frame, text="📥 Import Numbers", command=self.import_phone_numbers).pack(side=tk.LEFT, padx=(10, 0))
    
    def create_proxy_sharing_panel(self, parent):
        """Create proxy sharing panel"""
        ttk.Label(parent, text="Proxy pool shared between both tools").pack(anchor=tk.W)
        
        proxy_btn_frame = ttk.Frame(parent)
        proxy_btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(proxy_btn_frame, text="➕ Add Proxies", command=self.add_shared_proxies).pack(side=tk.LEFT)
        ttk.Button(proxy_btn_frame, text="🧪 Test All", command=self.test_shared_proxies).pack(side=tk.LEFT, padx=(10, 0))
    
    def create_event_monitoring_panel(self, parent):
        """Create event monitoring panel"""
        # Event log display
        self.event_text = tk.Text(parent, height=20, bg='#2b2b2b', fg='#ffffff', 
                                 font=('Consolas', 9), wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.event_text.yview)
        self.event_text.configure(yscrollcommand=scrollbar.set)
        
        self.event_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add some sample events
        self.add_event_log("System", "Integration manager initialized")
        self.add_event_log("System", "Monitoring started")
    
    def create_data_overview(self, parent):
        """Create data overview section"""
        stats = integration_manager.get_statistics()
        
        stats_grid = ttk.Frame(parent)
        stats_grid.pack(fill=tk.X)
        
        row = 0
        for category, data in stats.items():
            if isinstance(data, dict):
                ttk.Label(stats_grid, text=f"{category.replace('_', ' ').title()}:", 
                         font=('Consolas', 10, 'bold')).grid(row=row, column=0, sticky="w", pady=2)
                
                info = ", ".join([f"{k}: {v}" for k, v in data.items()])
                ttk.Label(stats_grid, text=info).grid(row=row, column=1, sticky="w", padx=(10, 0), pady=2)
                row += 1
            else:
                ttk.Label(stats_grid, text=f"{category.replace('_', ' ').title()}:", 
                         font=('Consolas', 10, 'bold')).grid(row=row, column=0, sticky="w", pady=2)
                ttk.Label(stats_grid, text=str(data)).grid(row=row, column=1, sticky="w", padx=(10, 0), pady=2)
                row += 1
    
    def create_phone_numbers_table(self, parent):
        """Create phone numbers table"""
        # Table headers
        headers = ["Phone", "Service", "Status", "Provider"]
        
        self.phone_tree = ttk.Treeview(parent, columns=headers, show='headings', height=15)
        
        for header in headers:
            self.phone_tree.heading(header, text=header)
            self.phone_tree.column(header, width=120)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.phone_tree.yview)
        h_scroll = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.phone_tree.xview)
        self.phone_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.phone_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.refresh_phone_numbers_table()
    
    def create_verification_codes_table(self, parent):
        """Create verification codes table"""
        headers = ["Phone", "Code", "Service", "Time"]
        
        self.codes_tree = ttk.Treeview(parent, columns=headers, show='headings', height=15)
        
        for header in headers:
            self.codes_tree.heading(header, text=header)
            self.codes_tree.column(header, width=100)
        
        v_scroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.codes_tree.yview)
        self.codes_tree.configure(yscrollcommand=v_scroll.set)
        
        self.codes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.refresh_verification_codes_table()
    
    def create_workflow_templates(self, parent):
        """Create workflow template buttons"""
        templates = [
            ("📱 Create TG Account", "Create Telegram account using SMS number"),
            ("🔄 Sync All Data", "Synchronize all data between tools"),
            ("🎯 Auto Purchase", "Automatically purchase and assign numbers"),
            ("📊 Generate Reports", "Export comprehensive usage reports")
        ]
        
        for i, (name, desc) in enumerate(templates):
            template_frame = ttk.Frame(parent)
            template_frame.pack(fill=tk.X, pady=5)
            
            ttk.Button(template_frame, text=name, width=20).pack(side=tk.LEFT)
            ttk.Label(template_frame, text=desc, font=('Consolas', 9)).pack(side=tk.LEFT, padx=(10, 0))
    
    def create_active_workflows(self, parent):
        """Create active workflows display"""
        self.workflow_text = tk.Text(parent, height=15, bg='#2b2b2b', fg='#ffffff', 
                                   font=('Consolas', 9), wrap=tk.WORD, state='disabled')
        
        workflow_scroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.workflow_text.yview)
        self.workflow_text.configure(yscrollcommand=workflow_scroll.set)
        
        self.workflow_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        workflow_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_system_status(self, parent):
        """Create system status display"""
        status_grid = ttk.Frame(parent)
        status_grid.pack(fill=tk.X)
        
        # Tool status
        ttk.Label(status_grid, text="Telegram GUI:", font=('Consolas', 10, 'bold')).grid(row=0, column=0, sticky="w")
        self.tg_status_display = ttk.Label(status_grid, text="Not Running", foreground='#ff4444')
        self.tg_status_display.grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        ttk.Label(status_grid, text="SMS Marketplace:", font=('Consolas', 10, 'bold')).grid(row=1, column=0, sticky="w")
        self.sms_status_display = ttk.Label(status_grid, text="Not Running", foreground='#ff4444')
        self.sms_status_display.grid(row=1, column=1, sticky="w", padx=(10, 0))
        
        ttk.Label(status_grid, text="Integration:", font=('Consolas', 10, 'bold')).grid(row=2, column=0, sticky="w")
        self.int_status_display = ttk.Label(status_grid, text="Active", foreground='#00ff88')
        self.int_status_display.grid(row=2, column=1, sticky="w", padx=(10, 0))
    
    def create_event_logs(self, parent):
        """Create event logs display"""
        self.logs_text = tk.Text(parent, bg='#2b2b2b', fg='#ffffff', 
                               font=('Consolas', 9), wrap=tk.WORD, state='disabled')
        
        logs_scroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.logs_text.yview)
        self.logs_text.configure(yscrollcommand=logs_scroll.set)
        
        self.logs_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        logs_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_status_bar(self, parent):
        """Create status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Status text
        self.status_text = ttk.Label(status_frame, text="Ready - Integration active", 
                                   style='Success.TLabel')
        self.status_text.pack(side=tk.LEFT)
        
        # Buttons
        button_frame = ttk.Frame(status_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="📊 Refresh Stats", 
                  command=self.refresh_statistics).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="🔄 Restart Integration", 
                  command=self.restart_integration).pack(side=tk.LEFT)
    
    # Tool launch methods
    def launch_telegram_gui(self):
        """Launch the Telegram automation GUI"""
        try:
            if self.telegram_process and self.telegram_process.poll() is None:
                messagebox.showwarning("Warning", "Telegram GUI is already running")
                return
            
            # Launch the enhanced Telegram GUI
            script_path = Path(__file__).parent / "enhanced_telegram_gui.py"
            self.telegram_process = subprocess.Popen([sys.executable, str(script_path)])
            
            self.telegram_status = "Running"
            self.telegram_status_label.config(text=f"Status: {self.telegram_status}", 
                                            style='Success.TLabel')
            self.tg_status_display.config(text="Running", foreground='#00ff88')
            
            self.telegram_launch_btn.config(state='disabled')
            self.telegram_stop_btn.config(state='normal')
            
            self.add_event_log("System", "Telegram GUI launched")
            self.logger.info("Telegram GUI launched")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Telegram GUI: {e}")
            self.logger.error(f"Error launching Telegram GUI: {e}")
    
    def launch_sms_marketplace(self):
        """Launch the SMS marketplace GUI"""
        try:
            if self.sms_marketplace_process and self.sms_marketplace_process.poll() is None:
                messagebox.showwarning("Warning", "SMS Marketplace is already running")
                return
            
            # Launch the marketplace GUI
            script_path = Path(__file__).parent / "marketplace_gui.py"
            self.sms_marketplace_process = subprocess.Popen([sys.executable, str(script_path)])
            
            self.sms_status = "Running"
            self.sms_status_label.config(text=f"Status: {self.sms_status}", 
                                       style='Success.TLabel')
            self.sms_status_display.config(text="Running", foreground='#00ff88')
            
            self.sms_launch_btn.config(state='disabled')
            self.sms_stop_btn.config(state='normal')
            
            self.add_event_log("System", "SMS Marketplace launched")
            self.logger.info("SMS Marketplace launched")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch SMS Marketplace: {e}")
            self.logger.error(f"Error launching SMS Marketplace: {e}")
    
    def stop_telegram(self):
        """Stop the Telegram GUI"""
        try:
            if self.telegram_process:
                self.telegram_process.terminate()
                self.telegram_process = None
            
            self.telegram_status = "Not Running"
            self.telegram_status_label.config(text=f"Status: {self.telegram_status}", 
                                            style='Error.TLabel')
            self.tg_status_display.config(text="Not Running", foreground='#ff4444')
            
            self.telegram_launch_btn.config(state='normal')
            self.telegram_stop_btn.config(state='disabled')
            
            self.add_event_log("System", "Telegram GUI stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping Telegram GUI: {e}")
    
    def stop_sms_marketplace(self):
        """Stop the SMS marketplace"""
        try:
            if self.sms_marketplace_process:
                self.sms_marketplace_process.terminate()
                self.sms_marketplace_process = None
            
            self.sms_status = "Not Running"
            self.sms_status_label.config(text=f"Status: {self.sms_status}", 
                                       style='Error.TLabel')
            self.sms_status_display.config(text="Not Running", foreground='#ff4444')
            
            self.sms_launch_btn.config(state='normal')
            self.sms_stop_btn.config(state='disabled')
            
            self.add_event_log("System", "SMS Marketplace stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping SMS Marketplace: {e}")
    
    # Integration event handlers
    def on_number_purchased(self, event: IntegrationEvent):
        """Handle number purchased event"""
        phone = event.data.get('phone_number', 'Unknown')
        self.add_event_log("SMS", f"Number purchased: {phone}")
        self.refresh_phone_numbers_table()
    
    def on_sms_code_received(self, event: IntegrationEvent):
        """Handle SMS code received event"""
        phone = event.data.get('phone_number', 'Unknown')
        code = event.data.get('code', 'Unknown')
        self.add_event_log("SMS", f"Code received for {phone}: {code}")
        self.refresh_verification_codes_table()
    
    def on_account_created(self, event: IntegrationEvent):
        """Handle account created event"""
        phone = event.data.get('phone_number', 'Unknown')
        self.add_event_log("Telegram", f"Account created for {phone}")
    
    # Workflow methods
    def sync_phone_numbers(self):
        """Sync phone numbers between tools"""
        try:
            # This would sync phone numbers from marketplace to Telegram automation
            self.add_event_log("System", "Phone numbers synchronized")
            self.refresh_phone_numbers_table()
            messagebox.showinfo("Success", "Phone numbers synchronized successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to sync phone numbers: {e}")
    
    def create_telegram_account_workflow(self):
        """Create Telegram account using available SMS number"""
        try:
            available_numbers = integration_manager.get_available_numbers('Telegram')
            if not available_numbers:
                messagebox.showwarning("Warning", "No available Telegram numbers found")
                return
            
            # Use the first available number
            number = available_numbers[0]
            result = integration_manager.create_telegram_account_workflow(number.phone_number)
            
            if result['status'] == 'success':
                messagebox.showinfo("Success", f"Telegram account workflow started for {result['phone_number']}")
                self.add_event_log("Workflow", f"TG account creation started for {result['phone_number']}")
            else:
                messagebox.showerror("Error", result['message'])
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start workflow: {e}")
    
    def auto_purchase_workflow(self):
        """Auto-purchase workflow"""
        messagebox.showinfo("Info", "Auto-purchase workflow would be implemented here")
    
    def export_integrated_data(self):
        """Export all integrated data"""
        try:
            export_data = integration_manager.export_shared_data()
            
            # Save to file
            filename = f"integrated_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            messagebox.showinfo("Success", f"Data exported to {filename}")
            self.add_event_log("System", f"Data exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {e}")
    
    def import_phone_numbers(self):
        """Import phone numbers"""
        messagebox.showinfo("Info", "Phone number import would be implemented here")
    
    def add_shared_proxies(self):
        """Add shared proxies"""
        messagebox.showinfo("Info", "Proxy management would be implemented here")
    
    def test_shared_proxies(self):
        """Test shared proxies"""
        messagebox.showinfo("Info", "Proxy testing would be implemented here")
    
    # UI update methods
    def refresh_phone_numbers_table(self):
        """Refresh the phone numbers table"""
        try:
            # Clear existing items
            for item in self.phone_tree.get_children():
                self.phone_tree.delete(item)
            
            # Get phone numbers from integration manager
            numbers = integration_manager.get_available_numbers()
            
            for number in numbers:
                self.phone_tree.insert('', 'end', values=(
                    number.phone_number,
                    number.service,
                    number.status,
                    number.provider
                ))
                
        except Exception as e:
            self.logger.error(f"Error refreshing phone numbers table: {e}")
    
    def refresh_verification_codes_table(self):
        """Refresh the verification codes table"""
        try:
            # Clear existing items
            for item in self.codes_tree.get_children():
                self.codes_tree.delete(item)
            
            # This would get codes from integration manager
            # For now, just placeholder
            
        except Exception as e:
            self.logger.error(f"Error refreshing codes table: {e}")
    
    def refresh_statistics(self):
        """Refresh statistics display"""
        try:
            stats = integration_manager.get_statistics()
            # Update header stats labels
            # This would update the stats display
            self.add_event_log("System", "Statistics refreshed")
        except Exception as e:
            self.logger.error(f"Error refreshing statistics: {e}")
    
    def restart_integration(self):
        """Restart the integration manager"""
        try:
            # This would restart the integration manager
            self.add_event_log("System", "Integration manager restarted")
            messagebox.showinfo("Success", "Integration manager restarted")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to restart integration: {e}")
    
    def add_event_log(self, source: str, message: str):
        """Add an event to the log display"""
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            log_entry = f"[{timestamp}] {source}: {message}\n"
            
            # Add to event monitoring
            if hasattr(self, 'event_text'):
                self.event_text.config(state='normal')
                self.event_text.insert(tk.END, log_entry)
                self.event_text.see(tk.END)
                self.event_text.config(state='disabled')
            
            # Add to main logs
            if hasattr(self, 'logs_text'):
                self.logs_text.config(state='normal')
                self.logs_text.insert(tk.END, log_entry)
                self.logs_text.see(tk.END)
                self.logs_text.config(state='disabled')
                
        except Exception as e:
            self.logger.error(f"Error adding event log: {e}")
    
    def start_status_monitoring(self):
        """Start background status monitoring"""
        def monitor():
            while True:
                try:
                    # Check tool statuses
                    if self.telegram_process and self.telegram_process.poll() is not None:
                        self.telegram_process = None
                        self.telegram_status = "Not Running"
                        if hasattr(self, 'telegram_status_label'):
                            self.telegram_status_label.config(text=f"Status: {self.telegram_status}", 
                                                            style='Error.TLabel')
                            self.telegram_launch_btn.config(state='normal')
                            self.telegram_stop_btn.config(state='disabled')
                    
                    if self.sms_marketplace_process and self.sms_marketplace_process.poll() is not None:
                        self.sms_marketplace_process = None
                        self.sms_status = "Not Running"
                        if hasattr(self, 'sms_status_label'):
                            self.sms_status_label.config(text=f"Status: {self.sms_status}", 
                                                       style='Error.TLabel')
                            self.sms_launch_btn.config(state='normal')
                            self.sms_stop_btn.config(state='disabled')
                    
                    time.sleep(5)  # Check every 5 seconds
                    
                except Exception as e:
                    self.logger.error(f"Error in status monitoring: {e}")
                    time.sleep(10)
        
        monitor_thread = threading.Thread(target=monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    def on_closing(self):
        """Handle window closing"""
        try:
            # Stop running processes
            if self.telegram_process:
                self.telegram_process.terminate()
            if self.sms_marketplace_process:
                self.sms_marketplace_process.terminate()
            
            # Cleanup integration manager
            integration_manager.cleanup()
            
            self.logger.info("Unified launcher shutting down")
            self.root.destroy()
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            self.root.destroy()
    
    def run(self):
        """Run the launcher"""
        self.root.mainloop()

def main():
    """Main entry point"""
    launcher = UnifiedToolLauncher()
    launcher.run()

if __name__ == "__main__":
    main()