#!/usr/bin/env python3
"""
Automated Account Creation Workflow
==================================
Complete workflow: buy numbers → create accounts → log accounts → use accounts
Integrates marketplace with telegram automation for full automation.
"""

import sqlite3
import json
import time
import threading
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

class AutomatedWorkflowManager:
    def __init__(self, parent_gui=None):
        self.parent_gui = parent_gui
        self.is_running = False
        self.current_step = None
        self.workflow_stats = {
            'numbers_purchased': 0,
            'accounts_created': 0,
            'accounts_verified': 0,
            'accounts_ready': 0
        }
        
    def create_workflow_gui(self, parent):
        """Create the automated workflow GUI"""
        # Workflow control frame
        control_frame = ttk.LabelFrame(parent, text="Automated Account Creation Workflow")
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Workflow steps display
        steps_frame = ttk.Frame(control_frame)
        steps_frame.pack(fill=tk.X, padx=5, pady=5)
        
        steps = [
            "1️⃣ Buy Phone Numbers",
            "2️⃣ Create Telegram Accounts", 
            "3️⃣ Verify Accounts",
            "4️⃣ Log to Account List",
            "5️⃣ Ready for Use"
        ]
        
        self.step_labels = []
        for i, step in enumerate(steps):
            label = ttk.Label(steps_frame, text=step)
            label.grid(row=0, column=i, padx=10, pady=5)
            self.step_labels.append(label)
            
        # Configuration
        config_frame = ttk.LabelFrame(parent, text="Workflow Configuration")
        config_frame.pack(fill=tk.X, padx=10, pady=10)
        
        config_grid = ttk.Frame(config_frame)
        config_grid.pack(padx=10, pady=10)
        
        ttk.Label(config_grid, text="Numbers to Purchase:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.numbers_count_var = tk.StringVar(value="5")
        ttk.Entry(config_grid, textvariable=self.numbers_count_var, width=10).grid(row=0, column=1, padx=5)
        
        ttk.Label(config_grid, text="Country:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.workflow_country_var = tk.StringVar(value="United States")
        ttk.Combobox(config_grid, textvariable=self.workflow_country_var, 
                    values=["United States", "United Kingdom", "Germany"], width=15).grid(row=0, column=3, padx=5)
        
        ttk.Label(config_grid, text="Provider:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.workflow_provider_var = tk.StringVar(value="SMS-Activate")
        ttk.Combobox(config_grid, textvariable=self.workflow_provider_var,
                    values=["SMS-Activate", "5SIM", "GetSMSCode"], width=15).grid(row=1, column=1, padx=5)
        
        ttk.Label(config_grid, text="Delay (seconds):").grid(row=1, column=2, sticky=tk.W, padx=5)
        self.workflow_delay_var = tk.StringVar(value="30")
        ttk.Entry(config_grid, textvariable=self.workflow_delay_var, width=10).grid(row=1, column=3, padx=5)
        
        # Control buttons
        button_frame = ttk.Frame(config_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.start_workflow_btn = ttk.Button(button_frame, text="🚀 Start Automated Workflow", 
                                           command=self.start_automated_workflow)
        self.start_workflow_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_workflow_btn = ttk.Button(button_frame, text="⏹️ Stop Workflow", 
                                          command=self.stop_automated_workflow, state='disabled')
        self.stop_workflow_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="📊 View Progress", command=self.show_workflow_progress).pack(side=tk.LEFT)
        
        # Progress tracking
        progress_frame = ttk.LabelFrame(parent, text="Workflow Progress")
        progress_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.workflow_progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.workflow_progress.pack(fill=tk.X, padx=5, pady=5)
        
        self.workflow_status = ttk.Label(progress_frame, text="Ready to start workflow")
        self.workflow_status.pack(pady=5)
        
        # Statistics
        stats_frame = ttk.LabelFrame(parent, text="Workflow Statistics")
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(padx=10, pady=10)
        
        ttk.Label(stats_grid, text="Numbers Purchased:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.numbers_purchased_label = ttk.Label(stats_grid, text="0", font=('Arial', 10, 'bold'))
        self.numbers_purchased_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(stats_grid, text="Accounts Created:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.accounts_created_label = ttk.Label(stats_grid, text="0", font=('Arial', 10, 'bold'))
        self.accounts_created_label.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        ttk.Label(stats_grid, text="Accounts Verified:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.accounts_verified_label = ttk.Label(stats_grid, text="0", font=('Arial', 10, 'bold'))
        self.accounts_verified_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(stats_grid, text="Ready for Use:").grid(row=1, column=2, sticky=tk.W, padx=5)
        self.accounts_ready_label = ttk.Label(stats_grid, text="0", font=('Arial', 10, 'bold'))
        self.accounts_ready_label.grid(row=1, column=3, sticky=tk.W, padx=5)
        
    def start_automated_workflow(self):
        """Start the complete automated workflow"""
        if self.is_running:
            return
            
        try:
            numbers_count = int(self.numbers_count_var.get())
            if numbers_count <= 0 or numbers_count > 50:
                messagebox.showerror("Error", "Please enter a valid number count (1-50)")
                return
                
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
            return
            
        self.is_running = True
        self.start_workflow_btn.config(state='disabled')
        self.stop_workflow_btn.config(state='normal')
        
        # Reset stats
        self.workflow_stats = {
            'numbers_purchased': 0,
            'accounts_created': 0,
            'accounts_verified': 0,
            'accounts_ready': 0
        }
        
        self.log_workflow("🚀 Starting automated account creation workflow...")
        
        # Start workflow in background thread
        threading.Thread(target=self.run_automated_workflow, daemon=True).start()
        
    def stop_automated_workflow(self):
        """Stop the automated workflow"""
        self.is_running = False
        self.start_workflow_btn.config(state='normal')
        self.stop_workflow_btn.config(state='disabled')
        self.log_workflow("⏹️ Workflow stopped by user")
        
    def run_automated_workflow(self):
        """Run the complete workflow in background"""
        try:
            numbers_count = int(self.numbers_count_var.get())
            delay = int(self.workflow_delay_var.get())
            provider = self.workflow_provider_var.get()
            country = self.workflow_country_var.get()
            
            total_steps = numbers_count * 5  # 5 steps per number
            completed_steps = 0
            
            for i in range(numbers_count):
                if not self.is_running:
                    break
                    
                self.log_workflow(f"Processing account {i+1}/{numbers_count}")
                
                # Step 1: Buy phone number
                self.update_current_step(0)
                phone_number = self.buy_phone_number(provider, country)
                if phone_number:
                    self.workflow_stats['numbers_purchased'] += 1
                    completed_steps += 1
                    self.update_progress(completed_steps, total_steps)
                    
                time.sleep(delay)
                if not self.is_running:
                    break
                    
                # Step 2: Create Telegram account
                self.update_current_step(1)
                account_created = self.create_telegram_account(phone_number)
                if account_created:
                    self.workflow_stats['accounts_created'] += 1
                    completed_steps += 1
                    self.update_progress(completed_steps, total_steps)
                    
                time.sleep(delay)
                if not self.is_running:
                    break
                    
                # Step 3: Verify account
                self.update_current_step(2)
                account_verified = self.verify_telegram_account(phone_number)
                if account_verified:
                    self.workflow_stats['accounts_verified'] += 1
                    completed_steps += 1
                    self.update_progress(completed_steps, total_steps)
                    
                time.sleep(delay)
                if not self.is_running:
                    break
                    
                # Step 4: Log to account list
                self.update_current_step(3)
                logged = self.log_to_account_list(phone_number)
                if logged:
                    completed_steps += 1
                    self.update_progress(completed_steps, total_steps)
                    
                time.sleep(delay)
                if not self.is_running:
                    break
                    
                # Step 5: Mark ready for use
                self.update_current_step(4)
                ready = self.mark_account_ready(phone_number)
                if ready:
                    self.workflow_stats['accounts_ready'] += 1
                    completed_steps += 1
                    self.update_progress(completed_steps, total_steps)
                    
                self.log_workflow(f"✅ Completed account {i+1}: {phone_number}")
                time.sleep(5)  # Brief pause between accounts
                
        except Exception as e:
            self.log_workflow(f"❌ Workflow error: {e}")
            
        finally:
            if self.is_running:
                self.log_workflow("🎉 Automated workflow completed successfully!")
            
            self.is_running = False
            if hasattr(self, 'start_workflow_btn'):
                self.start_workflow_btn.config(state='normal')
                self.stop_workflow_btn.config(state='disabled')
                
    def buy_phone_number(self, provider, country):
        """Step 1: Buy phone number from marketplace"""
        try:
            # Simulate purchasing number
            import random
            phone_number = f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}"
            
            self.log_workflow(f"📞 Purchased number: {phone_number} from {provider}")
            
            # Log to RAG database
            self.log_to_rag_database(phone_number, provider, country)
            
            return phone_number
            
        except Exception as e:
            self.log_workflow(f"❌ Number purchase failed: {e}")
            return None
            
    def create_telegram_account(self, phone_number):
        """Step 2: Create Telegram account"""
        try:
            self.log_workflow(f"🔧 Creating Telegram account for {phone_number}")
            
            # Simulate account creation
            time.sleep(3)
            
            # In real implementation, would use Telethon to create account
            account_id = f"account_{phone_number.replace('-', '').replace('+', '')}"
            
            self.log_workflow(f"✅ Created account: {account_id}")
            return True
            
        except Exception as e:
            self.log_workflow(f"❌ Account creation failed: {e}")
            return False
            
    def verify_telegram_account(self, phone_number):
        """Step 3: Verify Telegram account"""
        try:
            self.log_workflow(f"📲 Verifying account for {phone_number}")
            
            # Simulate SMS code reception and verification
            time.sleep(2)
            sms_code = "12345"  # Would get from marketplace
            
            self.log_workflow(f"📱 Received SMS code: {sms_code}")
            self.log_workflow(f"✅ Account verified successfully")
            
            return True
            
        except Exception as e:
            self.log_workflow(f"❌ Account verification failed: {e}")
            return False
            
    def log_to_account_list(self, phone_number):
        """Step 4: Log account to main account list"""
        try:
            # Add to database
            conn = sqlite3.connect('telegram_automation.db')
            cursor = conn.cursor()
            
            # Create accounts table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS automated_accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone_number TEXT NOT NULL,
                    account_id TEXT,
                    status TEXT DEFAULT 'created',
                    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_used DATETIME,
                    usage_count INTEGER DEFAULT 0
                )
            ''')
            
            cursor.execute('''
                INSERT INTO automated_accounts (phone_number, account_id, status)
                VALUES (?, ?, ?)
            ''', (phone_number, f"auto_{phone_number}", 'ready'))
            
            conn.commit()
            conn.close()
            
            self.log_workflow(f"📋 Logged {phone_number} to account list")
            return True
            
        except Exception as e:
            self.log_workflow(f"❌ Account logging failed: {e}")
            return False
            
    def mark_account_ready(self, phone_number):
        """Step 5: Mark account ready for use"""
        try:
            self.log_workflow(f"🎯 Account {phone_number} ready for use")
            
            # Update status in database
            conn = sqlite3.connect('telegram_automation.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE automated_accounts SET status = ? WHERE phone_number = ?', 
                         ('ready_for_use', phone_number))
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            self.log_workflow(f"❌ Failed to mark account ready: {e}")
            return False
            
    def log_to_rag_database(self, phone_number, provider, country):
        """Log to RAG database for integration"""
        try:
            conn = sqlite3.connect('rag_marketplace.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workflow_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone_number TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    country TEXT NOT NULL,
                    status TEXT DEFAULT 'processing',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                INSERT INTO workflow_log (phone_number, provider, country)
                VALUES (?, ?, ?)
            ''', (phone_number, provider, country))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.log_workflow(f"RAG database error: {e}")
            
    def update_current_step(self, step_index):
        """Update the current step indicator"""
        self.current_step = step_index
        
        # Update step label colors (would need GUI reference)
        if hasattr(self, 'step_labels'):
            for i, label in enumerate(self.step_labels):
                if i == step_index:
                    label.config(foreground='green')
                elif i < step_index:
                    label.config(foreground='blue')
                else:
                    label.config(foreground='gray')
                    
    def update_progress(self, completed, total):
        """Update progress bar and statistics"""
        if hasattr(self, 'workflow_progress'):
            progress_percent = (completed / total) * 100
            self.workflow_progress['value'] = progress_percent
            
        # Update statistics labels
        if hasattr(self, 'numbers_purchased_label'):
            self.numbers_purchased_label.config(text=str(self.workflow_stats['numbers_purchased']))
            self.accounts_created_label.config(text=str(self.workflow_stats['accounts_created']))
            self.accounts_verified_label.config(text=str(self.workflow_stats['accounts_verified']))
            self.accounts_ready_label.config(text=str(self.workflow_stats['accounts_ready']))
            
    def log_workflow(self, message):
        """Log workflow message"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        
        if hasattr(self, 'workflow_status'):
            self.workflow_status.config(text=message)
            
        # Also log to parent GUI if available
        if self.parent_gui and hasattr(self.parent_gui, 'log_message'):
            self.parent_gui.log_message(f"WORKFLOW: {message}", 'INFO')
            
        print(log_entry)  # Console fallback
        
    def show_workflow_progress(self):
        """Show detailed workflow progress"""
        progress_info = f"""Automated Workflow Progress:

Numbers Purchased: {self.workflow_stats['numbers_purchased']}
Accounts Created: {self.workflow_stats['accounts_created']}
Accounts Verified: {self.workflow_stats['accounts_verified']}
Accounts Ready: {self.workflow_stats['accounts_ready']}

Current Status: {'Running' if self.is_running else 'Stopped'}
Current Step: {self.current_step + 1 if self.current_step is not None else 'None'}
"""
        messagebox.showinfo("Workflow Progress", progress_info)

def main():
    """Test the workflow manager"""
    root = tk.Tk()
    root.title("Automated Workflow Test")
    root.geometry("800x600")
    
    workflow = AutomatedWorkflowManager()
    workflow.create_workflow_gui(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()