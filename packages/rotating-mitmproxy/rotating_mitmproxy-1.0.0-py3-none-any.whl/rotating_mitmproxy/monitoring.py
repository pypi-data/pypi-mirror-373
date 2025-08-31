"""Monitoring and observability features for rotating mitmproxy.

This module exposes mitmproxy's built-in monitoring capabilities and adds
custom monitoring features for proxy rotation.
"""

import time
import json
import logging
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from pathlib import Path

from mitmproxy import http, ctx
from mitmproxy.tools.main import mitmweb


@dataclass
class RequestMetrics:
    """Metrics for a single request."""
    
    timestamp: float
    url: str
    method: str
    proxy_id: str
    response_time: float
    status_code: Optional[int]
    response_size: int
    success: bool
    error_message: Optional[str] = None


@dataclass
class ProxyMetrics:
    """Aggregated metrics for a proxy."""
    
    proxy_id: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    total_response_size: int = 0
    last_used: float = 0.0
    first_used: float = 0.0
    health_score: float = 1.0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    @property
    def avg_response_time(self) -> float:
        """Calculate average response time."""
        if self.successful_requests == 0:
            return 0.0
        return self.total_response_time / self.successful_requests
    
    @property
    def avg_response_size(self) -> float:
        """Calculate average response size."""
        if self.successful_requests == 0:
            return 0.0
        return self.total_response_size / self.successful_requests


