#!/usr/bin/env python3
"""
Unified Integration Manager
==========================
Central hub for seamless integration between Telegram Automation and SMS Marketplace tools.
Handles data sharing, cross-communication, and unified workflows.

Author: Enhanced by AI Assistant
Version: 3.0.0
"""

import sqlite3
import json
import os
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import queue
import asyncio

class ToolType(Enum):
    TELEGRAM = "telegram"
    SMS_MARKETPLACE = "sms_marketplace"

class EventType(Enum):
    NUMBER_PURCHASED = "number_purchased"
    NUMBER_VERIFIED = "number_verified" 
    ACCOUNT_CREATED = "account_created"
    SCRAPE_COMPLETED = "scrape_completed"
    SMS_CODE_RECEIVED = "sms_code_received"
    PROXY_STATUS_CHANGED = "proxy_status_changed"

@dataclass
class IntegrationEvent:
    """Represents an event that can be shared between tools"""
    event_type: EventType
    source_tool: ToolType
    data: Dict[str, Any]
    timestamp: datetime
    event_id: str = None

@dataclass 
class SharedPhoneNumber:
    """Phone number that can be shared between tools"""
    phone_number: str
    country_code: str
    service: str
    provider: str
    purchase_date: datetime
    status: str  # available, in_use, verified, expired
    verification_codes: List[str] = None
    telegram_account_id: str = None
    cost: float = 0.0
    
@dataclass
class UnifiedSession:
    """Unified session data shared between tools"""
    session_id: str
    phone_number: str
    telegram_session_name: str = None
    sms_provider_data: Dict = None
    proxy_settings: Dict = None
    created_at: datetime = None
    last_used: datetime = None
    status: str = "active"

