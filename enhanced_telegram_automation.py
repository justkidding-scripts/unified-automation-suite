#!/usr/bin/env python3
"""
Enhanced Telegram Automation Framework
=====================================
A robust, anti-detection system for Telegram scraping, bulk inviting, and mass messaging.
Features continuous operation without hitting walls.

Author: Enhanced by AI Assistant
Version: 2.0.0
"""

import asyncio
import json
import os
import random
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any
import configparser
from dataclasses import dataclass, asdict
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor

# Telegram imports
from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetParticipantsRequest, InviteToChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest, GetFullChatRequest, CheckChatInviteRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.network.connection import ConnectionTcpMTProxyRandomizedIntermediate
from telethon.errors import (
    FloodWaitError, UserPrivacyRestrictedError, UserNotMutualContactError,
    SessionPasswordNeededError, PhoneCodeInvalidError, PeerFloodError,
    ChatWriteForbiddenError, UserBannedInChannelError
)

# Enhanced imports for anti-detection
import socks
import socket
from fake_useragent import UserAgent
import aiofiles
import asyncpg
from selenium_scraper import scrape_group_members_via_web

@dataclass
class TelegramAccount:
    """Represents a Telegram account configuration"""
    api_id: int
    api_hash: str
    phone_number: str
    session_name: str
    proxy_host: Optional[str] = None
    proxy_port: Optional[int] = None
    proxy_username: Optional[str] = None
    proxy_password: Optional[str] = None
    proxy_type: str = 'socks5'  # 'socks5' or 'mtproxy'
    mtproxy_secret: Optional[str] = None
    is_active: bool = True
    last_used: Optional[datetime] = None
    flood_wait_until: Optional[datetime] = None
    daily_operations: int = 0

@dataclass
class OperationState:
    """Tracks the state of operations for resumption"""
    operation_id: str
    operation_type: str  # scrape, invite, message
    target_group: str
    total_items: int
    completed_items: int
    failed_items: int
    started_at: datetime
    last_checkpoint: datetime
    status: str  # running, paused, completed, failed
    error_count: int = 0
    current_batch: int = 0

