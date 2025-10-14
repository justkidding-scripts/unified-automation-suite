#!/usr/bin/env python3
"""
Mobile Companion App API for SMS Marketplace
Provides REST API endpoints for mobile access and push notification system
"""

from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import jwt
from datetime import datetime, timedelta
import sqlite3
import threading
import hashlib
import uuid
from typing import Dict, List, Optional, Any
import json
import requests
import asyncio
from dataclasses import asdict
from functools import wraps
import logging

# Import our enhanced systems
try:
    from premium_features import get_premium_features, SubscriptionTier
    from performance_manager import get_performance_manager
    from multi_market_providers import get_multi_market_manager
    from revenue_optimizer import get_revenue_optimizer
except ImportError:
    # Handle import errors gracefully
    pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sms-marketplace-mobile-secret-key-change-in-production'
CORS(app)

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["1000 per hour"]
)

# Database setup
DB_PATH = "mobile_app.db"

def init_mobile_db():
    """Initialize mobile app database"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mobile_users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                subscription_tier TEXT DEFAULT 'free',
                device_tokens TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_login TEXT,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mobile_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                device_info TEXT,
                ip_address TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES mobile_users (user_id)
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS push_notifications (
                notification_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                data TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                sent_at TEXT,
                FOREIGN KEY (user_id) REFERENCES mobile_users (user_id)
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mobile_orders (
                order_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                country TEXT,
                service TEXT,
                provider TEXT,
                quantity INTEGER,
                unit_price REAL,
                total_amount REAL,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT,
                FOREIGN KEY (user_id) REFERENCES mobile_users (user_id)
            )
        """)
        
        conn.commit()

# Initialize database
init_mobile_db()

