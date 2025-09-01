"""
Thread-safe version of ProxyRotator to fix concurrency issues.

This addresses the main problems that prevent handling parallel requests:
1. Race conditions in shared state access
2. Non-atomic operations on statistics
3. Thread safety in proxy selection
"""

import time
import threading
import logging
from collections import defaultdict, deque
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from mitmproxy import http

from .config import Config, ProxyConfig
from .strategies import create_strategy


class ThreadSafeProxyRotator:
    """Thread-safe version of ProxyRotator that can handle concurrent requests."""
    
    def __init__(self, config: Config):
        """Initialize thread-safe proxy rotator."""
        self.config = config
        self.strategy = create_strategy(config.strategy)
        
        # Thread safety locks
        self._stats_lock = threading.RLock()  # Reentrant lock for nested calls
        self._health_lock = threading.RLock()
        self._selection_lock = threading.Lock()  # Fast lock for proxy selection
        
        # Health tracking (protected by _health_lock)
        self.health_scores: Dict[str, float] = {}
        self.failure_counts: Dict[str, int] = defaultdict(int)
        self.failed_proxy_timestamps: Dict[str, float] = {}
        
        # Statistics tracking (protected by _stats_lock)
        self.stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'response_times': deque(maxlen=100),
            'recent_successes': deque(maxlen=20),
            'last_used': 0,
            'first_used': 0
        })
        
        # Global statistics (atomic operations where possible)
        self._total_requests = 0
        self._total_failures = 0
        self.start_time = time.time()
        
        # Initialize proxy health scores
        with self._health_lock:
            for proxy in config.proxy_list:
                self.health_scores[proxy.id] = 1.0

        print(f"🌍 Loaded {len(config.proxy_list)} proxies for rotation")
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Start background tasks
        self._start_background_tasks()
    
    def _start_background_tasks(self) -> None:
        """Start background monitoring tasks."""
        if self.config.stats_interval > 0:
            stats_thread = threading.Thread(
                target=self._stats_loop, 
                daemon=True,
                name="RotatorStatsThread"
            )
            stats_thread.start()
    
    def requestheaders(self, flow: http.HTTPFlow) -> None:
        """Handle request headers - simple connection-based proxy switching."""
        # Atomic increment of total requests
        with self._stats_lock:
            self._total_requests += 1

        # Check if this is a new connection using multiple indicators
        is_new_connection = True

        if hasattr(flow, 'server_conn') and flow.server_conn:
            # Check multiple indicators that suggest connection reuse
            connection_indicators = [
                # Already has a proxy set
                hasattr(flow.server_conn, 'via') and flow.server_conn.via is not None,
                # Connection is already established
                hasattr(flow.server_conn, 'connected') and flow.server_conn.connected,
                # Connection has been used before
                hasattr(flow.server_conn, 'timestamp_start') and flow.server_conn.timestamp_start is not None,
                # Connection has an established socket
                hasattr(flow.server_conn, 'sockname') and flow.server_conn.sockname is not None,
            ]

            # If any indicator suggests reuse, treat as existing connection
            if any(connection_indicators):
                is_new_connection = False

        if is_new_connection:
            # This is a new connection - select and set a proxy
            proxy = self._select_proxy_thread_safe()

            if proxy:
                try:
                    # Double-check connection state before setting proxy
                    if (hasattr(flow.server_conn, 'connected') and flow.server_conn.connected) or \
                       (hasattr(flow.server_conn, 'via') and flow.server_conn.via is not None):
                        flow.metadata["selected_proxy"] = proxy.id
                        flow.metadata["request_start_time"] = time.time()
                        flow.metadata["connection_reused"] = True
                        return

                    # Set the upstream proxy
                    flow.server_conn.via = (
                        "http",  # scheme
                        (proxy.host, proxy.port)  # address tuple
                    )

                    # Store metadata for response handling
                    flow.metadata["selected_proxy"] = proxy.id
                    flow.metadata["request_start_time"] = time.time()

                    # Only log when we actually set a new proxy
                    print(f"🌍 Using proxy: {proxy.id}")

                    # Update statistics atomically
                    with self._stats_lock:
                        proxy_stats = self.stats[proxy.id]
                        proxy_stats['total_requests'] += 1
                        proxy_stats['last_used'] = time.time()
                        if proxy_stats['first_used'] == 0:
                            proxy_stats['first_used'] = time.time()

                except Exception as e:
                    self.logger.error(f"Proxy setup failed: {e}")
                    flow.metadata["selected_proxy"] = proxy.id if proxy else "none"
                    flow.metadata["request_start_time"] = time.time()
                    flow.metadata["proxy_failed"] = True
            else:
                self.logger.error("No healthy proxies available!")
                flow.metadata["no_proxy"] = True
        else:
            # This is a reused connection - just track it silently
            flow.metadata["connection_reused"] = True
            flow.metadata["request_start_time"] = time.time()
    
    def response(self, flow: http.HTTPFlow) -> None:
        """Handle response - update proxy health and statistics (minimal logging)."""
        request_start_time = flow.metadata.get("request_start_time", time.time())
        response_time = time.time() - request_start_time

        # Handle different scenarios
        if "selected_proxy" in flow.metadata:
            proxy_id = flow.metadata["selected_proxy"]
            proxy_failed = flow.metadata.get("proxy_failed", False)
            success = self._is_request_successful(flow)

            # Update statistics for successful proxy setups only
            if not proxy_failed:
                with self._stats_lock:
                    proxy_stats = self.stats[proxy_id]
                    proxy_stats['response_times'].append(response_time)

                    if success:
                        proxy_stats['successful_requests'] += 1
                        proxy_stats['recent_successes'].append(1)
                    else:
                        proxy_stats['failed_requests'] += 1
                        proxy_stats['recent_successes'].append(0)
                        self._total_failures += 1

        # No logging for connection reuse or other scenarios - keep it clean
    
    def _select_proxy_thread_safe(self) -> Optional[ProxyConfig]:
        """Thread-safe proxy selection."""
        with self._selection_lock:
            # Get available proxies (not in timeout)
            available_proxies = self._get_available_proxies_thread_safe()
            
            if not available_proxies:
                self.logger.warning("No available proxies! Attempting recovery...")
                available_proxies = self._attempt_recovery_thread_safe()
            
            if not available_proxies:
                return None
            
            # Create thread-safe copies of health scores and stats for strategy
            with self._health_lock:
                health_scores_copy = self.health_scores.copy()
            
            with self._stats_lock:
                # Create a simplified stats copy for strategy
                stats_copy = {}
                for proxy_id, proxy_stats in self.stats.items():
                    stats_copy[proxy_id] = {
                        'total_requests': proxy_stats['total_requests'],
                        'successful_requests': proxy_stats['successful_requests'],
                        'failed_requests': proxy_stats['failed_requests'],
                        'response_times': list(proxy_stats['response_times']),
                        'recent_successes': list(proxy_stats['recent_successes']),
                        'last_used': proxy_stats['last_used']
                    }
            
            # Use strategy to select proxy
            return self.strategy.select_proxy(
                available_proxies, 
                health_scores_copy, 
                stats_copy
            )
    
    def _get_available_proxies_thread_safe(self) -> List[ProxyConfig]:
        """Get list of available proxies (thread-safe)."""
        available = []
        current_time = time.time()
        
        with self._health_lock:
            for proxy in self.config.proxy_list:
                # Check if proxy is in timeout
                if proxy.id in self.failed_proxy_timestamps:
                    time_since_failure = current_time - self.failed_proxy_timestamps[proxy.id]
                    if time_since_failure < self.config.failure_timeout:
                        continue  # Still in timeout
                    else:
                        # Remove from timeout
                        del self.failed_proxy_timestamps[proxy.id]
                        self.failure_counts[proxy.id] = 0
                        self.health_scores[proxy.id] = 0.5  # Partial recovery
                
                # Check minimum health score
                health = self.health_scores.get(proxy.id, 1.0)
                if health >= self.config.min_health_score:
                    available.append(proxy)
        
        return available
    
    def _attempt_recovery_thread_safe(self) -> List[ProxyConfig]:
        """Attempt to recover failed proxies (thread-safe)."""
        with self._health_lock:
            # If no proxies meet minimum health, lower the bar
            if not any(score >= self.config.min_health_score for score in self.health_scores.values()):
                # Return proxies with any positive health score
                available = [
                    proxy for proxy in self.config.proxy_list
                    if self.health_scores.get(proxy.id, 1.0) > 0.0
                ]
                if available:
                    return available
            
            # Last resort: return least bad proxy
            if self.config.proxy_list:
                least_bad = min(
                    self.config.proxy_list,
                    key=lambda p: self.failure_counts[p.id]
                )
                self.health_scores[least_bad.id] = 0.1
                return [least_bad]
        
        return []
    
    def _handle_proxy_success_thread_safe(self, proxy_id: str, response_time: float) -> None:
        """Handle successful proxy response (thread-safe)."""
        with self._health_lock:
            # Reset failure count
            self.failure_counts[proxy_id] = 0
            
            # Remove from failed list if present
            self.failed_proxy_timestamps.pop(proxy_id, None)
            
            # Improve health score
            current_health = self.health_scores.get(proxy_id, 1.0)
            improvement = 0.1 if response_time < 2.0 else 0.05
            self.health_scores[proxy_id] = min(1.0, current_health + improvement)
    
    def _handle_proxy_failure_thread_safe(self, proxy_id: str, flow: http.HTTPFlow) -> None:
        """Handle failed proxy response (thread-safe)."""
        with self._health_lock:
            # Increment failure count
            self.failure_counts[proxy_id] += 1
            
            # Calculate penalty based on error type
            if flow.response is None:
                penalty = 0.3  # Connection failed
            elif flow.response.status_code >= 500:
                penalty = 0.2  # Server error
            elif flow.response.status_code in [403, 429]:
                penalty = 0.25  # Blocked/rate limited
            else:
                penalty = 0.1  # Other errors
            
            # Decrease health score
            current_health = self.health_scores.get(proxy_id, 1.0)
            self.health_scores[proxy_id] = max(0.0, current_health - penalty)
            
            # Put proxy in timeout if too many failures
            if self.failure_counts[proxy_id] >= self.config.max_failures:
                self.failed_proxy_timestamps[proxy_id] = time.time()
                self.logger.warning(
                    f"Proxy {proxy_id} failed {self.config.max_failures} times, "
                    f"putting in timeout for {self.config.failure_timeout}s"
                )
    
    def _is_request_successful(self, flow: http.HTTPFlow) -> bool:
        """Determine if a request was successful."""
        if flow.response is None:
            return False  # Connection failed
        
        status = flow.response.status_code
        
        # Define success criteria
        if status < 400:
            return True
        elif status in [403, 429, 503]:  # Blocked/rate limited/unavailable
            return False
        elif status >= 500:  # Server errors (might be proxy issue)
            return False
        else:
            # 4xx client errors might not be proxy's fault
            return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics (thread-safe)."""
        # Always acquire locks in consistent order: health -> stats -> selection
        with self._health_lock:
            with self._stats_lock:
                # Calculate aggregate stats
                total_requests = self._total_requests
                total_failures = self._total_failures
                success_rate = (total_requests - total_failures) / total_requests if total_requests > 0 else 0

                # Count healthy proxies
                healthy_proxies = sum(1 for score in self.health_scores.values() if score >= self.config.min_health_score)

                # Proxy details
                proxy_details = []
                for proxy in self.config.proxy_list:
                    proxy_stats = self.stats[proxy.id]
                    health_score = self.health_scores.get(proxy.id, 1.0)

                    # Calculate average response time
                    response_times = list(proxy_stats['response_times'])
                    avg_response_time = sum(response_times) / len(response_times) if response_times else 0

                    # Calculate success rate
                    proxy_success_rate = (
                        proxy_stats['successful_requests'] / proxy_stats['total_requests']
                        if proxy_stats['total_requests'] > 0 else 0
                    )

                    proxy_details.append({
                        'id': proxy.id,
                        'health_score': health_score,
                        'total_requests': proxy_stats['total_requests'],
                        'successful_requests': proxy_stats['successful_requests'],
                        'failed_requests': proxy_stats['failed_requests'],
                        'success_rate': proxy_success_rate,
                        'avg_response_time': avg_response_time,
                        'last_used': proxy_stats['last_used'],
                        'in_timeout': proxy.id in self.failed_proxy_timestamps
                    })

                return {
                    'total_requests': total_requests,
                    'total_failures': total_failures,
                    'success_rate': success_rate,
                    'healthy_proxies': healthy_proxies,
                    'total_proxies': len(self.config.proxy_list),
                    'strategy': self.config.strategy,
                    'uptime': time.time() - self.start_time,
                    'proxy_details': proxy_details
                }
    
    def _stats_loop(self) -> None:
        """Background thread for periodic statistics logging."""
        while True:
            time.sleep(self.config.stats_interval)
            try:
                stats = self.get_statistics()
                self.logger.info(
                    f"Stats: {stats['total_requests']} requests, "
                    f"{stats['success_rate']:.2%} success rate, "
                    f"{stats['healthy_proxies']}/{stats['total_proxies']} healthy proxies"
                )
            except Exception as e:
                self.logger.error(f"Error in stats loop: {e}")


# Alias for backward compatibility
ProxyRotator = ThreadSafeProxyRotator
