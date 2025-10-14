#!/usr/bin/env python3
"""
Revenue Optimization Engine for SMS Marketplace
Implements dynamic pricing algorithms, demand-based adjustments, and profit maximization
"""

import json
import time
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import sqlite3
import threading
import uuid
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PricingModel:
    base_price: float
    demand_multiplier: float
    quality_premium: float
    time_of_day_factor: float
    regional_adjustment: float
    competition_factor: float
    profit_margin: float
    minimum_price: float
    maximum_price: float

@dataclass
class MarketData:
    timestamp: datetime
    country: str
    service: str
    provider: str
    demand_level: float  # 0.0 to 1.0
    supply_level: float  # 0.0 to 1.0
    average_price: float
    success_rate: float
    competitor_prices: List[float]

@dataclass
class RevenueMetrics:
    period: str
    total_revenue: float
    total_transactions: int
    average_transaction_value: float
    profit_margin: float
    customer_acquisition_cost: float
    lifetime_value: float
    conversion_rate: float

class DemandPredictor:
    """AI-powered demand prediction system"""
    
    def __init__(self):
        self.historical_data = []
        self.demand_patterns = {}
        self.seasonal_factors = {}
        
    def record_demand(self, country: str, service: str, demand_level: float, timestamp: datetime = None):
        """Record demand data point"""
        if timestamp is None:
            timestamp = datetime.now()
            
        self.historical_data.append({
            'country': country,
            'service': service,
            'demand': demand_level,
            'timestamp': timestamp,
            'hour': timestamp.hour,
            'day_of_week': timestamp.weekday(),
            'day_of_month': timestamp.day
        })
        
        # Keep only last 10000 records for performance
        if len(self.historical_data) > 10000:
            self.historical_data = self.historical_data[-5000:]
    
    def predict_demand(self, country: str, service: str, hours_ahead: int = 1) -> float:
        """Predict future demand using historical patterns"""
        future_time = datetime.now() + timedelta(hours=hours_ahead)
        
        # Filter relevant historical data
        relevant_data = [
            d for d in self.historical_data
            if d['country'] == country and d['service'] == service
        ]
        
        if not relevant_data:
            return 0.5  # Default moderate demand
        
        # Calculate time-based factors
        hour_factor = self._get_hourly_pattern(relevant_data, future_time.hour)
        day_factor = self._get_daily_pattern(relevant_data, future_time.weekday())
        
        # Calculate base demand from recent data
        recent_data = [d for d in relevant_data if d['timestamp'] > datetime.now() - timedelta(days=7)]
        base_demand = np.mean([d['demand'] for d in recent_data]) if recent_data else 0.5
        
        # Combine factors
        predicted_demand = base_demand * hour_factor * day_factor
        
        return max(0.0, min(1.0, predicted_demand))
    
    def _get_hourly_pattern(self, data: List[Dict], hour: int) -> float:
        """Get hourly demand pattern multiplier"""
        hour_data = [d['demand'] for d in data if d['hour'] == hour]
        all_data = [d['demand'] for d in data]
        
        if not hour_data or not all_data:
            return 1.0
            
        hour_avg = np.mean(hour_data)
        overall_avg = np.mean(all_data)
        
        return hour_avg / overall_avg if overall_avg > 0 else 1.0
    
    def _get_daily_pattern(self, data: List[Dict], day_of_week: int) -> float:
        """Get daily demand pattern multiplier"""
        day_data = [d['demand'] for d in data if d['day_of_week'] == day_of_week]
        all_data = [d['demand'] for d in data]
        
        if not day_data or not all_data:
            return 1.0
            
        day_avg = np.mean(day_data)
        overall_avg = np.mean(all_data)
        
        return day_avg / overall_avg if overall_avg > 0 else 1.0

