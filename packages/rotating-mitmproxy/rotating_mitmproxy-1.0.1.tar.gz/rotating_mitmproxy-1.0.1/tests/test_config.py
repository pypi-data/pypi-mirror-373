"""Tests for configuration module."""

import pytest
from pathlib import Path
import tempfile

from rotating_mitmproxy.config import Config, ProxyConfig


class TestProxyConfig:
    """Test ProxyConfig class."""
    
    def test_from_string_simple(self):
        """Test parsing simple host:port format."""
        proxy = ProxyConfig.from_string("example.com:8080")
        assert proxy.host == "example.com"
        assert proxy.port == 8080
        assert proxy.username is None
        assert proxy.password is None
        assert proxy.protocol == "http"
    
    def test_from_string_with_auth(self):
        """Test parsing with authentication."""
        proxy = ProxyConfig.from_string("user:pass@example.com:8080")
        assert proxy.host == "example.com"
        assert proxy.port == 8080
        assert proxy.username == "user"
        assert proxy.password == "pass"
        assert proxy.protocol == "http"
    
    def test_from_string_with_protocol(self):
        """Test parsing with protocol."""
        proxy = ProxyConfig.from_string("socks5://example.com:1080")
        assert proxy.host == "example.com"
        assert proxy.port == 1080
        assert proxy.username is None
        assert proxy.password is None
        assert proxy.protocol == "socks5"
    
    def test_from_string_full_format(self):
        """Test parsing full format with protocol and auth."""
        proxy = ProxyConfig.from_string("https://user:pass@example.com:8080")
        assert proxy.host == "example.com"
        assert proxy.port == 8080
        assert proxy.username == "user"
        assert proxy.password == "pass"
        assert proxy.protocol == "https"
    
    def test_to_tuple(self):
        """Test conversion to tuple format."""
        proxy = ProxyConfig("example.com", 8080)
        assert proxy.to_tuple() == ("example.com", 8080)
    
    def test_to_url(self):
        """Test conversion to URL format."""
        proxy = ProxyConfig("example.com", 8080, "user", "pass", "http")
        assert proxy.to_url() == "http://user:pass@example.com:8080"
        
        proxy_no_auth = ProxyConfig("example.com", 8080)
        assert proxy_no_auth.to_url() == "http://example.com:8080"
    
    def test_id_property(self):
        """Test proxy ID generation."""
        proxy = ProxyConfig("example.com", 8080)
        assert proxy.id == "example.com:8080"


class TestConfig:
    """Test Config class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        assert config.listen_port == 8080
        assert config.listen_host == "127.0.0.1"
        assert config.strategy == "smart"
        assert config.min_health_score == 0.2
        assert config.max_failures == 5
        assert config.failure_timeout == 300
    
    def test_add_proxy_string(self):
        """Test adding proxy from string."""
        config = Config()
        config.add_proxy("example.com:8080")
        
        assert len(config.proxy_list) == 1
        assert config.proxy_list[0].host == "example.com"
        assert config.proxy_list[0].port == 8080
    
    def test_add_proxy_object(self):
        """Test adding proxy object."""
        config = Config()
        proxy = ProxyConfig("example.com", 8080)
        config.add_proxy(proxy)
        
        assert len(config.proxy_list) == 1
        assert config.proxy_list[0] == proxy
    
    def test_load_proxy_list_from_file(self):
        """Test loading proxy list from file."""
        proxy_content = """
        # Test proxy list
        proxy1.com:8080
        user:pass@proxy2.com:8080
        
        # Comment line
        http://proxy3.com:8080
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(proxy_content)
            f.flush()
            
            config = Config()
            config.proxy_list_file = Path(f.name)
            config.load_proxy_list()
        
        assert len(config.proxy_list) == 3
        assert config.proxy_list[0].host == "proxy1.com"
        assert config.proxy_list[1].username == "user"
        assert config.proxy_list[2].protocol == "http"
    
    def test_validate_valid_config(self):
        """Test validation of valid configuration."""
        config = Config()
        config.add_proxy("example.com:8080")
        
        # Should not raise exception
        config.validate()
    
    def test_validate_no_proxies(self):
        """Test validation fails with no proxies."""
        config = Config()
        
        with pytest.raises(ValueError, match="No proxies configured"):
            config.validate()
    
    def test_validate_invalid_strategy(self):
        """Test validation fails with invalid strategy."""
        config = Config()
        config.add_proxy("example.com:8080")
        config.strategy = "invalid_strategy"
        
        with pytest.raises(ValueError, match="Invalid strategy"):
            config.validate()
    
    def test_validate_invalid_health_score(self):
        """Test validation fails with invalid health score."""
        config = Config()
        config.add_proxy("example.com:8080")
        config.min_health_score = 1.5
        
        with pytest.raises(ValueError, match="min_health_score must be between 0 and 1"):
            config.validate()
    
    def test_proxy_count(self):
        """Test proxy count property."""
        config = Config()
        assert config.proxy_count == 0
        
        config.add_proxy("proxy1.com:8080")
        config.add_proxy("proxy2.com:8080")
        assert config.proxy_count == 2
