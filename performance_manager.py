#!/usr/bin/env python3
"""
Performance Manager for SMS Marketplace
Handles async operations, connection pooling, caching, and load balancing
"""

import asyncio
import aiohttp
import time
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import defaultdict
import json
import hashlib
from concurrent.futures import ThreadPoolExecutor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CacheItem:
    data: Any
    timestamp: float
    expires_at: float
    
    def is_expired(self) -> bool:
        return time.time() > self.expires_at

class MemoryCache:
    """High-performance in-memory cache with TTL support"""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.cache: Dict[str, CacheItem] = {}
        self.default_ttl = default_ttl
        self._lock = threading.RLock()
        
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key in self.cache:
                item = self.cache[key]
                if not item.is_expired():
                    return item.data
                else:
                    del self.cache[key]
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        ttl = ttl or self.default_ttl
        expires_at = time.time() + ttl
        
        with self._lock:
            self.cache[key] = CacheItem(
                data=value,
                timestamp=time.time(),
                expires_at=expires_at
            )
    
    def delete(self, key: str) -> None:
        with self._lock:
            if key in self.cache:
                del self.cache[key]
    
    def clear(self) -> None:
        with self._lock:
            self.cache.clear()
    
    def cleanup_expired(self) -> None:
        """Remove expired items from cache"""
        with self._lock:
            expired_keys = [
                key for key, item in self.cache.items() 
                if item.is_expired()
            ]
            for key in expired_keys:
                del self.cache[key]