class CompetitorAnalyzer:
    """Analyze competitor pricing and strategies"""
    
    def __init__(self):
        self.competitor_data = {}
        
    def update_competitor_prices(self, country: str, service: str, provider_prices: Dict[str, float]):
        """Update competitor price data"""
        key = f"{country}:{service}"
        
        if key not in self.competitor_data:
            self.competitor_data[key] = []
            
        self.competitor_data[key].append({
            'timestamp': datetime.now(),
            'prices': provider_prices.copy()
        })
        
        # Keep only recent data (last 48 hours)
        cutoff_time = datetime.now() - timedelta(hours=48)
        self.competitor_data[key] = [
            d for d in self.competitor_data[key]
            if d['timestamp'] > cutoff_time
        ]
    
    def get_market_position(self, country: str, service: str, our_price: float) -> Dict[str, Any]:
        """Analyze our market position relative to competitors"""
        key = f"{country}:{service}"
        
        if key not in self.competitor_data or not self.competitor_data[key]:
            return {
                'position': 'unknown',
                'price_percentile': 0.5,
                'competitive_advantage': 0.0,
                'recommended_action': 'maintain'
            }
        
        # Get recent competitor prices
        recent_data = self.competitor_data[key][-10:]  # Last 10 updates
        all_competitor_prices = []
        
        for data_point in recent_data:
            all_competitor_prices.extend(data_point['prices'].values())
        
        if not all_competitor_prices:
            return {'position': 'unknown', 'price_percentile': 0.5, 'competitive_advantage': 0.0}
        
        # Calculate position metrics
        sorted_prices = sorted(all_competitor_prices)
        our_percentile = len([p for p in sorted_prices if p < our_price]) / len(sorted_prices)
        
        min_competitor = min(all_competitor_prices)
        max_competitor = max(all_competitor_prices)
        avg_competitor = np.mean(all_competitor_prices)
        
        # Determine competitive position
        if our_price <= min_competitor:
            position = 'price_leader'
        elif our_price <= avg_competitor:
            position = 'competitive'
        elif our_price <= max_competitor:
            position = 'premium'
        else:
            position = 'overpriced'
        
        # Calculate competitive advantage
        advantage = (avg_competitor - our_price) / avg_competitor if avg_competitor > 0 else 0
        
        # Recommend action
        if position == 'overpriced':
            action = 'decrease_price'
        elif position == 'price_leader' and advantage > 0.2:
            action = 'increase_price'
        else:
            action = 'maintain'
        
        return {
            'position': position,
            'price_percentile': our_percentile,
            'competitive_advantage': advantage,
            'min_competitor': min_competitor,
            'max_competitor': max_competitor,
            'avg_competitor': avg_competitor,
            'recommended_action': action
        }

