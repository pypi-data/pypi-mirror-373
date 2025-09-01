"""Tests for proxy selection strategies."""

import pytest
from collections import deque

from rotating_mitmproxy.strategies import (
    RoundRobinStrategy,
    RandomStrategy,
    FastestStrategy,
    SmartStrategy,
    create_strategy
)
from rotating_mitmproxy.config import ProxyConfig


class TestRoundRobinStrategy:
    """Test round-robin strategy."""
    
    def test_round_robin_selection(self):
        """Test round-robin proxy selection."""
        strategy = RoundRobinStrategy()
        proxies = [
            ProxyConfig("proxy1.com", 8080),
            ProxyConfig("proxy2.com", 8080),
            ProxyConfig("proxy3.com", 8080)
        ]
        health_scores = {p.id: 1.0 for p in proxies}
        stats = {}
        
        # Should cycle through proxies in order
        selected1 = strategy.select_proxy(proxies, health_scores, stats)
        selected2 = strategy.select_proxy(proxies, health_scores, stats)
        selected3 = strategy.select_proxy(proxies, health_scores, stats)
        selected4 = strategy.select_proxy(proxies, health_scores, stats)
        
        assert selected1 == proxies[0]
        assert selected2 == proxies[1]
        assert selected3 == proxies[2]
        assert selected4 == proxies[0]  # Should wrap around
    
    def test_round_robin_with_unhealthy_proxies(self):
        """Test round-robin skips unhealthy proxies."""
        strategy = RoundRobinStrategy()
        proxies = [
            ProxyConfig("proxy1.com", 8080),
            ProxyConfig("proxy2.com", 8080),
            ProxyConfig("proxy3.com", 8080)
        ]
        health_scores = {
            "proxy1.com:8080": 0.05,  # Unhealthy
            "proxy2.com:8080": 0.8,   # Healthy
            "proxy3.com:8080": 0.9    # Healthy
        }
        stats = {}
        
        # Should skip unhealthy proxy
        selected1 = strategy.select_proxy(proxies, health_scores, stats)
        selected2 = strategy.select_proxy(proxies, health_scores, stats)
        selected3 = strategy.select_proxy(proxies, health_scores, stats)
        
        assert selected1 == proxies[1]  # Skip proxy1
        assert selected2 == proxies[2]
        assert selected3 == proxies[1]  # Wrap to proxy2
    
    def test_round_robin_empty_list(self):
        """Test round-robin with empty proxy list."""
        strategy = RoundRobinStrategy()
        result = strategy.select_proxy([], {}, {})
        assert result is None
    
    def test_reset(self):
        """Test strategy reset."""
        strategy = RoundRobinStrategy()
        proxies = [ProxyConfig("proxy1.com", 8080)]
        health_scores = {"proxy1.com:8080": 1.0}
        
        # Advance counter
        strategy.select_proxy(proxies, health_scores, {})
        assert strategy.current_index == 1
        
        # Reset should reset counter
        strategy.reset()
        assert strategy.current_index == 0


class TestRandomStrategy:
    """Test random strategy."""
    
    def test_random_selection(self):
        """Test random proxy selection."""
        strategy = RandomStrategy()
        proxies = [
            ProxyConfig("proxy1.com", 8080),
            ProxyConfig("proxy2.com", 8080),
            ProxyConfig("proxy3.com", 8080)
        ]
        health_scores = {p.id: 1.0 for p in proxies}
        stats = {}
        
        # Should return one of the proxies
        selected = strategy.select_proxy(proxies, health_scores, stats)
        assert selected in proxies
    
    def test_random_with_unhealthy_proxies(self):
        """Test random selection filters unhealthy proxies."""
        strategy = RandomStrategy()
        proxies = [
            ProxyConfig("proxy1.com", 8080),
            ProxyConfig("proxy2.com", 8080),
            ProxyConfig("proxy3.com", 8080)
        ]
        health_scores = {
            "proxy1.com:8080": 0.1,   # Unhealthy
            "proxy2.com:8080": 0.8,   # Healthy
            "proxy3.com:8080": 0.9    # Healthy
        }
        stats = {}
        
        # Should only select from healthy proxies
        for _ in range(10):  # Test multiple times due to randomness
            selected = strategy.select_proxy(proxies, health_scores, stats)
            assert selected in [proxies[1], proxies[2]]  # Only healthy ones
    
    def test_random_empty_list(self):
        """Test random with empty proxy list."""
        strategy = RandomStrategy()
        result = strategy.select_proxy([], {}, {})
        assert result is None