class MonitoringAddon:
    """Mitmproxy addon for advanced monitoring and logging."""
    
    def __init__(self, rotator=None, log_file: Optional[Path] = None, 
                 detailed_logging: bool = False):
        """Initialize monitoring addon.
        
        Args:
            rotator: ProxyRotator instance to monitor
            log_file: Optional file to log detailed request data
            detailed_logging: Whether to log detailed request/response data
        """
        self.rotator = rotator
        self.log_file = log_file
        self.detailed_logging = detailed_logging
        
        # Metrics storage
        self.request_history: deque = deque(maxlen=1000)  # Last 1000 requests
        self.proxy_metrics: Dict[str, ProxyMetrics] = {}
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.status_code_counts: Dict[int, int] = defaultdict(int)
        
        # Performance tracking
        self.start_time = time.time()
        self.total_bytes_transferred = 0
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        if log_file:
            handler = logging.FileHandler(log_file)
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(handler)
    
    def request(self, flow: http.HTTPFlow) -> None:
        """Handle request - start timing and logging."""
        flow.monitoring_start_time = time.time()
        
        if self.detailed_logging:
            self.logger.info(f"Request: {flow.request.method} {flow.request.pretty_url}")
    
    def response(self, flow: http.HTTPFlow) -> None:
        """Handle response - collect metrics and log."""
        if not hasattr(flow, 'monitoring_start_time'):
            return
        
        # Calculate metrics
        response_time = time.time() - flow.monitoring_start_time
        proxy_id = getattr(flow, 'proxy_id', 'unknown')
        status_code = flow.response.status_code if flow.response else None
        response_size = len(flow.response.content) if flow.response else 0
        success = flow.response is not None and flow.response.status_code < 400
        
        # Create request metrics
        metrics = RequestMetrics(
            timestamp=time.time(),
            url=flow.request.pretty_url,
            method=flow.request.method,
            proxy_id=proxy_id,
            response_time=response_time,
            status_code=status_code,
            response_size=response_size,
            success=success,
            error_message=None if success else f"Status: {status_code}"
        )
        
        # Store in history
        self.request_history.append(metrics)
        
        # Update proxy metrics
        if proxy_id not in self.proxy_metrics:
            self.proxy_metrics[proxy_id] = ProxyMetrics(proxy_id=proxy_id)
        proxy_metrics = self.proxy_metrics[proxy_id]
        proxy_metrics.total_requests += 1
        proxy_metrics.last_used = time.time()
        
        if proxy_metrics.first_used == 0:
            proxy_metrics.first_used = time.time()
        
        if success:
            proxy_metrics.successful_requests += 1
            proxy_metrics.total_response_time += response_time
            proxy_metrics.total_response_size += response_size
        else:
            proxy_metrics.failed_requests += 1
            self.error_counts[f"{status_code}"] += 1
        
        # Update global metrics
        if status_code:
            self.status_code_counts[status_code] += 1
        self.total_bytes_transferred += response_size
        
        # Sync with rotator health scores
        if self.rotator and proxy_id in self.rotator.health_scores:
            proxy_metrics.health_score = self.rotator.health_scores[proxy_id]
        
        # Detailed logging
        if self.detailed_logging:
            self.logger.info(
                f"Response: {flow.request.method} {flow.request.pretty_url} "
                f"-> {status_code} ({response_time:.2f}s, {response_size} bytes) "
                f"via {proxy_id}"
            )
        
        # Log to file if configured
        if self.log_file:
            self._log_request_to_file(metrics)
    
    def error(self, flow: http.HTTPFlow) -> None:
        """Handle connection errors."""
        if not hasattr(flow, 'monitoring_start_time'):
            return
        
        response_time = time.time() - flow.monitoring_start_time
        proxy_id = getattr(flow, 'proxy_id', 'unknown')
        
        # Create error metrics
        metrics = RequestMetrics(
            timestamp=time.time(),
            url=flow.request.pretty_url,
            method=flow.request.method,
            proxy_id=proxy_id,
            response_time=response_time,
            status_code=None,
            response_size=0,
            success=False,
            error_message="Connection error"
        )
        
        self.request_history.append(metrics)
        
        # Update proxy metrics
        if proxy_id not in self.proxy_metrics:
            self.proxy_metrics[proxy_id] = ProxyMetrics(proxy_id=proxy_id)
        proxy_metrics = self.proxy_metrics[proxy_id]
        proxy_metrics.total_requests += 1
        proxy_metrics.failed_requests += 1
        proxy_metrics.last_used = time.time()
        
        if proxy_metrics.first_used == 0:
            proxy_metrics.first_used = time.time()
        
        self.error_counts["connection_error"] += 1
        
        if self.detailed_logging:
            self.logger.error(f"Connection error: {flow.request.pretty_url} via {proxy_id}")
    
    def _log_request_to_file(self, metrics: RequestMetrics) -> None:
        """Log request metrics to file in JSON format."""
        try:
            with open(self.log_file, 'a') as f:
                json.dump(asdict(metrics), f)
                f.write('\n')
        except Exception as e:
            self.logger.error(f"Failed to log to file: {e}")
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get comprehensive monitoring statistics."""
        uptime = time.time() - self.start_time
        total_requests = len(self.request_history)
        successful_requests = sum(1 for r in self.request_history if r.success)
        
        return {
            'uptime': uptime,
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': total_requests - successful_requests,
            'success_rate': successful_requests / max(1, total_requests),
            'total_bytes_transferred': self.total_bytes_transferred,
            'requests_per_second': total_requests / max(1, uptime),
            'bytes_per_second': self.total_bytes_transferred / max(1, uptime),
            
            # Proxy metrics
            'proxy_metrics': {
                proxy_id: asdict(metrics) 
                for proxy_id, metrics in self.proxy_metrics.items()
            },
            
            # Error breakdown
            'error_counts': dict(self.error_counts),
            'status_code_counts': dict(self.status_code_counts),
            
            # Recent requests (last 10)
            'recent_requests': [
                asdict(req) for req in list(self.request_history)[-10:]
            ]
        }
    
    def get_proxy_performance_report(self) -> Dict[str, Any]:
        """Generate detailed proxy performance report."""
        report = {
            'timestamp': time.time(),
            'uptime': time.time() - self.start_time,
            'proxies': []
        }
        
        for proxy_id, metrics in self.proxy_metrics.items():
            proxy_report = {
                'proxy_id': proxy_id,
                'performance_score': self._calculate_performance_score(metrics),
                'metrics': asdict(metrics),
                'recent_requests': [
                    asdict(req) for req in self.request_history 
                    if req.proxy_id == proxy_id
                ][-5:],  # Last 5 requests for this proxy
                'recommendations': self._generate_recommendations(metrics)
            }
            report['proxies'].append(proxy_report)
        
        # Sort by performance score
        report['proxies'].sort(key=lambda x: x['performance_score'], reverse=True)
        
        return report
    
    def _calculate_performance_score(self, metrics: ProxyMetrics) -> float:
        """Calculate overall performance score for a proxy."""
        if metrics.total_requests == 0:
            return 0.0
        
        # Factors: success rate (40%), speed (30%), health (30%)
        success_score = metrics.success_rate
        
        # Speed score (inverse of response time, normalized)
        speed_score = 1.0 / (1.0 + metrics.avg_response_time) if metrics.avg_response_time > 0 else 0.5
        
        # Health score from rotator
        health_score = metrics.health_score
        
        return (success_score * 0.4 + speed_score * 0.3 + health_score * 0.3)
    
    def _generate_recommendations(self, metrics: ProxyMetrics) -> List[str]:
        """Generate recommendations for proxy optimization."""
        recommendations = []
        
        if metrics.success_rate < 0.8:
            recommendations.append("Low success rate - consider removing or investigating proxy")
        
        if metrics.avg_response_time > 5.0:
            recommendations.append("High response time - proxy may be overloaded or distant")
        
        if metrics.total_requests < 10:
            recommendations.append("Low usage - proxy may not be selected by strategy")
        
        if metrics.health_score < 0.5:
            recommendations.append("Low health score - proxy experiencing issues")
        
        if not recommendations:
            recommendations.append("Proxy performing well")
        
        return recommendations


class MitmproxyWebIntegration:
    """Integration with mitmproxy's web interface."""
    
    def __init__(self, rotator, monitoring_addon: MonitoringAddon):
        self.rotator = rotator
        self.monitoring = monitoring_addon
    
    def start_web_interface(self, port: int = 8081, host: str = "127.0.0.1"):
        """Start mitmproxy web interface with custom monitoring."""
        # This would integrate with mitmweb
        # For now, we'll document how to use it
        pass
    
    def get_web_dashboard_data(self) -> Dict[str, Any]:
        """Get data for web dashboard."""
        return {
            'proxy_stats': self.rotator.get_statistics() if self.rotator else {},
            'monitoring_stats': self.monitoring.get_monitoring_stats(),
            'performance_report': self.monitoring.get_proxy_performance_report()
        }


def create_monitoring_addon(rotator=None, **kwargs) -> MonitoringAddon:
    """Factory function to create monitoring addon."""
    return MonitoringAddon(rotator=rotator, **kwargs)