class DynamicPricingEngine:
    """Core dynamic pricing engine"""
    
    def __init__(self):
        self.base_models = {}
        self.demand_predictor = DemandPredictor()
        self.competitor_analyzer = CompetitorAnalyzer()
        self.lock = threading.RLock()
        
        # Initialize base pricing models
        self._setup_base_models()
    
    def _setup_base_models(self):
        """Setup base pricing models for different market segments"""
        self.base_models = {
            'premium': PricingModel(
                base_price=0.12,
                demand_multiplier=1.5,
                quality_premium=1.3,
                time_of_day_factor=1.0,
                regional_adjustment=1.0,
                competition_factor=0.9,
                profit_margin=0.4,
                minimum_price=0.08,
                maximum_price=0.25
            ),
            'standard': PricingModel(
                base_price=0.08,
                demand_multiplier=1.2,
                quality_premium=1.0,
                time_of_day_factor=1.0,
                regional_adjustment=1.0,
                competition_factor=0.95,
                profit_margin=0.3,
                minimum_price=0.05,
                maximum_price=0.18
            ),
            'budget': PricingModel(
                base_price=0.05,
                demand_multiplier=1.1,
                quality_premium=0.8,
                time_of_day_factor=1.0,
                regional_adjustment=1.0,
                competition_factor=1.0,
                profit_margin=0.2,
                minimum_price=0.03,
                maximum_price=0.12
            )
        }
    
    def calculate_optimal_price(self, country: str, service: str, provider: str, 
                              quality_tier: str = 'standard') -> Dict[str, Any]:
        """Calculate optimal price using dynamic pricing algorithm"""
        with self.lock:
            model = self.base_models.get(quality_tier, self.base_models['standard'])
            
            # Get market factors
            demand_factor = self._calculate_demand_factor(country, service)
            supply_factor = self._calculate_supply_factor(country, service)
            time_factor = self._calculate_time_factor()
            regional_factor = self._calculate_regional_factor(country)
            competition_factor = self._calculate_competition_factor(country, service, model.base_price)
            
            # Calculate base price with all factors
            adjusted_price = (
                model.base_price * 
                model.demand_multiplier * demand_factor *
                model.quality_premium *
                time_factor *
                regional_factor *
                competition_factor
            )
            
            # Apply constraints
            final_price = max(model.minimum_price, min(model.maximum_price, adjusted_price))
            
            # Calculate profit metrics
            cost_estimate = final_price * (1 - model.profit_margin)
            profit_estimate = final_price - cost_estimate
            
            return {
                'optimized_price': round(final_price, 4),
                'base_price': model.base_price,
                'demand_factor': demand_factor,
                'supply_factor': supply_factor,
                'time_factor': time_factor,
                'regional_factor': regional_factor,
                'competition_factor': competition_factor,
                'profit_margin': model.profit_margin,
                'estimated_cost': round(cost_estimate, 4),
                'estimated_profit': round(profit_estimate, 4),
                'quality_tier': quality_tier,
                'price_confidence': self._calculate_confidence_score(country, service)
            }
    
    def _calculate_demand_factor(self, country: str, service: str) -> float:
        """Calculate demand-based pricing factor"""
        predicted_demand = self.demand_predictor.predict_demand(country, service)
        
        # Convert demand level to pricing factor
        if predicted_demand > 0.8:
            return 1.4  # High demand - increase prices
        elif predicted_demand > 0.6:
            return 1.2
        elif predicted_demand > 0.4:
            return 1.0
        elif predicted_demand > 0.2:
            return 0.9
        else:
            return 0.8  # Low demand - decrease prices
    
    def _calculate_supply_factor(self, country: str, service: str) -> float:
        """Calculate supply-based pricing factor"""
        # Mock supply calculation - in production, integrate with provider APIs
        import random
        supply_level = random.uniform(0.3, 0.9)
        
        # Lower supply = higher prices
        return 2.0 - supply_level
    
    def _calculate_time_factor(self) -> float:
        """Calculate time-based pricing factor"""
        current_hour = datetime.now().hour
        
        # Peak hours (9 AM - 6 PM) get higher pricing
        if 9 <= current_hour <= 18:
            return 1.1
        # Evening hours get moderate pricing
        elif 18 < current_hour <= 23:
            return 1.05
        # Night/early morning get lower pricing
        else:
            return 0.95
    
    def _calculate_regional_factor(self, country: str) -> float:
        """Calculate regional pricing adjustment"""
        regional_multipliers = {
            'United States': 1.2,
            'United Kingdom': 1.15,
            'Germany': 1.1,
            'France': 1.08,
            'Canada': 1.05,
            'Russia': 0.8,
            'Poland': 0.85,
            'Netherlands': 1.12,
            'Sweden': 1.18,
            'Norway': 1.25
        }
        
        return regional_multipliers.get(country, 1.0)
    
    def _calculate_competition_factor(self, country: str, service: str, our_price: float) -> float:
        """Calculate competition-based pricing factor"""
        market_position = self.competitor_analyzer.get_market_position(country, service, our_price)
        
        if market_position['position'] == 'overpriced':
            return 0.85  # Reduce prices to compete
        elif market_position['position'] == 'price_leader':
            return 1.05  # Slight premium for being cheapest
        elif market_position['position'] == 'premium':
            return 1.0   # Maintain premium positioning
        else:
            return 0.98  # Slight competitive adjustment
    
    def _calculate_confidence_score(self, country: str, service: str) -> float:
        """Calculate confidence in price recommendation"""
        # Factors that increase confidence:
        # - More historical data
        # - Recent competitor data
        # - Stable demand patterns
        
        base_confidence = 0.7
        
        # Check historical data availability
        key = f"{country}:{service}"
        if hasattr(self.competitor_analyzer, 'competitor_data'):
            if key in self.competitor_analyzer.competitor_data:
                base_confidence += 0.2
        
        # Check demand prediction data
        relevant_demand_data = [
            d for d in self.demand_predictor.historical_data
            if d['country'] == country and d['service'] == service
        ]
        
        if len(relevant_demand_data) > 10:
            base_confidence += 0.1
        
        return min(1.0, base_confidence)