class MobilePushNotificationService:
    """Push notification service for mobile apps"""
    
    def __init__(self):
        self.fcm_server_key = "YOUR_FCM_SERVER_KEY"  # Replace with actual FCM key
        self.apns_key = "YOUR_APNS_KEY"  # Replace with actual APNS key
        
    def send_push_notification(self, user_id: str, title: str, message: str, 
                             data: Dict = None, notification_type: str = "info"):
        """Send push notification to user"""
        
        # Get user's device tokens
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("""
                SELECT device_tokens FROM mobile_users WHERE user_id = ?
            """, (user_id,))
            result = cursor.fetchone()
            
            if not result or not result[0]:
                return False
            
            device_tokens = json.loads(result[0]) if result[0] else []
        
        # Store notification in database
        notification_id = str(uuid.uuid4())
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                INSERT INTO push_notifications 
                (notification_id, user_id, title, message, data, status)
                VALUES (?, ?, ?, ?, ?, 'sent')
            """, (notification_id, user_id, title, message, json.dumps(data or {})))
            conn.commit()
        
        # Send to FCM (Android) and APNS (iOS)
        success_count = 0
        for token in device_tokens:
            if token['platform'] == 'android':
                if self._send_fcm_notification(token['token'], title, message, data):
                    success_count += 1
            elif token['platform'] == 'ios':
                if self._send_apns_notification(token['token'], title, message, data):
                    success_count += 1
        
        return success_count > 0
    
    def _send_fcm_notification(self, token: str, title: str, message: str, data: Dict) -> bool:
        """Send Firebase Cloud Messaging notification"""
        url = "https://fcm.googleapis.com/fcm/send"
        headers = {
            "Authorization": f"key={self.fcm_server_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "to": token,
            "notification": {
                "title": title,
                "body": message,
                "icon": "ic_notification",
                "sound": "default"
            },
            "data": data or {}
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"FCM notification failed: {e}")
            return False
    
    def _send_apns_notification(self, token: str, title: str, message: str, data: Dict) -> bool:
        """Send Apple Push Notification Service notification"""
        # This is a simplified version - production would use proper APNS libraries
        try:
            # Mock APNS implementation
            logger.info(f"APNS notification sent to {token}: {title}")
            return True
        except Exception as e:
            logger.error(f"APNS notification failed: {e}")
            return False
    
    def send_bulk_notifications(self, user_ids: List[str], title: str, message: str, data: Dict = None):
        """Send bulk notifications to multiple users"""
        for user_id in user_ids:
            self.send_push_notification(user_id, title, message, data)

# Global notification service
notification_service = MobilePushNotificationService()

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No authorization token provided'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            g.current_user_id = payload['user_id']
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

@app.route('/api/v1/auth/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """Register new mobile user"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Hash password
    password_hash = hashlib.sha256(data['password'].encode()).hexdigest()
    user_id = str(uuid.uuid4())
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                INSERT INTO mobile_users (user_id, username, email, password_hash)
                VALUES (?, ?, ?, ?)
            """, (user_id, data['username'], data['email'], password_hash))
            conn.commit()
        
        # Create JWT token
        token = jwt.encode({
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=30)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        # Send welcome notification
        notification_service.send_push_notification(
            user_id,
            "Welcome to SMS Marketplace!",
            "Your account has been created successfully. Start purchasing SMS numbers now!"
        )
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'token': token,
            'subscription_tier': 'free'
        })
        
    except sqlite3.IntegrityError as e:
        if 'username' in str(e):
            return jsonify({'error': 'Username already exists'}), 409
        elif 'email' in str(e):
            return jsonify({'error': 'Email already exists'}), 409
        else:
            return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/v1/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Login mobile user"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('username', 'password')):
        return jsonify({'error': 'Missing username or password'}), 400
    
    password_hash = hashlib.sha256(data['password'].encode()).hexdigest()
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            SELECT user_id, subscription_tier FROM mobile_users
            WHERE username = ? AND password_hash = ? AND is_active = TRUE
        """, (data['username'], password_hash))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        user_id, subscription_tier = result
        
        # Update last login
        conn.execute("""
            UPDATE mobile_users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?
        """, (user_id,))
        conn.commit()
    
    # Create JWT token
    token = jwt.encode({
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=30)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    # Update device token if provided
    device_token = data.get('device_token')
    platform = data.get('platform', 'unknown')
    
    if device_token:
        update_device_token(user_id, device_token, platform)
    
    return jsonify({
        'success': True,
        'user_id': user_id,
        'token': token,
        'subscription_tier': subscription_tier
    })

def update_device_token(user_id: str, device_token: str, platform: str):
    """Update user's device token for push notifications"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            SELECT device_tokens FROM mobile_users WHERE user_id = ?
        """, (user_id,))
        result = cursor.fetchone()
        
        device_tokens = json.loads(result[0]) if result and result[0] else []
        
        # Remove existing token for same platform
        device_tokens = [t for t in device_tokens if t['platform'] != platform]
        
        # Add new token
        device_tokens.append({
            'token': device_token,
            'platform': platform,
            'updated_at': datetime.now().isoformat()
        })
        
        conn.execute("""
            UPDATE mobile_users SET device_tokens = ? WHERE user_id = ?
        """, (json.dumps(device_tokens), user_id))
        conn.commit()

@app.route('/api/v1/numbers/available', methods=['GET'])
@require_auth
@limiter.limit("100 per hour")
def get_available_numbers():
    """Get available SMS numbers"""
    country = request.args.get('country', 'United States')
    service = request.args.get('service', 'Telegram')
    provider = request.args.get('provider')
    
    try:
        # Check user's subscription limits
        premium_features = get_premium_features()
        subscription = premium_features.get_user_subscription(g.current_user_id)
        available_providers = premium_features.get_available_providers(g.current_user_id)
        
        # Get numbers from multi-market manager
        multi_market = get_multi_market_manager()
        
        if provider and provider in available_providers:
            provider_obj = multi_market.get_provider(provider)
            numbers = provider_obj.get_voice_numbers(country, service) if provider_obj else []
        else:
            numbers = multi_market.get_voice_numbers_multi_market(country, service)
            # Filter by available providers
            numbers = [n for n in numbers if n.get('provider') in available_providers]
        
        # Apply revenue optimization
        revenue_optimizer = get_revenue_optimizer()
        for number in numbers:
            pricing = revenue_optimizer.optimize_pricing(
                country, service, number.get('provider', 'Unknown'), 
                number.get('cost', 0.08), 'standard'
            )
            number['optimized_price'] = pricing['optimized_price']
            number['original_price'] = number.get('cost', 0.08)
        
        return jsonify({
            'success': True,
            'numbers': numbers,
            'subscription_tier': subscription['effective_tier'].value,
            'available_providers': available_providers
        })
        
    except Exception as e:
        logger.error(f"Error getting available numbers: {e}")
        return jsonify({'error': 'Failed to fetch numbers'}), 500

