#!/usr/bin/env python3
"""
Premium Features System for SMS Marketplace
Manages subscription tiers, advanced filtering, priority support, and exclusive features
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, asdict
import sqlite3
import threading
import uuid

class SubscriptionTier(Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

@dataclass 
class SubscriptionPlan:
    tier: SubscriptionTier
    name: str
    price_monthly: float
    price_yearly: float
    features: List[str]
    limits: Dict[str, Any]
    exclusive_providers: List[str]
    priority_support: bool
    api_rate_limit: int  # requests per minute
    bulk_discount: float  # percentage
    
class PremiumFeatures:
    def __init__(self, db_path: str = "premium_features.db"):
        self.db_path = db_path
        self.lock = threading.RLock()
        self._init_database()
        self._setup_plans()
        
    def _init_database(self):
        """Initialize SQLite database for premium features"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    user_id TEXT PRIMARY KEY,
                    subscription_tier TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    auto_renewal BOOLEAN DEFAULT TRUE,
                    payment_method TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usage_tracking (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    feature_used TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 1,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS premium_providers (
                    provider_name TEXT PRIMARY KEY,
                    required_tier TEXT NOT NULL,
                    extra_cost REAL DEFAULT 0.0,
                    features TEXT,
                    enabled BOOLEAN DEFAULT TRUE
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS support_tickets (
                    ticket_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    tier TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    description TEXT,
                    priority TEXT DEFAULT 'normal',
                    status TEXT DEFAULT 'open',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def _setup_plans(self):
        """Setup subscription plans"""
        self.plans = {
            SubscriptionTier.FREE: SubscriptionPlan(
                tier=SubscriptionTier.FREE,
                name="Free Tier",
                price_monthly=0.0,
                price_yearly=0.0,
                features=[
                    "Basic SMS number access",
                    "Standard providers only",
                    "Basic filtering",
                    "Community support"
                ],
                limits={
                    "numbers_per_day": 10,
                    "bulk_purchase": 5,
                    "api_calls_per_hour": 100,
                    "countries": ["United States", "United Kingdom"]
                },
                exclusive_providers=[],
                priority_support=False,
                api_rate_limit=100,
                bulk_discount=0.0
            ),
            
            SubscriptionTier.BASIC: SubscriptionPlan(
                tier=SubscriptionTier.BASIC,
                name="Basic Pro",
                price_monthly=29.99,
                price_yearly=299.99,
                features=[
                    "All Free features",
                    "Advanced filtering",
                    "Extended country support",
                    "Email support",
                    "5% bulk discount",
                    "Priority processing"
                ],
                limits={
                    "numbers_per_day": 100,
                    "bulk_purchase": 25,
                    "api_calls_per_hour": 500,
                    "countries": "all"
                },
                exclusive_providers=["SMS-Pool", "PrivateSMS"],
                priority_support=True,
                api_rate_limit=500,
                bulk_discount=5.0
            ),
            
            SubscriptionTier.PRO: SubscriptionPlan(
                tier=SubscriptionTier.PRO,
                name="Professional",
                price_monthly=99.99,
                price_yearly=999.99,
                features=[
                    "All Basic features",
                    "Premium providers access",
                    "Advanced analytics",
                    "Custom automation",
                    "15% bulk discount",
                    "Priority support",
                    "Voice call support",
                    "Virtual numbers"
                ],
                limits={
                    "numbers_per_day": 500,
                    "bulk_purchase": 100,
                    "api_calls_per_hour": 2000,
                    "countries": "all"
                },
                exclusive_providers=["PremiumSMS", "EliteSMS", "ProNumber"],
                priority_support=True,
                api_rate_limit=2000,
                bulk_discount=15.0
            ),
            
            SubscriptionTier.ENTERPRISE: SubscriptionPlan(
                tier=SubscriptionTier.ENTERPRISE,
                name="Enterprise",
                price_monthly=299.99,
                price_yearly=2999.99,
                features=[
                    "All Pro features",
                    "Unlimited access",
                    "Dedicated support",
                    "Custom integrations",
                    "25% bulk discount",
                    "SLA guarantee",
                    "Dedicated account manager",
                    "Custom pricing tiers"
                ],
                limits={
                    "numbers_per_day": -1,  # Unlimited
                    "bulk_purchase": -1,    # Unlimited
                    "api_calls_per_hour": -1, # Unlimited
                    "countries": "all"
                },
                exclusive_providers=["EnterpriseSMS", "CorporateSMS", "GlobalSMS"],
                priority_support=True,
                api_rate_limit=-1,  # Unlimited
                bulk_discount=25.0
            )
        }
        
        # Initialize premium providers
        self._init_premium_providers()
    
    def _init_premium_providers(self):
        """Initialize premium provider configurations"""
        premium_providers = [
            ("SMS-Pool", SubscriptionTier.BASIC.value, 0.02, ["High success rate", "Fast delivery"]),
            ("PrivateSMS", SubscriptionTier.BASIC.value, 0.03, ["Private numbers", "Exclusive access"]),
            ("PremiumSMS", SubscriptionTier.PRO.value, 0.05, ["Ultra-fast delivery", "99.9% uptime"]),
            ("EliteSMS", SubscriptionTier.PRO.value, 0.07, ["Premium countries", "VIP support"]),
            ("ProNumber", SubscriptionTier.PRO.value, 0.04, ["Voice calls", "Virtual numbers"]),
            ("EnterpriseSMS", SubscriptionTier.ENTERPRISE.value, 0.10, ["Dedicated infrastructure"]),
            ("CorporateSMS", SubscriptionTier.ENTERPRISE.value, 0.12, ["SLA guarantee", "24/7 support"]),
            ("GlobalSMS", SubscriptionTier.ENTERPRISE.value, 0.08, ["Worldwide coverage", "Custom solutions"])
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            for provider, tier, cost, features in premium_providers:
                conn.execute("""
                    INSERT OR REPLACE INTO premium_providers 
                    (provider_name, required_tier, extra_cost, features)
                    VALUES (?, ?, ?, ?)
                """, (provider, tier, cost, json.dumps(features)))
            conn.commit()
    
    def subscribe_user(self, user_id: str, tier: SubscriptionTier, payment_method: str = "crypto") -> bool:
        """Subscribe user to a premium tier"""
        with self.lock:
            try:
                start_date = datetime.now().isoformat()
                end_date = (datetime.now() + timedelta(days=30)).isoformat()
                
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO subscriptions 
                        (user_id, subscription_tier, start_date, end_date, payment_method, updated_at)
                        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, (user_id, tier.value, start_date, end_date, payment_method))
                    conn.commit()
                
                return True
            except Exception as e:
                print(f"Subscription error: {e}")
                return False
    
    def get_user_subscription(self, user_id: str) -> Optional[Dict]:
        """Get user's current subscription"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM subscriptions WHERE user_id = ?
            """, (user_id,))
            row = cursor.fetchone()
            
            if row:
                columns = [desc[0] for desc in cursor.description]
                subscription = dict(zip(columns, row))
                
                # Check if subscription is still valid
                end_date = datetime.fromisoformat(subscription['end_date'])
                if datetime.now() > end_date:
                    subscription['expired'] = True
                    return {**subscription, 'effective_tier': SubscriptionTier.FREE}
                
                subscription['expired'] = False
                subscription['effective_tier'] = SubscriptionTier(subscription['subscription_tier'])
                return subscription
            
            return {'effective_tier': SubscriptionTier.FREE, 'expired': False}
    
    def check_feature_access(self, user_id: str, feature: str) -> bool:
        """Check if user has access to a specific feature"""
        subscription = self.get_user_subscription(user_id)
        tier = subscription['effective_tier']
        plan = self.plans[tier]
        
        return feature in plan.features
    
    def check_usage_limit(self, user_id: str, feature: str) -> Dict[str, Any]:
        """Check usage limits for user"""
        subscription = self.get_user_subscription(user_id)
        tier = subscription['effective_tier']
        plan = self.plans[tier]
        
        # Get current usage
        today = datetime.now().date().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT SUM(usage_count) FROM usage_tracking 
                WHERE user_id = ? AND feature_used = ? AND DATE(timestamp) = ?
            """, (user_id, feature, today))
            current_usage = cursor.fetchone()[0] or 0
        
        limit = plan.limits.get(feature, 0)
        
        return {
            'current_usage': current_usage,
            'limit': limit,
            'remaining': max(0, limit - current_usage) if limit > 0 else -1,
            'unlimited': limit == -1,
            'can_use': limit == -1 or current_usage < limit
        }
    
    def track_usage(self, user_id: str, feature: str, count: int = 1, metadata: Dict = None):
        """Track feature usage"""
        usage_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO usage_tracking 
                (id, user_id, feature_used, usage_count, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (usage_id, user_id, feature, count, json.dumps(metadata or {})))
            conn.commit()
    
    def get_available_providers(self, user_id: str) -> List[str]:
        """Get providers available to user based on subscription"""
        subscription = self.get_user_subscription(user_id)
        tier = subscription['effective_tier']
        
        # Base providers (available to all)
        base_providers = ["SMS-Activate", "5SIM", "GetSMSCode"]
        
        # Get tier-specific providers
        available_providers = base_providers.copy()
        
        # Add providers based on tier
        for t in SubscriptionTier:
            if self._tier_level(tier) >= self._tier_level(t):
                available_providers.extend(self.plans[t].exclusive_providers)
        
        # Remove duplicates
        return list(set(available_providers))
    
    def _tier_level(self, tier: SubscriptionTier) -> int:
        """Get numeric level for tier comparison"""
        levels = {
            SubscriptionTier.FREE: 0,
            SubscriptionTier.BASIC: 1,
            SubscriptionTier.PRO: 2,
            SubscriptionTier.ENTERPRISE: 3
        }
        return levels.get(tier, 0)
    
    def get_bulk_discount(self, user_id: str, quantity: int) -> float:
        """Calculate bulk discount for user"""
        subscription = self.get_user_subscription(user_id)
        tier = subscription['effective_tier']
        plan = self.plans[tier]
        
        # Progressive discounts
        base_discount = plan.bulk_discount
        
        if quantity >= 100:
            return base_discount + 5.0
        elif quantity >= 50:
            return base_discount + 2.5
        elif quantity >= 25:
            return base_discount + 1.0
        
        return base_discount
    
    def create_support_ticket(self, user_id: str, subject: str, description: str) -> str:
        """Create support ticket"""
        ticket_id = str(uuid.uuid4())
        subscription = self.get_user_subscription(user_id)
        tier = subscription['effective_tier']
        plan = self.plans[tier]
        
        priority = "high" if plan.priority_support else "normal"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO support_tickets 
                (ticket_id, user_id, tier, subject, description, priority)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (ticket_id, user_id, tier.value, subject, description, priority))
            conn.commit()
        
        return ticket_id
    
    def get_analytics_access(self, user_id: str) -> Dict[str, Any]:
        """Get analytics access level for user"""
        subscription = self.get_user_subscription(user_id)
        tier = subscription['effective_tier']
        
        analytics_levels = {
            SubscriptionTier.FREE: {
                "basic_stats": True,
                "detailed_analytics": False,
                "custom_reports": False,
                "data_export": False,
                "real_time_metrics": False
            },
            SubscriptionTier.BASIC: {
                "basic_stats": True,
                "detailed_analytics": True,
                "custom_reports": False,
                "data_export": True,
                "real_time_metrics": False
            },
            SubscriptionTier.PRO: {
                "basic_stats": True,
                "detailed_analytics": True,
                "custom_reports": True,
                "data_export": True,
                "real_time_metrics": True
            },
            SubscriptionTier.ENTERPRISE: {
                "basic_stats": True,
                "detailed_analytics": True,
                "custom_reports": True,
                "data_export": True,
                "real_time_metrics": True,
                "api_analytics": True,
                "custom_dashboards": True
            }
        }
        
        return analytics_levels.get(tier, analytics_levels[SubscriptionTier.FREE])
    
    def get_plan_info(self, tier: SubscriptionTier) -> Dict:
        """Get detailed plan information"""
        plan = self.plans[tier]
        return asdict(plan)
    
    def upgrade_user(self, user_id: str, new_tier: SubscriptionTier, payment_method: str = "crypto") -> bool:
        """Upgrade user subscription"""
        current_subscription = self.get_user_subscription(user_id)
        current_tier = current_subscription['effective_tier']
        
        if self._tier_level(new_tier) > self._tier_level(current_tier):
            return self.subscribe_user(user_id, new_tier, payment_method)
        
        return False
    
    def get_subscription_stats(self) -> Dict:
        """Get subscription statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT subscription_tier, COUNT(*) as count 
                FROM subscriptions 
                WHERE datetime(end_date) > datetime('now')
                GROUP BY subscription_tier
            """)
            
            stats = {}
            for row in cursor.fetchall():
                stats[row[0]] = row[1]
            
            # Get total revenue (mock calculation)
            total_revenue = 0
            for tier_name, count in stats.items():
                tier = SubscriptionTier(tier_name)
                plan = self.plans[tier]
                total_revenue += plan.price_monthly * count
            
            stats['total_active_subscriptions'] = sum(stats.values())
            stats['estimated_monthly_revenue'] = total_revenue
            
            return stats

# Global premium features instance
premium_features = PremiumFeatures()

def get_premium_features() -> PremiumFeatures:
    """Get global premium features instance"""
    return premium_features