class RevenueOptimizer:
    """Main revenue optimization system"""
    
    def __init__(self, db_path: str = "revenue_optimizer.db"):
        self.db_path = db_path
        self.pricing_engine = DynamicPricingEngine()
        self.revenue_metrics = []
        self.optimization_strategies = {}
        self.lock = threading.RLock()
        
        self._init_database()
        self._setup_optimization_strategies()
        
    def _init_database(self):
        """Initialize revenue tracking database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS revenue_transactions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    country TEXT,
                    service TEXT,
                    provider TEXT,
                    quantity INTEGER,
                    unit_price REAL,
                    total_amount REAL,
                    profit_margin REAL,
                    transaction_date TEXT,
                    optimization_strategy TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pricing_history (
                    id TEXT PRIMARY KEY,
                    country TEXT,
                    service TEXT,
                    provider TEXT,
                    old_price REAL,
                    new_price REAL,
                    reason TEXT,
                    timestamp TEXT,
                    performance_impact REAL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS revenue_metrics (
                    id TEXT PRIMARY KEY,
                    period_start TEXT,
                    period_end TEXT,
                    total_revenue REAL,
                    total_transactions INTEGER,
                    average_order_value REAL,
                    profit_margin REAL,
                    customer_count INTEGER,
                    conversion_rate REAL
                )
            """)
            
            conn.commit()
    
    def _setup_optimization_strategies(self):
        """Setup revenue optimization strategies"""
        self.optimization_strategies = {
            'dynamic_pricing': {
                'name': 'Dynamic Pricing',
                'description': 'Adjust prices based on demand, supply, and competition',
                'impact_score': 0.8,
                'implementation_difficulty': 'medium',
                'expected_revenue_lift': 0.15
            },
            'bulk_discounts': {
                'name': 'Progressive Bulk Discounts',
                'description': 'Offer increasing discounts for larger quantities',
                'impact_score': 0.6,
                'implementation_difficulty': 'easy',
                'expected_revenue_lift': 0.08
            },
            'time_based_pricing': {
                'name': 'Time-Based Pricing',
                'description': 'Peak and off-peak pricing strategies',
                'impact_score': 0.5,
                'implementation_difficulty': 'easy',
                'expected_revenue_lift': 0.05
            },
            'geographic_pricing': {
                'name': 'Geographic Price Optimization',
                'description': 'Adjust prices based on regional economic factors',
                'impact_score': 0.7,
                'implementation_difficulty': 'medium',
                'expected_revenue_lift': 0.12
            },
            'customer_segmentation': {
                'name': 'Customer Segment Pricing',
                'description': 'Different pricing for premium vs budget customers',
                'impact_score': 0.9,
                'implementation_difficulty': 'hard',
                'expected_revenue_lift': 0.20
            }
        }
    
    def optimize_pricing(self, country: str, service: str, provider: str, 
                        current_price: float, quality_tier: str = 'standard') -> Dict[str, Any]:
        """Get optimized pricing recommendation"""
        
        # Get dynamic pricing recommendation
        pricing_result = self.pricing_engine.calculate_optimal_price(
            country, service, provider, quality_tier
        )
        
        # Calculate potential revenue impact
        price_change = pricing_result['optimized_price'] - current_price
        price_change_percent = (price_change / current_price) * 100 if current_price > 0 else 0
        
        # Estimate demand elasticity impact
        demand_impact = self._estimate_demand_impact(price_change_percent)
        
        # Calculate revenue projection
        current_revenue_estimate = current_price * 100  # Assume 100 units baseline
        new_revenue_estimate = pricing_result['optimized_price'] * 100 * (1 + demand_impact)
        revenue_change = new_revenue_estimate - current_revenue_estimate
        
        return {
            **pricing_result,
            'current_price': current_price,
            'price_change': round(price_change, 4),
            'price_change_percent': round(price_change_percent, 2),
            'estimated_demand_impact': round(demand_impact, 3),
            'estimated_revenue_change': round(revenue_change, 2),
            'recommendation': self._get_pricing_recommendation(price_change_percent),
            'implementation_priority': self._calculate_priority(abs(price_change_percent), pricing_result['price_confidence'])
        }
    
    def _estimate_demand_impact(self, price_change_percent: float) -> float:
        """Estimate demand change based on price elasticity"""
        # SMS services typically have moderate price elasticity
        # Simplified elasticity model
        elasticity = -0.8  # 1% price increase = 0.8% demand decrease
        
        return elasticity * (price_change_percent / 100)
    
    def _get_pricing_recommendation(self, price_change_percent: float) -> str:
        """Get human-readable pricing recommendation"""
        if abs(price_change_percent) < 2:
            return "maintain_current_pricing"
        elif price_change_percent > 5:
            return "significant_price_increase_recommended"
        elif price_change_percent > 0:
            return "moderate_price_increase_recommended"
        elif price_change_percent < -5:
            return "significant_price_decrease_recommended"
        else:
            return "moderate_price_decrease_recommended"
    
    def _calculate_priority(self, price_change_percent: float, confidence: float) -> str:
        """Calculate implementation priority"""
        impact_score = price_change_percent * confidence
        
        if impact_score > 8:
            return "high"
        elif impact_score > 3:
            return "medium"
        else:
            return "low"
    
    def track_transaction(self, user_id: str, country: str, service: str, provider: str,
                         quantity: int, unit_price: float, optimization_strategy: str = None):
        """Track revenue transaction"""
        transaction_id = str(uuid.uuid4())
        total_amount = quantity * unit_price
        
        # Estimate profit margin (would use real cost data in production)
        estimated_cost = unit_price * 0.7  # Assume 30% margin
        profit_margin = (unit_price - estimated_cost) / unit_price
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO revenue_transactions 
                (id, user_id, country, service, provider, quantity, unit_price, 
                 total_amount, profit_margin, transaction_date, optimization_strategy)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (transaction_id, user_id, country, service, provider, quantity,
                  unit_price, total_amount, profit_margin, datetime.now().isoformat(),
                  optimization_strategy))
            conn.commit()
        
        # Record demand data
        demand_level = min(1.0, quantity / 10.0)  # Normalize quantity to demand level
        self.pricing_engine.demand_predictor.record_demand(country, service, demand_level)
    
    def get_revenue_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive revenue analytics"""
        start_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_transactions,
                    SUM(total_amount) as total_revenue,
                    AVG(total_amount) as avg_order_value,
                    AVG(profit_margin) as avg_profit_margin,
                    COUNT(DISTINCT user_id) as unique_customers
                FROM revenue_transactions
                WHERE datetime(transaction_date) > datetime(?)
            """, (start_date.isoformat(),))
            
            results = cursor.fetchone()
            
            if not results or not results[0]:
                return self._get_empty_analytics()
            
            # Calculate additional metrics
            conversion_rate = 0.15  # Mock conversion rate
            customer_lifetime_value = results[1] / results[4] if results[4] > 0 else 0
            
            return {
                'period_days': days,
                'total_transactions': results[0],
                'total_revenue': round(results[1] or 0, 2),
                'average_order_value': round(results[2] or 0, 2),
                'average_profit_margin': round((results[3] or 0) * 100, 2),
                'unique_customers': results[4] or 0,
                'estimated_conversion_rate': round(conversion_rate * 100, 2),
                'customer_lifetime_value': round(customer_lifetime_value, 2),
                'revenue_per_day': round((results[1] or 0) / days, 2),
                'transactions_per_day': round((results[0] or 0) / days, 1)
            }
    
    def _get_empty_analytics(self) -> Dict[str, Any]:
        """Return empty analytics structure"""
        return {
            'period_days': 0,
            'total_transactions': 0,
            'total_revenue': 0,
            'average_order_value': 0,
            'average_profit_margin': 0,
            'unique_customers': 0,
            'estimated_conversion_rate': 0,
            'customer_lifetime_value': 0,
            'revenue_per_day': 0,
            'transactions_per_day': 0
        }
    
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get top optimization recommendations"""
        recommendations = []
        
        for strategy_id, strategy in self.optimization_strategies.items():
            recommendations.append({
                'strategy_id': strategy_id,
                'name': strategy['name'],
                'description': strategy['description'],
                'expected_revenue_lift': f"{strategy['expected_revenue_lift']*100:.1f}%",
                'impact_score': strategy['impact_score'],
                'difficulty': strategy['implementation_difficulty'],
                'priority': self._calculate_strategy_priority(strategy)
            })
        
        # Sort by impact score descending
        recommendations.sort(key=lambda x: x['impact_score'], reverse=True)
        
        return recommendations
    
    def _calculate_strategy_priority(self, strategy: Dict) -> str:
        """Calculate strategy implementation priority"""
        difficulty_scores = {'easy': 1, 'medium': 2, 'hard': 3}
        
        # Priority based on impact vs difficulty ratio
        ratio = strategy['impact_score'] / difficulty_scores[strategy['implementation_difficulty']]
        
        if ratio > 0.4:
            return 'high'
        elif ratio > 0.25:
            return 'medium'
        else:
            return 'low'
    
    def simulate_pricing_strategy(self, strategy_params: Dict) -> Dict[str, Any]:
        """Simulate potential impact of pricing strategy"""
        
        # Mock simulation - in production would use historical data
        baseline_revenue = 10000  # Monthly revenue
        baseline_transactions = 500
        
        # Apply strategy parameters
        price_adjustment = strategy_params.get('price_adjustment', 0)  # Percentage
        expected_demand_change = self._estimate_demand_impact(price_adjustment)
        
        new_transactions = baseline_transactions * (1 + expected_demand_change)
        new_avg_price = strategy_params.get('base_price', 0.08) * (1 + price_adjustment/100)
        new_revenue = new_transactions * new_avg_price
        
        return {
            'baseline_revenue': baseline_revenue,
            'projected_revenue': round(new_revenue, 2),
            'revenue_change': round(new_revenue - baseline_revenue, 2),
            'revenue_change_percent': round(((new_revenue - baseline_revenue) / baseline_revenue) * 100, 2),
            'baseline_transactions': baseline_transactions,
            'projected_transactions': round(new_transactions),
            'transaction_change': round(new_transactions - baseline_transactions),
            'new_average_price': round(new_avg_price, 4),
            'strategy_effectiveness': 'high' if new_revenue > baseline_revenue * 1.1 else 'moderate' if new_revenue > baseline_revenue else 'low'
        }

# Global revenue optimizer instance
revenue_optimizer = RevenueOptimizer()

def get_revenue_optimizer() -> RevenueOptimizer:
    """Get global revenue optimizer instance"""
    return revenue_optimizer