class TestFastestStrategy:
    """Test fastest strategy."""
    
    def test_fastest_selection(self):
        """Test fastest proxy selection."""
        strategy = FastestStrategy()
        proxies = [
            ProxyConfig("proxy1.com", 8080),
            ProxyConfig("proxy2.com", 8080),
            ProxyConfig("proxy3.com", 8080)
        ]
        health_scores = {p.id: 1.0 for p in proxies}
        stats = {
            "proxy1.com:8080": {"response_times": deque([2.0, 2.1, 1.9])},
            "proxy2.com:8080": {"response_times": deque([1.0, 1.1, 0.9])},  # Fastest
            "proxy3.com:8080": {"response_times": deque([3.0, 3.1, 2.9])}
        }
        
        selected = strategy.select_proxy(proxies, health_scores, stats)
        assert selected == proxies[1]  # proxy2 is fastest
    
    def test_fastest_with_no_stats(self):
        """Test fastest selection with no response time stats."""
        strategy = FastestStrategy()
        proxies = [ProxyConfig("proxy1.com", 8080)]
        health_scores = {"proxy1.com:8080": 1.0}
        stats = {}
        
        selected = strategy.select_proxy(proxies, health_scores, stats)
        assert selected == proxies[0]  # Should return available proxy
    
    def test_fastest_empty_list(self):
        """Test fastest with empty proxy list."""
        strategy = FastestStrategy()
        result = strategy.select_proxy([], {}, {})
        assert result is None


class TestSmartStrategy:
    """Test smart strategy."""
    
    def test_smart_selection(self):
        """Test smart proxy selection."""
        strategy = SmartStrategy()
        proxies = [
            ProxyConfig("proxy1.com", 8080),
            ProxyConfig("proxy2.com", 8080),
            ProxyConfig("proxy3.com", 8080)
        ]
        health_scores = {
            "proxy1.com:8080": 0.5,   # Medium health
            "proxy2.com:8080": 0.9,   # High health
            "proxy3.com:8080": 0.3    # Low health
        }
        stats = {
            "proxy1.com:8080": {
                "total_requests": 100,
                "successful_requests": 80,
                "response_times": deque([2.0, 2.1, 1.9]),
                "recent_successes": deque([1, 1, 0, 1, 1])
            },
            "proxy2.com:8080": {
                "total_requests": 100,
                "successful_requests": 95,
                "response_times": deque([1.0, 1.1, 0.9]),
                "recent_successes": deque([1, 1, 1, 1, 1])
            },
            "proxy3.com:8080": {
                "total_requests": 100,
                "successful_requests": 60,
                "response_times": deque([3.0, 3.1, 2.9]),
                "recent_successes": deque([0, 1, 0, 0, 1])
            }
        }
        
        selected = strategy.select_proxy(proxies, health_scores, stats)
        # proxy2 should win: high health + high success rate + fast response
        assert selected == proxies[1]
    
    def test_smart_with_minimal_stats(self):
        """Test smart selection with minimal statistics."""
        strategy = SmartStrategy()
        proxies = [ProxyConfig("proxy1.com", 8080)]
        health_scores = {"proxy1.com:8080": 0.8}
        stats = {}
        
        selected = strategy.select_proxy(proxies, health_scores, stats)
        assert selected == proxies[0]
    
    def test_smart_empty_list(self):
        """Test smart with empty proxy list."""
        strategy = SmartStrategy()
        result = strategy.select_proxy([], {}, {})
        assert result is None


class TestStrategyFactory:
    """Test strategy factory function."""
    
    def test_create_round_robin(self):
        """Test creating round-robin strategy."""
        strategy = create_strategy("round_robin")
        assert isinstance(strategy, RoundRobinStrategy)
    
    def test_create_random(self):
        """Test creating random strategy."""
        strategy = create_strategy("random")
        assert isinstance(strategy, RandomStrategy)
    
    def test_create_fastest(self):
        """Test creating fastest strategy."""
        strategy = create_strategy("fastest")
        assert isinstance(strategy, FastestStrategy)
    
    def test_create_smart(self):
        """Test creating smart strategy."""
        strategy = create_strategy("smart")
        assert isinstance(strategy, SmartStrategy)
    
    def test_create_invalid_strategy(self):
        """Test creating invalid strategy raises error."""
        with pytest.raises(ValueError, match="Unknown strategy"):
            create_strategy("invalid_strategy")
    
    def test_case_insensitive(self):
        """Test strategy creation is case insensitive."""
        strategy = create_strategy("SMART")
        assert isinstance(strategy, SmartStrategy)
        
        strategy = create_strategy("Round_Robin")
        assert isinstance(strategy, RoundRobinStrategy)