@app.route('/api/v1/numbers/purchase', methods=['POST'])
@require_auth
@limiter.limit("50 per hour")
def purchase_number():
    """Purchase SMS numbers"""
    data = request.get_json()
    
    required_fields = ['numbers', 'country', 'service', 'provider']
    if not data or not all(k in data for k in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        premium_features = get_premium_features()
        
        # Check usage limits
        quantity = len(data['numbers'])
        usage_check = premium_features.check_usage_limit(g.current_user_id, 'numbers_per_day')
        
        if not usage_check['can_use'] or usage_check['remaining'] < quantity:
            return jsonify({
                'error': 'Usage limit exceeded',
                'limit': usage_check['limit'],
                'current_usage': usage_check['current_usage']
            }), 429
        
        # Calculate pricing with bulk discounts
        unit_price = data.get('unit_price', 0.08)
        discount = premium_features.get_bulk_discount(g.current_user_id, quantity)
        
        discounted_price = unit_price * (1 - discount / 100)
        total_amount = discounted_price * quantity
        
        # Create order
        order_id = str(uuid.uuid4())
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                INSERT INTO mobile_orders 
                (order_id, user_id, country, service, provider, quantity, unit_price, total_amount, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'completed')
            """, (order_id, g.current_user_id, data['country'], data['service'], 
                  data['provider'], quantity, discounted_price, total_amount))
            conn.commit()
        
        # Track usage
        premium_features.track_usage(g.current_user_id, 'numbers_per_day', quantity)
        
        # Track revenue
        revenue_optimizer = get_revenue_optimizer()
        revenue_optimizer.track_transaction(
            g.current_user_id, data['country'], data['service'], 
            data['provider'], quantity, discounted_price, 'mobile_app'
        )
        
        # Send success notification
        notification_service.send_push_notification(
            g.current_user_id,
            "Purchase Successful!",
            f"You've successfully purchased {quantity} SMS numbers for {data['service']}",
            {'order_id': order_id, 'type': 'purchase_success'}
        )
        
        return jsonify({
            'success': True,
            'order_id': order_id,
            'quantity': quantity,
            'unit_price': discounted_price,
            'discount_applied': discount,
            'total_amount': total_amount,
            'numbers': data['numbers']
        })
        
    except Exception as e:
        logger.error(f"Error purchasing numbers: {e}")
        return jsonify({'error': 'Purchase failed'}), 500

@app.route('/api/v1/orders/history', methods=['GET'])
@require_auth
@limiter.limit("200 per hour")
def get_order_history():
    """Get user's order history"""
    limit = min(int(request.args.get('limit', 50)), 100)
    offset = int(request.args.get('offset', 0))
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            SELECT order_id, country, service, provider, quantity, unit_price, 
                   total_amount, status, created_at, completed_at
            FROM mobile_orders 
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (g.current_user_id, limit, offset))
        
        orders = []
        for row in cursor.fetchall():
            orders.append({
                'order_id': row[0],
                'country': row[1],
                'service': row[2],
                'provider': row[3],
                'quantity': row[4],
                'unit_price': row[5],
                'total_amount': row[6],
                'status': row[7],
                'created_at': row[8],
                'completed_at': row[9]
            })
    
    return jsonify({
        'success': True,
        'orders': orders,
        'pagination': {
            'limit': limit,
            'offset': offset,
            'has_more': len(orders) == limit
        }
    })