class ConnectionPool:
    """Async HTTP connection pool manager"""
    
    def __init__(self, max_connections: int = 100, max_per_host: int = 30):
        self.max_connections = max_connections
        self.max_per_host = max_per_host
        self.session: Optional[aiohttp.ClientSession] = None
        self.connector: Optional[aiohttp.TCPConnector] = None
        
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create async HTTP session with connection pooling"""
        if self.session is None or self.session.closed:
            self.connector = aiohttp.TCPConnector(
                limit=self.max_connections,
                limit_per_host=self.max_per_host,
                ttl_dns_cache=300,
                use_dns_cache=True,
                keepalive_timeout=30,
                enable_cleanup_closed=True
            )
            
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self.session = aiohttp.ClientSession(
                connector=self.connector,
                timeout=timeout,
                headers={'User-Agent': 'SMS-Marketplace-Pro/2.0'}
            )
        
        return self.session
    
    async def close(self):
        """Clean up connections"""
        if self.session and not self.session.closed:
            await self.session.close()
        if self.connector:
            await self.connector.close()

class LoadBalancer:
    """Simple round-robin load balancer for API endpoints"""
    
    def __init__(self):
        self.endpoints: Dict[str, List[str]] = defaultdict(list)
        self.current_index: Dict[str, int] = defaultdict(int)
        self._lock = threading.Lock()
    
    def add_endpoint(self, service: str, endpoint: str):
        """Add endpoint for a service"""
        with self._lock:
            if endpoint not in self.endpoints[service]:
                self.endpoints[service].append(endpoint)
    
    def get_endpoint(self, service: str) -> Optional[str]:
        """Get next endpoint using round-robin"""
        with self._lock:
            if not self.endpoints[service]:
                return None
            
            endpoint = self.endpoints[service][self.current_index[service]]
            self.current_index[service] = (
                self.current_index[service] + 1
            ) % len(self.endpoints[service])
            
            return endpoint
    
    def remove_endpoint(self, service: str, endpoint: str):
        """Remove failed endpoint"""
        with self._lock:
            if endpoint in self.endpoints[service]:
                self.endpoints[service].remove(endpoint)
                # Reset index if needed
                if self.current_index[service] >= len(self.endpoints[service]):
                    self.current_index[service] = 0

class PerformanceManager:
    """Main performance management class"""
    
    def __init__(self, max_workers: int = 10):
        self.cache = MemoryCache()
        self.connection_pool = ConnectionPool()
        self.load_balancer = LoadBalancer()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.metrics = {
            'requests_total': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'response_times': [],
            'active_connections': 0,
            'failed_requests': 0
        }
        
        # Setup load balancer endpoints
        self._setup_endpoints()
        
        # Start background cleanup task
        self._start_cleanup_task()
    
    def _setup_endpoints(self):
        """Setup multiple endpoints for load balancing"""
        # SMS-Activate endpoints
        self.load_balancer.add_endpoint('sms-activate', 'https://api.sms-activate.org')
        self.load_balancer.add_endpoint('sms-activate', 'https://api.sms-activate.io')
        
        # 5SIM endpoints  
        self.load_balancer.add_endpoint('5sim', 'https://5sim.net/v1')
        self.load_balancer.add_endpoint('5sim', 'https://api.5sim.net/v1')
        
        # Add more providers
        self.load_balancer.add_endpoint('smshub', 'https://smshub.org/api')
        self.load_balancer.add_endpoint('getsmscode', 'https://getsmscode.com/api')
    
    def _start_cleanup_task(self):
        """Start background cleanup task"""
        def cleanup_loop():
            while True:
                time.sleep(60)  # Cleanup every minute
                self.cache.cleanup_expired()
                self._cleanup_metrics()
        
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
    
    def _cleanup_metrics(self):
        """Keep metrics manageable"""
        if len(self.metrics['response_times']) > 1000:
            self.metrics['response_times'] = self.metrics['response_times'][-500:]
    
    async def async_request(self, method: str, service: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """Make async HTTP request with caching and load balancing"""
        start_time = time.time()
        
        # Generate cache key
        cache_key = self._generate_cache_key(method, service, endpoint, kwargs)
        
        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            self.metrics['cache_hits'] += 1
            return cached_result
        
        self.metrics['cache_misses'] += 1
        
        # Get endpoint from load balancer
        base_url = self.load_balancer.get_endpoint(service)
        if not base_url:
            logger.error(f"No endpoints available for service: {service}")
            return None
        
        full_url = f"{base_url}/{endpoint.lstrip('/')}"
        
        try:
            session = await self.connection_pool.get_session()
            self.metrics['active_connections'] += 1
            
            async with session.request(method, full_url, **kwargs) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Cache successful response
                    self.cache.set(cache_key, data, ttl=60)  # Cache for 1 minute
                    
                    response_time = time.time() - start_time
                    self.metrics['response_times'].append(response_time)
                    self.metrics['requests_total'] += 1
                    
                    return data
                else:
                    logger.warning(f"Request failed: {response.status} for {full_url}")
                    self.metrics['failed_requests'] += 1
                    return None
                    
        except Exception as e:
            logger.error(f"Request error: {e} for {full_url}")
            self.metrics['failed_requests'] += 1
            # Remove failed endpoint
            self.load_balancer.remove_endpoint(service, base_url)
            return None
        finally:
            self.metrics['active_connections'] -= 1
    
    def _generate_cache_key(self, method: str, service: str, endpoint: str, kwargs: Dict) -> str:
        """Generate cache key for request"""
        key_data = f"{method}:{service}:{endpoint}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def batch_requests(self, requests: List[Dict]) -> List[Optional[Dict]]:
        """Execute multiple requests concurrently"""
        tasks = []
        for req in requests:
            task = self.async_request(
                req.get('method', 'GET'),
                req['service'],
                req['endpoint'],
                **req.get('kwargs', {})
            )
            tasks.append(task)
        
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    def sync_request(self, method: str, service: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """Synchronous wrapper for async requests"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.async_request(method, service, endpoint, **kwargs)
            )
        finally:
            loop.close()
    
    def get_metrics(self) -> Dict:
        """Get performance metrics"""
        avg_response_time = 0
        if self.metrics['response_times']:
            avg_response_time = sum(self.metrics['response_times']) / len(self.metrics['response_times'])
        
        cache_hit_rate = 0
        total_cache_requests = self.metrics['cache_hits'] + self.metrics['cache_misses']
        if total_cache_requests > 0:
            cache_hit_rate = self.metrics['cache_hits'] / total_cache_requests
        
        return {
            'requests_total': self.metrics['requests_total'],
            'cache_hit_rate': cache_hit_rate,
            'avg_response_time': avg_response_time,
            'active_connections': self.metrics['active_connections'],
            'failed_requests': self.metrics['failed_requests'],
            'cache_size': len(self.cache.cache)
        }
    
    async def close(self):
        """Clean up resources"""
        await self.connection_pool.close()
        self.executor.shutdown(wait=True)

# Global performance manager instance
performance_manager = PerformanceManager()

def get_performance_manager() -> PerformanceManager:
    """Get global performance manager instance"""
    return performance_manager