class EnhancedTelegramAutomation:
    """
    Enhanced Telegram automation system with anti-detection and continuous operation
    """
    
    def __init__(self, config_file: str = "telegram_config.ini"):
        self.config_file = config_file
        self.accounts: List[TelegramAccount] = []
        self.clients: Dict[str, TelegramClient] = {}
        self.active_operations: Dict[str, OperationState] = {}
        self.user_agent = UserAgent()
        
        # Setup logging
        self.setup_logging()
        
        # Database for state management
        self.db_path = "telegram_automation.db"
        self.setup_database()
        
        # Track busy sessions to avoid reusing same client across concurrent operations
        self.busy_sessions: Dict[str, str] = {}
        
        # Load configuration
        self.load_configuration()
        
        # Rate limiting and anti-detection (will be overridden by config)
        self.operation_delays = {
            'scrape': (0.1, 0.2),    # Minimal delays by default
            'invite': (0.1, 0.2),    # Minimal delays by default  
            'message': (0.1, 0.2),   # Minimal delays by default
        }
        
        # Smart delays enabled/disabled from config
        self.smart_delays_enabled = False
        
        # Daily limits per account (tuneable)
        self.daily_limits = {
            'scrape_requests': 500,  # participant page requests/day
            'invites': 50,           # invites/day
            'messages': 200          # messages/day
        }
        
        # Operation profiles controlling delays and batch sizes
        # Stealth: safest; Normal: balanced; Aggressive: faster, higher risk
        self.profiles = {
            'Stealth': {
                'delays': {
                    'scrape': (20, 45),
                    'invite': (60, 120),
                    'message': (15, 35),
                },
                'scrape_batch': 100
            },
            'Normal': {
                'delays': {
                    'scrape': (15, 30),
                    'invite': (45, 90),
                    'message': (10, 25),
                },
                'scrape_batch': 200
            },
            'Aggressive': {
                'delays': {
                    'scrape': (8, 16),
                    'invite': (20, 40),
                    'message': (6, 14),
                },
                'scrape_batch': 300
            }
        }
        # Active profile
        self.active_profile = 'Normal'
        # Apply defaults from active profile
        self.operation_delays = self.profiles[self.active_profile]['delays'].copy()
        self.scrape_batch_size = self.profiles[self.active_profile]['scrape_batch']
        
        # Error handling configurations
        self.max_retries = 3
        self.backoff_multiplier = 2
        self.max_flood_wait = 3600  # 1 hour max flood wait
        
        # Round-robin index per operation type for client rotation
        self._rr_index = {
            'scrape': 0,
            'invite': 0,
            'message': 0,
        }
        
    def setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('telegram_automation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_database(self):
        """Initialize SQLite database for state management"""
        # Use connection with timeout and WAL mode for better concurrency
        conn = sqlite3.connect(self.db_path, timeout=30, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")  # Enable WAL mode for better concurrency
        conn.execute("PRAGMA busy_timeout=30000")  # 30 second timeout
        cursor = conn.cursor()
        
        # Operations state table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS operation_states (
                operation_id TEXT PRIMARY KEY,
                operation_type TEXT,
                target_group TEXT,
                total_items INTEGER,
                completed_items INTEGER,
                failed_items INTEGER,
                started_at TEXT,
                last_checkpoint TEXT,
                status TEXT,
                error_count INTEGER,
                current_batch INTEGER,
                state_data TEXT
            )
        """)
        
        # Account usage tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS account_usage (
                session_name TEXT,
                date TEXT,
                operation_type TEXT,
                count INTEGER,
                PRIMARY KEY (session_name, date, operation_type)
            )
        """)
        
        # Scraped members storage
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraped_members (
                user_id INTEGER,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                phone TEXT,
                source_group TEXT,
                scraped_at TEXT,
                PRIMARY KEY (user_id, source_group)
            )
        """)
        
        conn.commit()
        conn.close()
        
    def load_configuration(self):
        """Load accounts and settings from configuration file"""
        if not os.path.exists(self.config_file):
            self.create_default_config()
            
        config = configparser.ConfigParser()
        config.read(self.config_file)
        
        # Reset accounts before loading
        self.accounts = []
        
        # Load accounts
        for section in config.sections():
            if section.startswith('account_'):
                account = TelegramAccount(
                    api_id=int(config[section]['api_id']),
                    api_hash=config[section]['api_hash'],
                    phone_number=config[section]['phone_number'],
                    session_name=config[section]['session_name'],
                    proxy_host=config[section].get('proxy_host'),
                    proxy_port=int(config[section]['proxy_port']) if config[section].get('proxy_port') else None,
                    proxy_username=config[section].get('proxy_username'),
                    proxy_password=config[section].get('proxy_password'),
                    proxy_type=config[section].get('proxy_type', 'socks5').lower(),
                    mtproxy_secret=config[section].get('mtproxy_secret')
                )
                self.accounts.append(account)
        
        # Load global settings and delay configuration
        if 'settings' in config:
            settings = config['settings']
            
            # Load smart delays setting
            self.smart_delays_enabled = settings.getboolean('smart_delays', False)
            
            # Load specific delay values from config
            scrape_delay = float(settings.get('scrape_delay', 0.1))
            invite_delay = float(settings.get('invite_delay', 0.1))
            message_delay = float(settings.get('message_delay', 0.1))
            min_delay = float(settings.get('min_delay', 0.1))
            max_delay = float(settings.get('max_delay', 0.2))
            
            # Override default delays with config values
            self.operation_delays = {
                'scrape': (min_delay, scrape_delay),
                'invite': (min_delay, invite_delay),
                'message': (min_delay, message_delay),
            }
            
            # Update max requests per minute
            max_requests = int(settings.get('max_requests_per_minute', 999999))
            self.max_requests_per_minute = max_requests
            
            # Update max concurrent operations
            max_concurrent = int(settings.get('max_concurrent_operations', 10))
            self.max_concurrent_operations = max_concurrent
                
        self.logger.info(f"Loaded {len(self.accounts)} accounts from configuration")
        self.logger.info(f"Smart delays: {self.smart_delays_enabled}, Operation delays: {self.operation_delays}")
        
    def create_default_config(self):
        """Create a default configuration file template"""
        config = configparser.ConfigParser()
        
        config['account_1'] = {
            'api_id': '20059171',
            'api_hash': 'bb756a7e8fca2b55f4679edd0a03e619',
            'phone_number': '+4591680894',
            'session_name': 'session1',
            'proxy_host': '',
            'proxy_port': '',
            'proxy_username': '',
            'proxy_password': ''
        }
        
        config['settings'] = {
            'max_concurrent_operations': '3',
            'enable_proxy_rotation': 'true',
            'enable_user_agent_rotation': 'true',
            'smart_delays': 'true'
        }
        
        with open(self.config_file, 'w') as f:
            config.write(f)
            
        self.logger.info(f"Created default configuration file: {self.config_file}")
        
    def set_profile(self, profile: str):
        """Set active profile (Stealth, Normal, Aggressive) and apply settings"""
        if profile in self.profiles:
            self.active_profile = profile
            self.operation_delays = self.profiles[profile]['delays'].copy()
            self.scrape_batch_size = self.profiles[profile]['scrape_batch']
            self.logger.info(f"Active profile set to {profile}: delays={self.operation_delays}, scrape_batch={self.scrape_batch_size}")
        else:
            self.logger.warning(f"Unknown profile '{profile}', keeping {self.active_profile}")
        
    async def get_available_client(self, operation_type: str, require_proxy: Optional[bool] = None) -> Optional[TelegramClient]:
        """Get an available client for the specified operation type.
        If require_proxy is True, only consider accounts that have a proxy configured.
        Accounts are iterated in a round-robin fashion per operation type to distribute load.
        Skips accounts whose client is currently busy with a different operation.
        """
        current_time = datetime.now()
        if not self.accounts:
            return None
        
        start_idx = self._rr_index.get(operation_type, 0) % len(self.accounts)
        # Build ordered indices starting from start_idx
        indices = list(range(start_idx, len(self.accounts))) + list(range(0, start_idx))
        
        chosen_index = None
        for idx in indices:
            account = self.accounts[idx]
            if not account.is_active:
                continue
            if require_proxy:
                if not (account.proxy_host and account.proxy_port):
                    continue
            # Check if account is in flood wait
            if account.flood_wait_until and current_time < account.flood_wait_until:
                continue
            # If this session is busy with another operation, skip
            busy_op = self.busy_sessions.get(account.session_name)
            if busy_op and busy_op != operation_type:
                continue
            # Check daily limits
            if await self.check_daily_limit(account.session_name, operation_type):
                continue
            # Get or create client
            client = await self.get_client(account)
            if client and await client.is_user_authorized():
                chosen_index = idx
                # Advance RR index for next call
                self._rr_index[operation_type] = (idx + 1) % len(self.accounts)
                return client
        
        # If none found, still advance index to avoid starvation next time
        self._rr_index[operation_type] = (start_idx + 1) % len(self.accounts)
        return None
        
    async def scrape_members_via_selenium(self, group_link: str, max_members: int = 500, profile_dir: Optional[str] = None, headless: bool = True, proxy_url: Optional[str] = None) -> List[Dict]:
        """Run Selenium scraper in a thread executor and store results."""
        loop = asyncio.get_event_loop()
        members = await loop.run_in_executor(None, scrape_group_members_via_web, group_link, max_members, profile_dir, headless, proxy_url)
        # Convert to DB schema and store
        batch = []
        for m in members:
            batch.append({
                'id': m.get('id'),
                'username': m.get('username'),
                'first_name': m.get('first_name'),
                'last_name': m.get('last_name'),
                'phone': None,
                'source_group': group_link,
                'scraped_at': datetime.now().isoformat()
            })
        if batch:
            await self.store_scraped_members(batch)
        return batch
        
    async def get_client(self, account: TelegramAccount) -> TelegramClient:
        """Create a fresh Telegram client for the account (avoid cross-loop reuse).
        For SOCKS5 proxies, use Telethon's tuple format: (socks.SOCKS5, host, port, rdns, username, password).
        For MTProxy, use ConnectionTcpMTProxyRandomizedIntermediate with (host, port, secret).
        Do not trigger interactive login here; only connect and ensure authorization.
        """
        connection = None
        proxy = None
        if account.proxy_host and account.proxy_port:
            if account.proxy_type == 'mtproxy' and account.mtproxy_secret:
                connection = ConnectionTcpMTProxyRandomizedIntermediate
                proxy = (account.proxy_host, int(account.proxy_port), account.mtproxy_secret)
            else:
                # SOCKS5
                proxy = (socks.SOCKS5, str(account.proxy_host).strip(), int(account.proxy_port), True, account.proxy_username or None, account.proxy_password or None)
        client_kwargs = dict(proxy=proxy)
        if connection is not None:
            client_kwargs['connection'] = connection
        client = TelegramClient(
            account.session_name,
            account.api_id,
            account.api_hash,
            **client_kwargs
        )
        
        try:
            await client.connect()
            if not await client.is_user_authorized():
                # Not authorized; return None so caller can pick another account or prompt sign-in explicitly
                await client.disconnect()
                self.logger.warning(f"Client not authorized: {account.session_name}")
                return None
            # Validate with a lightweight RPC call to catch stale sessions
            try:
                await client.get_me()
            except Exception as e:
                self.logger.warning(f"Client session invalid or needs reauth ({account.session_name}): {e}")
                try:
                    await client.disconnect()
                except Exception:
                    pass
                return None
            self.logger.info(f"Successfully connected client: {account.session_name}")
            return client
        except Exception as e:
            self.logger.exception(f"Failed to connect client {account.session_name}: {e!r}")
            try:
                await client.disconnect()
            except Exception:
                pass
            return None
            
    async def check_daily_limit(self, session_name: str, operation_type: str) -> bool:
        """Check if daily limit is exceeded for the account"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT count FROM account_usage 
            WHERE session_name = ? AND date = ? AND operation_type = ?
        """, (session_name, today, operation_type))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return False
            
        limit_key = f"{operation_type}_requests" if operation_type == "scrape" else f"{operation_type}s"
        daily_limit = self.daily_limits.get(limit_key, 1000)
        
        return result[0] >= daily_limit
        
    async def update_account_usage(self, session_name: str, operation_type: str):
        """Update account usage statistics"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO account_usage (session_name, date, operation_type, count)
            VALUES (?, ?, ?, COALESCE((SELECT count FROM account_usage 
                    WHERE session_name = ? AND date = ? AND operation_type = ?), 0) + 1)
        """, (session_name, today, operation_type, session_name, today, operation_type))
        
        conn.commit()
        conn.close()
        
    async def smart_delay(self, operation_type: str, base_delay: Optional[float] = None):
        """Implement smart delays with randomization and adaptive behavior"""
        # If smart delays are disabled in config, use minimal delay
        if not self.smart_delays_enabled:
            min_delay, _ = self.operation_delays.get(operation_type, (0.01, 0.02))
            await asyncio.sleep(min_delay)
            return
            
        if base_delay is None:
            min_delay, max_delay = self.operation_delays.get(operation_type, (0.1, 0.2))
            base_delay = random.uniform(min_delay, max_delay)
            
        # Add randomization to avoid patterns (only if smart delays enabled)
        randomized_delay = base_delay * random.uniform(0.8, 1.5)
        
        # Add small random micro-delays to simulate human behavior (only if smart delays enabled)
        micro_delay = random.uniform(0.01, 0.05)
        
        total_delay = randomized_delay + micro_delay
        
        self.logger.debug(f"Smart delay: {total_delay:.2f}s for {operation_type}")
        await asyncio.sleep(total_delay)
        
    def _reserve_session(self, session_name: str, operation_type: str):
        self.busy_sessions[session_name] = operation_type
    
    def _release_session(self, session_name: str):
        try:
            if session_name in self.busy_sessions:
                del self.busy_sessions[session_name]
        except Exception:
            pass
    
    async def enhanced_scrape_members(self, source_group: str, max_members: int = 500, strategy: str = 'standard') -> List[Dict]:
        """Enhanced member scraping with anti-detection and resumption.
        Supports:
        - public usernames or IDs
        - private invite links (t.me/joinchat/<hash> or t.me/+<hash>) by attempting to join first
        - strategy: 'standard' (default) or 'expanded' (letters iteration + recent activity)
        """
        operation_id = f"scrape_{source_group}_{int(time.time())}"
        
        # Initialize operation state
        operation_state = OperationState(
            operation_id=operation_id,
            operation_type="scrape",
            target_group=source_group,
            total_items=max_members,
            completed_items=0,
            failed_items=0,
            started_at=datetime.now(),
            last_checkpoint=datetime.now(),
            status="running"
        )
        
        self.active_operations[operation_id] = operation_state
        
        try:
            client = await self.get_available_client("scrape")
            if not client:
                raise Exception("No available clients for scraping")
            # Reserve this session during scraping
            reserved_session = client.session.filename.split('/')[-1]
            self._reserve_session(reserved_session, "scrape")
                
            # Handle invite links by attempting to join
            target = source_group.strip()
            invite_hash = None
            if target.startswith("http") and "t.me/" in target:
                if "/joinchat/" in target:
                    invite_hash = target.split("/joinchat/")[-1].split('?')[0]
                elif "/+" in target:
                    invite_hash = target.split("/+")[-1].split('?')[0]
            if invite_hash:
                group_entity = None
                try:
                    info = await client(CheckChatInviteRequest(invite_hash))
                    # If already a participant, we get ChatInviteAlready with .chat
                    if hasattr(info, 'chat') and info.chat:
                        group_entity = info.chat
                except Exception:
                    pass
                if group_entity is None:
                    try:
                        res = await client(ImportChatInviteRequest(invite_hash))
                        # Import returns Updates with chats list
                        if hasattr(res, 'chats') and res.chats:
                            group_entity = res.chats[0]
                        self.logger.info("Joined private group via invite link for scraping")
                    except Exception as e:
                        self.logger.info(f"Proceeding without join (possibly already a member): {e}")
                # Final fallback
                if group_entity is None:
                    try:
                        group_entity = await client.get_entity(target)
                    except Exception as e:
                        self.logger.error(f"Unable to resolve entity from invite link: {e}")
                        raise
            else:
                group_entity = await client.get_entity(target)
            self.logger.info(f"Starting enhanced scraping from: {getattr(group_entity, 'title', str(group_entity))}")
            
            all_participants: List[Dict] = []
            seen_ids = set()
            batch_size = max(50, min(self.scrape_batch_size, 400))
            
            # If entity is a basic Chat (not Channel/megagroup), use GetFullChatRequest once
            # Channels/supergroups will use paginated Channels.GetParticipants
            is_channel_like = hasattr(group_entity, 'megagroup') or hasattr(group_entity, 'broadcast') or group_entity.__class__.__name__ == 'Channel'
            
            if not is_channel_like:
                try:
                    full = await client(GetFullChatRequest(group_entity.id))
                    # Map user_id -> user object for details
                    user_map = {getattr(u, 'id', None): u for u in getattr(full, 'users', [])}
                    part_container = getattr(full.full_chat, 'participants', None)
                    part_list = getattr(part_container, 'participants', []) if part_container else []
                    batch_members = []
                    for p in part_list:
                        uid = getattr(p, 'user_id', None)
                        if uid is None or uid in seen_ids:
                            continue
                        seen_ids.add(uid)
                        u = user_map.get(uid)
                        member_data = {
                            'id': uid,
                            'username': getattr(u, 'username', None) if u else None,
                            'first_name': getattr(u, 'first_name', None) if u else None,
                            'last_name': getattr(u, 'last_name', None) if u else None,
                            'phone': getattr(u, 'phone', None) if u else None,
                            'source_group': source_group,
                            'scraped_at': datetime.now().isoformat()
                        }
                        batch_members.append(member_data)
                    if batch_members:
                        await self.store_scraped_members(batch_members)
                        all_participants.extend(batch_members)
                        # Update usage and checkpoint
                        session_name = client.session.filename.split('/')[-1]
                        await self.update_account_usage(session_name, "scrape")
                        operation_state.completed_items = len(all_participants)
                        operation_state.last_checkpoint = datetime.now()
                        await self.save_operation_state(operation_state)
                    self.logger.info(f"Basic chat scrape collected {len(batch_members)} members")
                except Exception as e:
                    self.logger.exception(f"Basic chat scrape failed: {e!r}")
                # Finalize for basic chats
                operation_state.status = "completed"
                await self.save_operation_state(operation_state)
                self.logger.info(f"Scraping completed: {len(all_participants)} members")
                return all_participants
            
            async def fetch_page(search_query: str, start_offset: int = 0) -> int:
                nonlocal seen_ids, all_participants
                offset = start_offset
                fetched_this_query = 0
                while len(all_participants) < max_members:
                    participants = await client(GetParticipantsRequest(
                        group_entity,
                        ChannelParticipantsSearch(search_query),
                        offset,
                        batch_size,
                        hash=0
                    ))
                    if not participants.users:
                        break
                    batch_members = []
                    for user in participants.users:
                        if user.id in seen_ids:
                            continue
                        seen_ids.add(user.id)
                        member_data = {
                            'id': user.id,
                            'username': user.username,
                            'first_name': getattr(user, 'first_name', None),
                            'last_name': getattr(user, 'last_name', None),
                            'phone': getattr(user, 'phone', None),
                            'source_group': source_group,
                            'scraped_at': datetime.now().isoformat()
                        }
                        batch_members.append(member_data)
                    if batch_members:
                        await self.store_scraped_members(batch_members)
                        all_participants.extend(batch_members)
                        fetched_this_query += len(batch_members)
                        # Update usage
                        session_name = client.session.filename.split('/')[-1]
                        await self.update_account_usage(session_name, "scrape")
                    offset += len(participants.users)
                    # Smart delay with anti-detection
                    await self.smart_delay("scrape")
                    if len(all_participants) >= max_members:
                        break
                return fetched_this_query
            
            # Standard: empty search once; Expanded: iterate query chars and recent activity
            if strategy == 'expanded':
                queries = [''] + list('abcdefghijklmnopqrstuvwxyz0123456789')
            else:
                queries = ['']
            
            for q in queries:
                if len(all_participants) >= max_members:
                    break
                try:
                    await fetch_page(q, 0)
                except FloodWaitError as e:
                    self.logger.warning(f"FloodWait during scraping: {e.seconds}s")
                    if e.seconds > self.max_flood_wait:
                        self.logger.error(f"FloodWait too long: {e.seconds}s, switching client")
                        # Mark current client as unavailable
                        session_name = client.session.filename.split('/')[-1]
                        for account in self.accounts:
                            if account.session_name == session_name:
                                account.flood_wait_until = datetime.now() + timedelta(seconds=e.seconds)
                                break
                        client = await self.get_available_client("scrape")
                        if not client:
                            raise Exception("No available clients after FloodWait")
                    else:
                        # Respect FloodWaitError from Telegram, but use minimal additional delay
                        await asyncio.sleep(e.seconds + (0.1 if self.smart_delays_enabled else 0.01))
                except Exception as e:
                    self.logger.exception(f"Error during scraping batch: {e!r}")
                    operation_state.error_count += 1
                    if operation_state.error_count > self.max_retries:
                        raise
                    await asyncio.sleep(0.1 if self.smart_delays_enabled else 0.01)
            
            # Expanded mode: also harvest recent activity senders
            if strategy == 'expanded' and len(all_participants) < max_members:
                try:
                    async for msg in client.iter_messages(entity=group_entity, limit=2000):
                        if getattr(msg, 'sender_id', None) and msg.sender_id not in seen_ids:
                            seen_ids.add(msg.sender_id)
                            member_data = {
                                'id': msg.sender_id,
                                'username': None,
                                'first_name': None,
                                'last_name': None,
                                'phone': None,
                                'source_group': source_group,
                                'scraped_at': datetime.now().isoformat()
                            }
                            await self.store_scraped_members([member_data])
                            all_participants.append(member_data)
                            if len(all_participants) >= max_members:
                                break
                    self.logger.info(f"Expanded activity-based scrape added senders, total: {len(all_participants)}")
                except Exception as e:
                    self.logger.info(f"Activity-based supplement failed or limited: {e!r}")
            operation_state.status = "completed"
            await self.save_operation_state(operation_state)
            
            self.logger.info(f"Scraping completed: {len(all_participants)} members")
            return all_participants
            
        except Exception as e:
            operation_state.status = "failed"
            await self.save_operation_state(operation_state)
            self.logger.exception(f"Scraping failed: {e!r}")
            raise
            
        finally:
            try:
                self._release_session(reserved_session)
            except Exception:
                pass
    async def store_scraped_members(self, members: List[Dict]):
        """Store scraped members in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for member in members:
            cursor.execute("""
                INSERT OR REPLACE INTO scraped_members 
                (user_id, username, first_name, last_name, phone, source_group, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                member['id'], member['username'], member['first_name'],
                member['last_name'], member['phone'], member['source_group'],
                member['scraped_at']
            ))
            
        conn.commit()
        conn.close()
        
    async def save_operation_state(self, operation_state: OperationState):
        """Save operation state to database for resumption"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO operation_states 
            (operation_id, operation_type, target_group, total_items, completed_items,
             failed_items, started_at, last_checkpoint, status, error_count, current_batch, state_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            operation_state.operation_id, operation_state.operation_type,
            operation_state.target_group, operation_state.total_items,
            operation_state.completed_items, operation_state.failed_items,
            operation_state.started_at.isoformat(), operation_state.last_checkpoint.isoformat(),
            operation_state.status, operation_state.error_count,
            operation_state.current_batch, json.dumps(asdict(operation_state), default=str)
        ))
        
        conn.commit()
        conn.close()
        
    async def enhanced_mass_messaging(self, message_template: str, target_group: str = None) -> bool:
        """Enhanced mass messaging with smart distribution and anti-detection"""
        operation_id = f"message_{int(time.time())}"
        
        # Get recipients from database or target group
        recipients = await self.get_message_recipients(target_group)
        if not recipients:
            self.logger.error("No recipients found for messaging")
            return False
            
        operation_state = OperationState(
            operation_id=operation_id,
            operation_type="message",
            target_group=target_group or "scraped_members",
            total_items=len(recipients),
            completed_items=0,
            failed_items=0,
            started_at=datetime.now(),
            last_checkpoint=datetime.now(),
            status="running"
        )
        
        self.active_operations[operation_id] = operation_state
        
        try:
            successful_sends = 0
            
            for i, recipient in enumerate(recipients):
                try:
                    client = await self.get_available_client("message")
                    if not client:
                        self.logger.warning("No available clients for messaging, waiting...")
                        await asyncio.sleep(1.0 if self.smart_delays_enabled else 0.1)  # Brief wait
                        continue
                        
                    # Personalize message
                    message = message_template.format(
                        name=recipient.get('first_name', ''),
                        last_name=recipient.get('last_name', '')
                    )
                    
                    # Send message
                    await client.send_message(recipient['id'], message)
                    successful_sends += 1
                    operation_state.completed_items = successful_sends
                    
                    self.logger.info(f"Message sent to {recipient['id']} ({i+1}/{len(recipients)})")
                    
                    # Update usage
                    session_name = client.session.filename.split('/')[-1]
                    await self.update_account_usage(session_name, "message")
                    
                    # Smart delay
                    await self.smart_delay("message")
                    
                except FloodWaitError as e:
                    self.logger.warning(f"FloodWait during messaging: {e.seconds}s")
                    await asyncio.sleep(e.seconds + (0.1 if self.smart_delays_enabled else 0.01))
                    
                except Exception as e:
                    self.logger.exception(f"Failed to send message to {recipient['id']}: {e!r}")
                    operation_state.failed_items += 1
                    await asyncio.sleep(0.1 if self.smart_delays_enabled else 0.01)
                    
                # Save checkpoint every 10 messages
                if i % 10 == 0:
                    operation_state.last_checkpoint = datetime.now()
                    await self.save_operation_state(operation_state)
                    
            operation_state.status = "completed"
            await self.save_operation_state(operation_state)
            
            self.logger.info(f"Mass messaging completed: {successful_sends}/{len(recipients)} successful")
            return True
            
        except Exception as e:
            operation_state.status = "failed"
            await self.save_operation_state(operation_state)
            self.logger.exception(f"Mass messaging failed: {e!r}")
            return False
            
    async def get_message_recipients(self, target_group: str = None) -> List[Dict]:
        """Get recipients for messaging from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if target_group:
            cursor.execute("""
                SELECT user_id, username, first_name, last_name 
                FROM scraped_members WHERE source_group = ?
            """, (target_group,))
        else:
            cursor.execute("""
                SELECT user_id, username, first_name, last_name 
                FROM scraped_members
            """)
            
        rows = cursor.fetchall()
        conn.close()
        
        recipients = []
        for row in rows:
            recipients.append({
                'id': row[0],
                'username': row[1],
                'first_name': row[2],
                'last_name': row[3]
            })
            
        return recipients
        
    async def enhanced_bulk_invite(self, target_group: str, source_group: str = None, rotate_accounts: bool = False, require_proxy: bool = False) -> bool:
        """Enhanced bulk invite with smart distribution and error recovery.
        When rotate_accounts is True, a fresh available client is selected for each invite, enabling per-account proxy use.
        If require_proxy is True, only accounts with configured proxies are used for inviting.
        """
        operation_id = f"invite_{target_group}_{int(time.time())}"
        
        # Get members to invite
        members_to_invite = await self.get_invite_candidates(source_group)
        if not members_to_invite:
            self.logger.error("No members found to invite")
            return False
            
        operation_state = OperationState(
            operation_id=operation_id,
            operation_type="invite",
            target_group=target_group,
            total_items=len(members_to_invite),
            completed_items=0,
            failed_items=0,
            started_at=datetime.now(),
            last_checkpoint=datetime.now(),
            status="running"
        )
        
        self.active_operations[operation_id] = operation_state
        
        try:
            # Cache of target entities per client/session when rotating
            target_entity_cache: Dict[str, Any] = {}
            
            # If not rotating, acquire one client and resolve target once
            if not rotate_accounts:
                client = await self.get_available_client("invite", require_proxy=require_proxy)
                if not client:
                    raise Exception("No available clients for inviting")
                # Reserve during whole invite run
                reserved_session = client.session.filename.split('/')[-1]
                self._reserve_session(reserved_session, "invite")
                target_entity = await client.get_entity(target_group)
            else:
                client = None
                target_entity = None
            
            successful_invites = 0
            
            for i, member in enumerate(members_to_invite):
                try:
                    # Select client according to rotation setting
                    if rotate_accounts:
                        client = await self.get_available_client("invite", require_proxy=require_proxy)
                        if not client:
                            self.logger.warning("No available clients for inviting at the moment, waiting...")
                            await asyncio.sleep(1.0 if self.smart_delays_enabled else 0.1)
                            continue
                        # Resolve target entity for this client (cache per session)
                        session_name = client.session.filename.split('/')[-1]
                        if session_name in target_entity_cache:
                            target_entity = target_entity_cache[session_name]
                        else:
                            target_entity_cache[session_name] = await client.get_entity(target_group)
                            target_entity = target_entity_cache[session_name]
                    # Create user entity for invitation
                    user_entity = await client.get_entity(member['id'])
                    
                    # Send invitation
                    await client(InviteToChannelRequest(target_entity, [user_entity]))
                    successful_invites += 1
                    operation_state.completed_items = successful_invites
                    
                    self.logger.info(f"Invited {member['first_name']} to {target_entity.title} ({i+1}/{len(members_to_invite)})")
                    
                    # Update usage
                    session_name = client.session.filename.split('/')[-1]
                    await self.update_account_usage(session_name, "invite")
                    
                    # Smart delay with longer intervals for invites
                    await self.smart_delay("invite")
                    
                except UserPrivacyRestrictedError:
                    self.logger.warning(f"Privacy restricted: {member['id']}")
                    operation_state.failed_items += 1
                    
                except UserNotMutualContactError:
                    self.logger.warning(f"Not mutual contact: {member['id']}")
                    operation_state.failed_items += 1
                    
                except PeerFloodError:
                    self.logger.error("Peer flood error - need to wait longer between operations")
                    await asyncio.sleep(30 if self.smart_delays_enabled else 1.0)  # Minimal wait or short delay
                    
                except FloodWaitError as e:
                    self.logger.warning(f"FloodWait during invite: {e.seconds}s")
                    await asyncio.sleep(e.seconds + (0.1 if self.smart_delays_enabled else 0.01))
                    
                except Exception as e:
                    self.logger.error(f"Failed to invite {member['id']}: {e}")
                    operation_state.failed_items += 1
                    await asyncio.sleep(0.1 if self.smart_delays_enabled else 0.01)
                    
                # Save checkpoint every 5 invites
                if i % 5 == 0:
                    operation_state.last_checkpoint = datetime.now()
                    await self.save_operation_state(operation_state)
                    
            operation_state.status = "completed"
            await self.save_operation_state(operation_state)
            
            self.logger.info(f"Bulk invite completed: {successful_invites}/{len(members_to_invite)} successful")
            return True
            
        except Exception as e:
            operation_state.status = "failed"
            await self.save_operation_state(operation_state)
            self.logger.error(f"Bulk invite failed: {e}")
            return False
            
        finally:
            try:
                if not rotate_accounts and 'reserved_session' in locals():
                    self._release_session(reserved_session)
            except Exception:
                pass
    async def get_invite_candidates(self, source_group: str = None) -> List[Dict]:
        """Get members to invite from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if source_group:
            cursor.execute("""
                SELECT user_id, username, first_name, last_name 
                FROM scraped_members WHERE source_group = ?
                ORDER BY scraped_at DESC
            """, (source_group,))
        else:
            cursor.execute("""
                SELECT user_id, username, first_name, last_name 
                FROM scraped_members
                ORDER BY scraped_at DESC
            """)
            
        rows = cursor.fetchall()
        conn.close()
        
        candidates = []
        for row in rows:
            candidates.append({
                'id': row[0],
                'username': row[1],
                'first_name': row[2],
                'last_name': row[3]
            })
            
        return candidates
        
    async def cleanup_and_close(self):
        """Cleanup resources and close connections"""
        self.logger.info("Cleaning up resources...")
        
        for client in self.clients.values():
            if client.is_connected():
                await client.disconnect()
                
        self.logger.info("All connections closed")

# Usage example and CLI interface
async def main():
    """Main function demonstrating the enhanced framework"""
    automation = EnhancedTelegramAutomation()
    
    try:
        # Example: Scrape members from a group
        print("Starting enhanced Telegram automation...")
        
        # Scrape members
        source_group = input("Enter source group username/ID (or press Enter to skip): ")
        if source_group:
            members = await automation.enhanced_scrape_members(source_group, max_members=100)
            print(f"Scraped {len(members)} members")
        
        # Send mass messages
        send_messages = input("Send mass messages? (y/n): ")
        if send_messages.lower() == 'y':
            message_template = input("Enter message template (use {name} for personalization): ")
            await automation.enhanced_mass_messaging(message_template)
            
        # Bulk invite
        bulk_invite = input("Perform bulk invite? (y/n): ")
        if bulk_invite.lower() == 'y':
            target_group = input("Enter target group username/ID: ")
            await automation.enhanced_bulk_invite(target_group)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await automation.cleanup_and_close()

if __name__ == "__main__":
    asyncio.run(main())