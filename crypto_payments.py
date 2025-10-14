#!/usr/bin/env python3
"""
Cryptocurrency Payment Processing
=================================
Bitcoin, Ethereum, and USDT payment integration for SMS marketplace
"""

import requests
import json
import time
import logging
import sqlite3
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
import hmac
from decimal import Decimal

logger = logging.getLogger(__name__)

class PaymentStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class CryptoType(Enum):
    BITCOIN = "BTC"
    ETHEREUM = "ETH"
    USDT = "USDT"
    LITECOIN = "LTC"
    MONERO = "XMR"

@dataclass
class PaymentRequest:
    payment_id: str
    crypto_type: CryptoType
    amount_crypto: float
    amount_usd: float
    wallet_address: str
    qr_code_data: str
    status: PaymentStatus
    created_at: str
    expires_at: str
    confirmed_at: Optional[str] = None
    transaction_hash: Optional[str] = None

@dataclass
class WalletBalance:
    crypto_type: CryptoType
    balance: float
    usd_value: float
    pending: float = 0.0

class CryptoRateProvider:
    """Get real-time cryptocurrency rates"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 60  # 1 minute cache
        
    def get_crypto_rate(self, crypto: CryptoType) -> float:
        """Get current USD rate for cryptocurrency"""
        try:
            cache_key = f"{crypto.value}_rate"
            current_time = time.time()
            
            # Check cache first
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                if current_time - cached_data['timestamp'] < self.cache_duration:
                    return cached_data['rate']
            
            # Fetch from CoinGecko API
            crypto_ids = {
                CryptoType.BITCOIN: 'bitcoin',
                CryptoType.ETHEREUM: 'ethereum',
                CryptoType.USDT: 'tether',
                CryptoType.LITECOIN: 'litecoin',
                CryptoType.MONERO: 'monero'
            }
            
            crypto_id = crypto_ids.get(crypto, 'bitcoin')
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd"
            
            response = requests.get(url, timeout=10)
            data = response.json()
            
            rate = float(data[crypto_id]['usd'])
            
            # Cache the result
            self.cache[cache_key] = {
                'rate': rate,
                'timestamp': current_time
            }
            
            return rate
            
        except Exception as e:
            logger.error(f"Error fetching crypto rate for {crypto.value}: {e}")
            # Fallback rates
            fallback_rates = {
                CryptoType.BITCOIN: 35000.0,
                CryptoType.ETHEREUM: 2000.0,
                CryptoType.USDT: 1.0,
                CryptoType.LITECOIN: 70.0,
                CryptoType.MONERO: 150.0
            }
            return fallback_rates.get(crypto, 1.0)

class BlockchainMonitor:
    """Monitor blockchain transactions"""
    
    def __init__(self):
        self.session = requests.Session()
        
    def check_bitcoin_payment(self, address: str, amount: float) -> Optional[str]:
        """Check if Bitcoin payment has been received"""
        try:
            # Using BlockCypher API
            url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/balance"
            response = self.session.get(url, timeout=15)
            data = response.json()
            
            balance = float(data.get('balance', 0)) / 100000000  # Convert from satoshi
            
            if balance >= amount * 0.95:  # 95% tolerance for fees
                # Get transaction hash
                txs_url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/txs?limit=1"
                txs_response = self.session.get(txs_url, timeout=15)
                txs_data = txs_response.json()
                
                if txs_data and len(txs_data) > 0:
                    return txs_data[0]['hash']
                    
            return None
            
        except Exception as e:
            logger.error(f"Bitcoin payment check error: {e}")
            return None
            
    def check_ethereum_payment(self, address: str, amount: float) -> Optional[str]:
        """Check if Ethereum payment has been received"""
        try:
            # Using Etherscan API (requires API key in production)
            url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest"
            response = self.session.get(url, timeout=15)
            data = response.json()
            
            if data['status'] == '1':
                balance = float(data['result']) / 1e18  # Convert from Wei
                
                if balance >= amount * 0.95:  # 95% tolerance
                    # Get latest transaction
                    txs_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=desc&page=1&offset=1"
                    txs_response = self.session.get(txs_url, timeout=15)
                    txs_data = txs_response.json()
                    
                    if txs_data['status'] == '1' and len(txs_data['result']) > 0:
                        return txs_data['result'][0]['hash']
                        
            return None
            
        except Exception as e:
            logger.error(f"Ethereum payment check error: {e}")
            return None

class WalletGenerator:
    """Generate cryptocurrency wallet addresses"""
    
    def generate_bitcoin_address(self, payment_id: str) -> str:
        """Generate Bitcoin address (demo - use proper key generation in production)"""
        # This is a demo implementation
        # In production, use proper HD wallet derivation
        hash_input = f"btc_{payment_id}_{int(time.time())}"
        address_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:34]
        return f"1{address_hash[:33]}"  # Bitcoin address format
        
    def generate_ethereum_address(self, payment_id: str) -> str:
        """Generate Ethereum address (demo)"""
        hash_input = f"eth_{payment_id}_{int(time.time())}"
        address_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:40]
        return f"0x{address_hash}"
        
    def generate_qr_code_data(self, crypto_type: CryptoType, address: str, amount: float) -> str:
        """Generate QR code data for payment"""
        if crypto_type == CryptoType.BITCOIN:
            return f"bitcoin:{address}?amount={amount}"
        elif crypto_type == CryptoType.ETHEREUM:
            return f"ethereum:{address}?value={int(amount * 1e18)}"
        else:
            return address

class PaymentProcessor:
    """Main cryptocurrency payment processor"""
    
    def __init__(self):
        self.rate_provider = CryptoRateProvider()
        self.blockchain_monitor = BlockchainMonitor()
        self.wallet_generator = WalletGenerator()
        self.db_path = 'crypto_payments.db'
        self._init_database()
        
    def _init_database(self):
        """Initialize payment database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    payment_id TEXT PRIMARY KEY,
                    crypto_type TEXT NOT NULL,
                    amount_crypto REAL NOT NULL,
                    amount_usd REAL NOT NULL,
                    wallet_address TEXT NOT NULL,
                    qr_code_data TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    confirmed_at TEXT,
                    transaction_hash TEXT,
                    user_data TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS balances (
                    crypto_type TEXT PRIMARY KEY,
                    balance REAL NOT NULL DEFAULT 0,
                    pending REAL NOT NULL DEFAULT 0,
                    last_updated TEXT NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            
    def create_payment_request(self, amount_usd: float, crypto_type: CryptoType, 
                              user_data: Dict = None) -> PaymentRequest:
        """Create a new cryptocurrency payment request"""
        try:
            # Generate payment ID
            payment_id = hashlib.sha256(f"{time.time()}_{amount_usd}_{crypto_type.value}".encode()).hexdigest()[:16]
            
            # Get current crypto rate
            crypto_rate = self.rate_provider.get_crypto_rate(crypto_type)
            amount_crypto = amount_usd / crypto_rate
            
            # Generate wallet address
            if crypto_type == CryptoType.BITCOIN:
                wallet_address = self.wallet_generator.generate_bitcoin_address(payment_id)
            elif crypto_type in [CryptoType.ETHEREUM, CryptoType.USDT]:
                wallet_address = self.wallet_generator.generate_ethereum_address(payment_id)
            else:
                wallet_address = self.wallet_generator.generate_bitcoin_address(payment_id)  # Fallback
                
            # Generate QR code data
            qr_code_data = self.wallet_generator.generate_qr_code_data(crypto_type, wallet_address, amount_crypto)
            
            # Set expiration (2 hours from now)
            created_at = time.strftime("%Y-%m-%d %H:%M:%S")
            expires_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() + 7200))
            
            # Create payment request object
            payment_request = PaymentRequest(
                payment_id=payment_id,
                crypto_type=crypto_type,
                amount_crypto=amount_crypto,
                amount_usd=amount_usd,
                wallet_address=wallet_address,
                qr_code_data=qr_code_data,
                status=PaymentStatus.PENDING,
                created_at=created_at,
                expires_at=expires_at
            )
            
            # Save to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO payments 
                (payment_id, crypto_type, amount_crypto, amount_usd, wallet_address, 
                 qr_code_data, status, created_at, expires_at, user_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                payment_id, crypto_type.value, amount_crypto, amount_usd,
                wallet_address, qr_code_data, PaymentStatus.PENDING.value,
                created_at, expires_at, json.dumps(user_data) if user_data else None
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Created payment request {payment_id} for ${amount_usd} in {crypto_type.value}")
            return payment_request
            
        except Exception as e:
            logger.error(f"Error creating payment request: {e}")
            raise
            
    def check_payment_status(self, payment_id: str) -> Optional[PaymentRequest]:
        """Check the status of a payment request"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT payment_id, crypto_type, amount_crypto, amount_usd, wallet_address,
                       qr_code_data, status, created_at, expires_at, confirmed_at, transaction_hash
                FROM payments WHERE payment_id = ?
            ''', (payment_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
                
            payment_request = PaymentRequest(
                payment_id=row[0],
                crypto_type=CryptoType(row[1]),
                amount_crypto=row[2],
                amount_usd=row[3],
                wallet_address=row[4],
                qr_code_data=row[5],
                status=PaymentStatus(row[6]),
                created_at=row[7],
                expires_at=row[8],
                confirmed_at=row[9],
                transaction_hash=row[10]
            )
            
            # If payment is still pending, check blockchain
            if payment_request.status == PaymentStatus.PENDING:
                tx_hash = None
                
                if payment_request.crypto_type == CryptoType.BITCOIN:
                    tx_hash = self.blockchain_monitor.check_bitcoin_payment(
                        payment_request.wallet_address, payment_request.amount_crypto
                    )
                elif payment_request.crypto_type in [CryptoType.ETHEREUM, CryptoType.USDT]:
                    tx_hash = self.blockchain_monitor.check_ethereum_payment(
                        payment_request.wallet_address, payment_request.amount_crypto
                    )
                
                # Update status if payment found
                if tx_hash:
                    self._update_payment_status(payment_id, PaymentStatus.CONFIRMED, tx_hash)
                    payment_request.status = PaymentStatus.CONFIRMED
                    payment_request.transaction_hash = tx_hash
                    payment_request.confirmed_at = time.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Update balance
                    self._update_balance(payment_request.crypto_type, payment_request.amount_crypto)
                    
            return payment_request
            
        except Exception as e:
            logger.error(f"Error checking payment status: {e}")
            return None
            
    def _update_payment_status(self, payment_id: str, status: PaymentStatus, 
                              transaction_hash: str = None):
        """Update payment status in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if status == PaymentStatus.CONFIRMED:
                cursor.execute('''
                    UPDATE payments 
                    SET status = ?, confirmed_at = ?, transaction_hash = ?
                    WHERE payment_id = ?
                ''', (status.value, time.strftime("%Y-%m-%d %H:%M:%S"), transaction_hash, payment_id))
            else:
                cursor.execute('''
                    UPDATE payments 
                    SET status = ?
                    WHERE payment_id = ?
                ''', (status.value, payment_id))
                
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating payment status: {e}")
            
    def _update_balance(self, crypto_type: CryptoType, amount: float):
        """Update cryptocurrency balance"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO balances 
                (crypto_type, balance, pending, last_updated)
                VALUES (?, COALESCE((SELECT balance FROM balances WHERE crypto_type = ?), 0) + ?, 0, ?)
            ''', (crypto_type.value, crypto_type.value, amount, time.strftime("%Y-%m-%d %H:%M:%S")))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating balance: {e}")
            
    def get_balances(self) -> List[WalletBalance]:
        """Get all cryptocurrency balances"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT crypto_type, balance, pending FROM balances')
            rows = cursor.fetchall()
            conn.close()
            
            balances = []
            for row in rows:
                crypto_type = CryptoType(row[0])
                balance = row[1]
                pending = row[2]
                
                # Get USD value
                rate = self.rate_provider.get_crypto_rate(crypto_type)
                usd_value = balance * rate
                
                balances.append(WalletBalance(
                    crypto_type=crypto_type,
                    balance=balance,
                    usd_value=usd_value,
                    pending=pending
                ))
                
            return balances
            
        except Exception as e:
            logger.error(f"Error getting balances: {e}")
            return []
            
    def get_payment_history(self, limit: int = 50) -> List[PaymentRequest]:
        """Get payment history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT payment_id, crypto_type, amount_crypto, amount_usd, wallet_address,
                       qr_code_data, status, created_at, expires_at, confirmed_at, transaction_hash
                FROM payments 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            payments = []
            for row in rows:
                payment = PaymentRequest(
                    payment_id=row[0],
                    crypto_type=CryptoType(row[1]),
                    amount_crypto=row[2],
                    amount_usd=row[3],
                    wallet_address=row[4],
                    qr_code_data=row[5],
                    status=PaymentStatus(row[6]),
                    created_at=row[7],
                    expires_at=row[8],
                    confirmed_at=row[9],
                    transaction_hash=row[10]
                )
                payments.append(payment)
                
            return payments
            
        except Exception as e:
            logger.error(f"Error getting payment history: {e}")
            return []

# Global payment processor instance
payment_processor = PaymentProcessor()