@app.route('/api/v1/subscription/info', methods=['GET'])
@require_auth
def get_subscription_info():
    """Get user's subscription information"""
    try:
        premium_features = get_premium_features()
        subscription = premium_features.get_user_subscription(g.current_user_id)
        
        # Get usage statistics
        usage_stats = {}
        for feature in ['numbers_per_day', 'bulk_purchase', 'api_calls_per_hour']:
            usage_stats[feature] = premium_features.check_usage_limit(g.current_user_id, feature)
        
        # Get available plans
        plans = {}
        for tier in SubscriptionTier:
            plans[tier.value] = premium_features.get_plan_info(tier)
        
        return jsonify({
            'success': True,
            'current_subscription': {
                'tier': subscription['effective_tier'].value,
                'expired': subscription.get('expired', False),
                'end_date': subscription.get('end_date'),
                'auto_renewal': subscription.get('auto_renewal', False)
            },
            'usage_stats': usage_stats,
            'available_plans': plans,
            'available_providers': premium_features.get_available_providers(g.current_user_id)
        })
        
    except Exception as e:
        logger.error(f"Error getting subscription info: {e}")
        return jsonify({'error': 'Failed to get subscription info'}), 500

@app.route('/api/v1/analytics/dashboard', methods=['GET'])
@require_auth
def get_mobile_dashboard():
    """Get mobile dashboard analytics"""
    days = min(int(request.args.get('days', 30)), 90)
    
    try:
        # Get user's order statistics
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_orders,
                    SUM(total_amount) as total_spent,
                    SUM(quantity) as total_numbers,
                    AVG(total_amount) as avg_order_value
                FROM mobile_orders 
                WHERE user_id = ? AND datetime(created_at) > datetime('now', '-{} days')
            """.format(days), (g.current_user_id,))
            
            stats = cursor.fetchone()
        
        # Get revenue analytics (if available)
        analytics = {
            'period_days': days,
            'total_orders': stats[0] or 0,
            'total_spent': round(stats[1] or 0, 2),
            'total_numbers_purchased': stats[2] or 0,
            'average_order_value': round(stats[3] or 0, 2)
        }
        
        # Get performance metrics
        try:
            performance_manager = get_performance_manager()
            performance_metrics = performance_manager.get_metrics()
            analytics['performance'] = performance_metrics
        except:
            analytics['performance'] = {}
        
        return jsonify({
            'success': True,
            'analytics': analytics,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard: {e}")
        return jsonify({'error': 'Failed to get dashboard data'}), 500

@app.route('/api/v1/notifications/history', methods=['GET'])
@require_auth
def get_notification_history():
    """Get user's notification history"""
    limit = min(int(request.args.get('limit', 20)), 50)
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            SELECT notification_id, title, message, data, status, created_at, sent_at
            FROM push_notifications 
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (g.current_user_id, limit))
        
        notifications = []
        for row in cursor.fetchall():
            notifications.append({
                'notification_id': row[0],
                'title': row[1],
                'message': row[2],
                'data': json.loads(row[3]) if row[3] else {},
                'status': row[4],
                'created_at': row[5],
                'sent_at': row[6]
            })
    
    return jsonify({
        'success': True,
        'notifications': notifications
    })

@app.route('/api/v1/test/notification', methods=['POST'])
@require_auth
def send_test_notification():
    """Send test push notification"""
    data = request.get_json()
    
    title = data.get('title', 'Test Notification')
    message = data.get('message', 'This is a test notification from SMS Marketplace')
    
    success = notification_service.send_push_notification(
        g.current_user_id, title, message, {'type': 'test'}
    )
    
    return jsonify({
        'success': success,
        'message': 'Notification sent successfully' if success else 'Failed to send notification'
    })

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'services': {
            'database': True,
            'notifications': True,
            'authentication': True
        }
    })

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Rate limit exceeded', 'retry_after': str(e.retry_after)}), 429

@app.errorhandler(404)
def not_found_handler(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error_handler(e):
    logger.error(f"Internal error: {e}")
    return jsonify({'error': 'Internal server error'}), 500

def start_mobile_api_server(host='127.0.0.1', port=5000, debug=False):
    """Start the mobile API server"""
    logger.info(f"Starting Mobile API server on {host}:{port}")
    app.run(host=host, port=port, debug=debug, threaded=True)

if __name__ == '__main__':
    start_mobile_api_server(debug=True)