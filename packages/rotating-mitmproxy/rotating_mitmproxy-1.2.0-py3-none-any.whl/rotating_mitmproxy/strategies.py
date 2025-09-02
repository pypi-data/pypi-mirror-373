"""Proxy selection strategies for rotating mitmproxy."""

import random
import time
from abc import ABC, abstractmethod
from collections import deque
from typing import List, Optional

from .config import ProxyConfig


class SelectionStrategy(ABC):
    """Base class for proxy selection strategies."""
    
    @abstractmethod
    def select_proxy(self, proxies: List[ProxyConfig], health_scores: dict, 
                    stats: dict) -> Optional[ProxyConfig]:
        """Select a proxy from the available list."""
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset strategy state."""
        pass


class RoundRobinStrategy(SelectionStrategy):
    """Round-robin proxy selection strategy."""
    
    def __init__(self):
        self.current_index = 0
    
    def select_proxy(self, proxies: List[ProxyConfig], health_scores: dict, 
                    stats: dict) -> Optional[ProxyConfig]:
        """Select next proxy in round-robin order."""
        if not proxies:
            return None
        
        # Find next healthy proxy
        attempts = 0
        while attempts < len(proxies):
            proxy = proxies[self.current_index % len(proxies)]
            self.current_index += 1
            
            # Check if proxy is healthy enough
            health = health_scores.get(proxy.id, 1.0)
            if health > 0.1:  # Very low threshold for round-robin
                return proxy
            
            attempts += 1
        
        # If no healthy proxy found, return first one
        return proxies[0] if proxies else None
    
    def reset(self) -> None:
        """Reset round-robin counter."""
        self.current_index = 0


class RandomStrategy(SelectionStrategy):
    """Random proxy selection strategy."""
    
    def select_proxy(self, proxies: List[ProxyConfig], health_scores: dict, 
                    stats: dict) -> Optional[ProxyConfig]:
        """Select random proxy from healthy ones."""
        if not proxies:
            return None
        
        # Filter healthy proxies
        healthy_proxies = [
            proxy for proxy in proxies 
            if health_scores.get(proxy.id, 1.0) > 0.2
        ]
        
        if not healthy_proxies:
            # If no healthy proxies, use all
            healthy_proxies = proxies
        
        return random.choice(healthy_proxies)
    
    def reset(self) -> None:
        """Nothing to reset for random strategy."""
        pass


class FastestStrategy(SelectionStrategy):
    """Select proxy with best average response time."""
    
    def select_proxy(self, proxies: List[ProxyConfig], health_scores: dict, 
                    stats: dict) -> Optional[ProxyConfig]:
        """Select proxy with fastest average response time."""
        if not proxies:
            return None
        
        # Filter healthy proxies
        healthy_proxies = [
            proxy for proxy in proxies 
            if health_scores.get(proxy.id, 1.0) > 0.3
        ]
        
        if not healthy_proxies:
            healthy_proxies = proxies
        
        # Select proxy with best average response time
        best_proxy = None
        best_time = float('inf')
        
        for proxy in healthy_proxies:
            proxy_stats = stats.get(proxy.id, {})
            response_times = proxy_stats.get('response_times', deque())
            
            if response_times:
                avg_time = sum(response_times) / len(response_times)
            else:
                avg_time = 1.0  # Default for new proxies
            
            if avg_time < best_time:
                best_time = avg_time
                best_proxy = proxy
        
        return best_proxy or healthy_proxies[0]
    
    def reset(self) -> None:
        """Nothing to reset for fastest strategy."""
        pass


class SmartStrategy(SelectionStrategy):
    """Intelligent proxy selection based on multiple factors."""
    
    def select_proxy(self, proxies: List[ProxyConfig], health_scores: dict, 
                    stats: dict) -> Optional[ProxyConfig]:
        """Select proxy using smart scoring algorithm."""
        if not proxies:
            return None
        
        # Filter minimally healthy proxies
        candidate_proxies = [
            proxy for proxy in proxies 
            if health_scores.get(proxy.id, 1.0) > 0.1
        ]
        
        if not candidate_proxies:
            candidate_proxies = proxies
        
        # Score each proxy
        best_proxy = None
        best_score = -1
        
        for proxy in candidate_proxies:
            score = self._calculate_proxy_score(proxy, health_scores, stats)
            if score > best_score:
                best_score = score
                best_proxy = proxy
        
        return best_proxy
    
    def _calculate_proxy_score(self, proxy: ProxyConfig, health_scores: dict, 
                              stats: dict) -> float:
        """Calculate composite score for proxy selection."""
        proxy_id = proxy.id
        proxy_stats = stats.get(proxy_id, {})
        
        # Health score (0-1)
        health = health_scores.get(proxy_id, 1.0)
        
        # Success rate (0-1)
        total_requests = proxy_stats.get('total_requests', 0)
        successful_requests = proxy_stats.get('successful_requests', 0)
        success_rate = (successful_requests / total_requests) if total_requests > 0 else 0.5
        
        # Speed score (0-1, higher is better)
        response_times = proxy_stats.get('response_times', deque())
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            # Convert to score: faster = higher score
            speed_score = 1.0 / (1.0 + avg_time)
        else:
            speed_score = 0.5  # Neutral for new proxies
        
        # Recent performance (0-1)
        recent_successes = proxy_stats.get('recent_successes', deque())
        if recent_successes:
            recent_success_rate = sum(recent_successes) / len(recent_successes)
        else:
            recent_success_rate = 0.5
        
        # Weighted combination
        composite_score = (
            health * 0.30 +              # 30% health
            success_rate * 0.25 +        # 25% overall success rate
            speed_score * 0.20 +         # 20% speed
            recent_success_rate * 0.25   # 25% recent performance
        )
        
        return composite_score
    
    def reset(self) -> None:
        """Nothing to reset for smart strategy."""
        pass


def create_strategy(strategy_name: str) -> SelectionStrategy:
    """Factory function to create selection strategies."""
    strategies = {
        'round_robin': RoundRobinStrategy,
        'random': RandomStrategy,
        'fastest': FastestStrategy,
        'smart': SmartStrategy,
    }
    
    strategy_class = strategies.get(strategy_name.lower())
    if not strategy_class:
        raise ValueError(f"Unknown strategy: {strategy_name}")
    
    return strategy_class()