class UnifiedIntegrationManager:
    """Central manager for tool integration and data sharing"""
    
    def __init__(self, db_path: str = "unified_automation.db"):
        self.db_path = db_path
        self.event_queue = queue.Queue()
        self.event_handlers: Dict[EventType, List[Callable]] = {}
        self.tool_connections: Dict[ToolType, Any] = {}
        self.shared_data: Dict[str, Any] = {}
        self.running = False
        self._event_processor_thread = None
        
        # Initialize database
        self.setup_database()
        
        # Setup logging
        self.setup_logging()
        
        # Start event processing
        self.start_event_processing()
        
        self.logger.info("Unified Integration Manager initialized")
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('unified_integration.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_database(self):
        """Initialize unified database schema"""
        conn = sqlite3.connect(self.db_path, timeout=30, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        cursor = conn.cursor()
        
        # Shared phone numbers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shared_phone_numbers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT UNIQUE NOT NULL,
                country_code TEXT NOT NULL,
                service TEXT NOT NULL,
                provider TEXT NOT NULL,
                purchase_date TEXT NOT NULL,
                status TEXT DEFAULT 'available',
                telegram_account_id TEXT,
                cost REAL DEFAULT 0.0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Verification codes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS verification_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                code TEXT NOT NULL,
                service TEXT NOT NULL,
                received_at TEXT NOT NULL,
                used BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (phone_number) REFERENCES shared_phone_numbers (phone_number)
            )
        """)
        
        # Unified sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS unified_sessions (
                session_id TEXT PRIMARY KEY,
                phone_number TEXT NOT NULL,
                telegram_session_name TEXT,
                sms_provider_data TEXT,
                proxy_settings TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_used TEXT DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (phone_number) REFERENCES shared_phone_numbers (phone_number)
            )
        """)
        
        # Integration events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS integration_events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                source_tool TEXT NOT NULL,
                event_data TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                processed BOOLEAN DEFAULT FALSE
            )
        """)
        
        # Shared proxy settings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shared_proxies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                host TEXT NOT NULL,
                port INTEGER NOT NULL,
                username TEXT,
                password TEXT,
                proxy_type TEXT DEFAULT 'socks5',
                status TEXT DEFAULT 'active',
                last_tested TEXT,
                response_time REAL,
                success_rate REAL DEFAULT 100.0,
                assigned_to TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def register_tool(self, tool_type: ToolType, tool_instance: Any):
        """Register a tool for integration"""
        self.tool_connections[tool_type] = tool_instance
        self.logger.info(f"Registered {tool_type.value} tool")
    
    def register_event_handler(self, event_type: EventType, handler: Callable):
        """Register an event handler for cross-tool communication"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        self.logger.info(f"Registered handler for {event_type.value}")
    
    def emit_event(self, event: IntegrationEvent):
        """Emit an event to be processed by registered handlers"""
        if not event.event_id:
            event.event_id = f"{event.source_tool.value}_{int(time.time())}_{id(event)}"
        
        # Add to processing queue
        self.event_queue.put(event)
        
        # Store in database
        self._store_event(event)
        
        self.logger.info(f"Event emitted: {event.event_type.value} from {event.source_tool.value}")
    
    def _store_event(self, event: IntegrationEvent):
        """Store event in database"""
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO integration_events 
            (event_id, event_type, source_tool, event_data, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (event.event_id, event.event_type.value, event.source_tool.value,
              json.dumps(event.data), event.timestamp.isoformat()))
        conn.commit()
        conn.close()
    
    def start_event_processing(self):
        """Start background event processing"""
        if self._event_processor_thread and self._event_processor_thread.is_alive():
            return
        
        self.running = True
        self._event_processor_thread = threading.Thread(target=self._process_events)
        self._event_processor_thread.daemon = True
        self._event_processor_thread.start()
    
    def stop_event_processing(self):
        """Stop background event processing"""
        self.running = False
        if self._event_processor_thread:
            self._event_processor_thread.join(timeout=5)
    
    def _process_events(self):
        """Background event processor"""
        while self.running:
            try:
                event = self.event_queue.get(timeout=1)
                self._handle_event(event)
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing event: {e}")
    
    def _handle_event(self, event: IntegrationEvent):
        """Handle an integration event"""
        if event.event_type in self.event_handlers:
            for handler in self.event_handlers[event.event_type]:
                try:
                    handler(event)
                except Exception as e:
                    self.logger.error(f"Error in event handler: {e}")
    
    # Phone Number Management
    def add_phone_number(self, phone_data: SharedPhoneNumber) -> bool:
        """Add a phone number to shared pool"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO shared_phone_numbers 
                (phone_number, country_code, service, provider, purchase_date, status, cost)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (phone_data.phone_number, phone_data.country_code, phone_data.service,
                  phone_data.provider, phone_data.purchase_date.isoformat(),
                  phone_data.status, phone_data.cost))
            conn.commit()
            conn.close()
            
            # Emit event
            self.emit_event(IntegrationEvent(
                event_type=EventType.NUMBER_PURCHASED,
                source_tool=ToolType.SMS_MARKETPLACE,
                data=asdict(phone_data),
                timestamp=datetime.now()
            ))
            
            return True
        except Exception as e:
            self.logger.error(f"Error adding phone number: {e}")
            return False
    
    def get_available_numbers(self, service: str = None) -> List[SharedPhoneNumber]:
        """Get available phone numbers for use"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            query = "SELECT * FROM shared_phone_numbers WHERE status = 'available'"
            params = []
            
            if service:
                query += " AND service = ?"
                params.append(service)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            numbers = []
            for row in rows:
                numbers.append(SharedPhoneNumber(
                    phone_number=row[1],
                    country_code=row[2],
                    service=row[3],
                    provider=row[4],
                    purchase_date=datetime.fromisoformat(row[5]),
                    status=row[6],
                    telegram_account_id=row[7],
                    cost=row[8] or 0.0
                ))
            
            return numbers
        except Exception as e:
            self.logger.error(f"Error getting available numbers: {e}")
            return []
    
    def reserve_number(self, phone_number: str, telegram_account_id: str) -> bool:
        """Reserve a phone number for Telegram account creation"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE shared_phone_numbers 
                SET status = 'in_use', telegram_account_id = ?, updated_at = CURRENT_TIMESTAMP
                WHERE phone_number = ? AND status = 'available'
            """, (telegram_account_id, phone_number))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return True
            
            conn.close()
            return False
        except Exception as e:
            self.logger.error(f"Error reserving number: {e}")
            return False
    
    def add_verification_code(self, phone_number: str, code: str, service: str):
        """Add a verification code for a phone number"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO verification_codes 
                (phone_number, code, service, received_at)
                VALUES (?, ?, ?, ?)
            """, (phone_number, code, service, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            
            # Emit event
            self.emit_event(IntegrationEvent(
                event_type=EventType.SMS_CODE_RECEIVED,
                source_tool=ToolType.SMS_MARKETPLACE,
                data={
                    'phone_number': phone_number,
                    'code': code,
                    'service': service
                },
                timestamp=datetime.now()
            ))
            
        except Exception as e:
            self.logger.error(f"Error adding verification code: {e}")
    
    def get_verification_codes(self, phone_number: str, unused_only: bool = True) -> List[Dict]:
        """Get verification codes for a phone number"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            query = "SELECT * FROM verification_codes WHERE phone_number = ?"
            params = [phone_number]
            
            if unused_only:
                query += " AND used = FALSE"
            
            query += " ORDER BY received_at DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            codes = []
            for row in rows:
                codes.append({
                    'id': row[0],
                    'phone_number': row[1],
                    'code': row[2],
                    'service': row[3],
                    'received_at': row[4],
                    'used': bool(row[5])
                })
            
            return codes
        except Exception as e:
            self.logger.error(f"Error getting verification codes: {e}")
            return []
    
    def mark_code_used(self, code_id: int):
        """Mark a verification code as used"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute("UPDATE verification_codes SET used = TRUE WHERE id = ?", (code_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Error marking code as used: {e}")
    
    # Proxy Management
    def add_shared_proxy(self, host: str, port: int, username: str = None, 
                        password: str = None, proxy_type: str = 'socks5'):
        """Add a proxy to the shared pool"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO shared_proxies 
                (host, port, username, password, proxy_type)
                VALUES (?, ?, ?, ?, ?)
            """, (host, port, username, password, proxy_type))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"Error adding proxy: {e}")
            return False
    
    def get_available_proxies(self) -> List[Dict]:
        """Get available proxies"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM shared_proxies WHERE status = 'active'")
            rows = cursor.fetchall()
            conn.close()
            
            proxies = []
            for row in rows:
                proxies.append({
                    'id': row[0],
                    'host': row[1],
                    'port': row[2],
                    'username': row[3],
                    'password': row[4],
                    'proxy_type': row[5],
                    'status': row[6],
                    'response_time': row[8],
                    'success_rate': row[9]
                })
            
            return proxies
        except Exception as e:
            self.logger.error(f"Error getting proxies: {e}")
            return []
    
    # Unified Session Management
    def create_unified_session(self, session_data: UnifiedSession) -> bool:
        """Create a unified session spanning both tools"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO unified_sessions 
                (session_id, phone_number, telegram_session_name, sms_provider_data, 
                 proxy_settings, created_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (session_data.session_id, session_data.phone_number,
                  session_data.telegram_session_name, 
                  json.dumps(session_data.sms_provider_data) if session_data.sms_provider_data else None,
                  json.dumps(session_data.proxy_settings) if session_data.proxy_settings else None,
                  session_data.created_at.isoformat() if session_data.created_at else datetime.now().isoformat(),
                  session_data.status))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"Error creating unified session: {e}")
            return False
    
    def get_unified_session(self, session_id: str) -> Optional[UnifiedSession]:
        """Get a unified session by ID"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM unified_sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            return UnifiedSession(
                session_id=row[0],
                phone_number=row[1],
                telegram_session_name=row[2],
                sms_provider_data=json.loads(row[3]) if row[3] else None,
                proxy_settings=json.loads(row[4]) if row[4] else None,
                created_at=datetime.fromisoformat(row[5]),
                last_used=datetime.fromisoformat(row[6]) if row[6] else None,
                status=row[7]
            )
        except Exception as e:
            self.logger.error(f"Error getting unified session: {e}")
            return None
    
    # Cross-Tool Automation Workflows
    def create_telegram_account_workflow(self, sms_number_id: str, proxy_settings: Dict = None) -> Dict:
        """Automated workflow to create Telegram account using SMS marketplace number"""
        workflow_id = f"tg_create_{int(time.time())}"
        
        try:
            # Get phone number details
            available_numbers = self.get_available_numbers()
            target_number = None
            
            for number in available_numbers:
                if str(id(number)) == sms_number_id or number.phone_number == sms_number_id:
                    target_number = number
                    break
            
            if not target_number:
                return {'status': 'error', 'message': 'Phone number not available'}
            
            # Reserve the number
            if not self.reserve_number(target_number.phone_number, workflow_id):
                return {'status': 'error', 'message': 'Failed to reserve phone number'}
            
            # Create unified session
            session = UnifiedSession(
                session_id=workflow_id,
                phone_number=target_number.phone_number,
                telegram_session_name=f"session_{workflow_id}",
                sms_provider_data={'provider': target_number.provider, 'service': target_number.service},
                proxy_settings=proxy_settings,
                created_at=datetime.now()
            )
            
            self.create_unified_session(session)
            
            # Emit workflow event
            self.emit_event(IntegrationEvent(
                event_type=EventType.ACCOUNT_CREATED,
                source_tool=ToolType.TELEGRAM,
                data={
                    'workflow_id': workflow_id,
                    'phone_number': target_number.phone_number,
                    'session_name': session.telegram_session_name
                },
                timestamp=datetime.now()
            ))
            
            return {
                'status': 'success',
                'workflow_id': workflow_id,
                'phone_number': target_number.phone_number,
                'session_name': session.telegram_session_name
            }
            
        except Exception as e:
            self.logger.error(f"Error in create_telegram_account_workflow: {e}")
            return {'status': 'error', 'message': str(e)}
    
    # Data Export/Import for Tool Synchronization
    def export_shared_data(self, data_types: List[str] = None) -> Dict:
        """Export shared data for synchronization"""
        if data_types is None:
            data_types = ['phone_numbers', 'proxies', 'sessions', 'verification_codes']
        
        export_data = {}
        
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            if 'phone_numbers' in data_types:
                cursor.execute("SELECT * FROM shared_phone_numbers")
                export_data['phone_numbers'] = cursor.fetchall()
            
            if 'proxies' in data_types:
                cursor.execute("SELECT * FROM shared_proxies")
                export_data['proxies'] = cursor.fetchall()
            
            if 'sessions' in data_types:
                cursor.execute("SELECT * FROM unified_sessions")
                export_data['sessions'] = cursor.fetchall()
            
            if 'verification_codes' in data_types:
                cursor.execute("SELECT * FROM verification_codes")
                export_data['verification_codes'] = cursor.fetchall()
            
            conn.close()
            return export_data
            
        except Exception as e:
            self.logger.error(f"Error exporting shared data: {e}")
            return {}
    
    def get_statistics(self) -> Dict:
        """Get integration statistics"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            stats = {}
            
            # Phone numbers stats
            cursor.execute("SELECT status, COUNT(*) FROM shared_phone_numbers GROUP BY status")
            stats['phone_numbers'] = dict(cursor.fetchall())
            
            # Verification codes stats
            cursor.execute("SELECT COUNT(*) FROM verification_codes")
            stats['total_codes'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM verification_codes WHERE used = FALSE")
            stats['unused_codes'] = cursor.fetchone()[0]
            
            # Proxies stats
            cursor.execute("SELECT status, COUNT(*) FROM shared_proxies GROUP BY status")
            stats['proxies'] = dict(cursor.fetchall())
            
            # Sessions stats
            cursor.execute("SELECT status, COUNT(*) FROM unified_sessions GROUP BY status")
            stats['sessions'] = dict(cursor.fetchall())
            
            conn.close()
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {}
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_event_processing()
        self.logger.info("Integration manager cleaned up")

# Global integration manager instance
integration_manager = UnifiedIntegrationManager()