"""Configuration management for rotating mitmproxy."""

import os
from dataclasses import dataclass, field
from typing import List, Optional, Union
from pathlib import Path


@dataclass
class ProxyConfig:
    """Configuration for a single proxy."""
    
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: str = "http"
    
    @classmethod
    def from_string(cls, proxy_string: str) -> "ProxyConfig":
        """Parse proxy from string format.
        
        Supports formats:
        - host:port
        - user:pass@host:port
        - protocol://host:port
        - protocol://user:pass@host:port
        """
        original = proxy_string.strip()
        
        # Remove protocol if present
        protocol = "http"
        if "://" in original:
            protocol, original = original.split("://", 1)
        
        # Extract auth if present
        username = password = None
        if "@" in original:
            auth, original = original.rsplit("@", 1)
            if ":" in auth:
                username, password = auth.split(":", 1)
            else:
                username = auth
        
        # Extract host and port
        if ":" in original:
            host, port_str = original.rsplit(":", 1)
            port = int(port_str)
        else:
            host = original
            port = 8080  # Default port
        
        return cls(
            host=host,
            port=port,
            username=username,
            password=password,
            protocol=protocol
        )
    
    def to_tuple(self) -> tuple:
        """Convert to tuple format for mitmproxy."""
        return (self.host, self.port)
    
    def to_url(self) -> str:
        """Convert to URL format."""
        auth = ""
        if self.username:
            auth = f"{self.username}"
            if self.password:
                auth += f":{self.password}"
            auth += "@"
        
        return f"{self.protocol}://{auth}{self.host}:{self.port}"
    
    @property
    def id(self) -> str:
        """Unique identifier for this proxy."""
        return f"{self.host}:{self.port}"


@dataclass
class Config:
    """Main configuration for rotating mitmproxy."""
    
    # Proxy settings
    proxy_list: List[ProxyConfig] = field(default_factory=list)
    proxy_list_file: Optional[Path] = None
    
    # Server settings
    listen_port: int = 8080
    listen_host: str = "127.0.0.1"
    web_port: int = 8081
    
    # Rotation settings
    strategy: str = "smart"  # round_robin, random, fastest, smart
    
    # Health monitoring
    min_health_score: float = 0.2
    max_failures: int = 5
    failure_timeout: int = 300  # seconds
    health_check_interval: int = 60  # seconds
    
    # Statistics
    stats_interval: int = 60  # seconds
    enable_stats_endpoint: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[Path] = None
    
    # Performance
    connection_timeout: int = 10
    read_timeout: int = 30
    
    @classmethod
    def from_file(cls, config_file: Union[str, Path]) -> "Config":
        """Load configuration from file."""
        # This could be extended to support YAML/JSON config files
        # For now, we'll focus on proxy list files
        config = cls()
        config.proxy_list_file = Path(config_file)
        config.load_proxy_list()
        return config
    
    def load_proxy_list(self) -> None:
        """Load proxy list from file."""
        if not self.proxy_list_file or not self.proxy_list_file.exists():
            return
        
        self.proxy_list = []
        with open(self.proxy_list_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        proxy = ProxyConfig.from_string(line)
                        self.proxy_list.append(proxy)
                    except Exception as e:
                        print(f"Warning: Failed to parse proxy '{line}': {e}")
    
    def add_proxy(self, proxy: Union[str, ProxyConfig]) -> None:
        """Add a proxy to the list."""
        if isinstance(proxy, str):
            proxy = ProxyConfig.from_string(proxy)
        self.proxy_list.append(proxy)
    
    def validate(self) -> None:
        """Validate configuration."""
        if not self.proxy_list:
            raise ValueError("No proxies configured")
        
        if self.strategy not in ["round_robin", "random", "fastest", "smart"]:
            raise ValueError(f"Invalid strategy: {self.strategy}")
        
        if not 0 <= self.min_health_score <= 1:
            raise ValueError("min_health_score must be between 0 and 1")
        
        if self.max_failures < 1:
            raise ValueError("max_failures must be at least 1")
        
        if self.failure_timeout < 0:
            raise ValueError("failure_timeout must be non-negative")
    
    @property
    def proxy_count(self) -> int:
        """Number of configured proxies."""
        return len(self.proxy_list)
