"""Statistics server for rotating mitmproxy."""

import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .thread_safe_rotator import ThreadSafeProxyRotator as ProxyRotator


class StatsHandler(BaseHTTPRequestHandler):
    """HTTP handler for statistics endpoints."""
    
    def __init__(self, rotator: 'ProxyRotator', *args, **kwargs):
        self.rotator = rotator
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/_stats':
            self._handle_stats()
        elif self.path == '/_health':
            self._handle_health()
        elif self.path == '/':
            self._handle_dashboard()
        else:
            self._handle_404()
    
    def _handle_stats(self):
        """Return JSON statistics."""
        try:
            stats = self.rotator.get_statistics()
            self._send_json_response(stats)
        except Exception as e:
            self._send_error_response(500, f"Error getting statistics: {e}")
    
    def _handle_health(self):
        """Return health check response."""
        try:
            stats = self.rotator.get_statistics()
            health_data = {
                'status': 'healthy' if stats['healthy_proxies'] > 0 else 'unhealthy',
                'healthy_proxies': stats['healthy_proxies'],
                'total_proxies': stats['total_proxies'],
                'success_rate': stats['success_rate']
            }
            self._send_json_response(health_data)
        except Exception as e:
            self._send_error_response(500, f"Error getting health: {e}")
    
    def _handle_dashboard(self):
        """Return HTML dashboard."""
        html = self._generate_dashboard_html()
        self._send_html_response(html)
    
    def _handle_404(self):
        """Handle 404 errors."""
        self._send_error_response(404, "Not Found")
    
    def _send_json_response(self, data):
        """Send JSON response."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def _send_html_response(self, html):
        """Send HTML response."""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def _send_error_response(self, code, message):
        """Send error response."""
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        error_data = {'error': message}
        self.wfile.write(json.dumps(error_data).encode())
    
    def _generate_dashboard_html(self):
        """Generate HTML dashboard."""
        try:
            stats = self.rotator.get_statistics()
        except Exception as e:
            return f"<html><body><h1>Error</h1><p>{e}</p></body></html>"
        
        # Sort proxies by health score
        proxies = sorted(
            stats['proxy_details'],
            key=lambda x: x['health_score'],
            reverse=True
        )
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Rotating mitmproxy Dashboard</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .stats {{ display: flex; gap: 20px; margin-bottom: 20px; }}
                .stat-box {{ background: #e8f4fd; padding: 15px; border-radius: 5px; flex: 1; }}
                .stat-value {{ font-size: 24px; font-weight: bold; color: #2c5aa0; }}
                .stat-label {{ color: #666; font-size: 14px; }}
                .proxy-table {{ width: 100%; border-collapse: collapse; }}
                .proxy-table th, .proxy-table td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                .proxy-table th {{ background: #f5f5f5; }}
                .health-good {{ color: #28a745; }}
                .health-warning {{ color: #ffc107; }}
                .health-bad {{ color: #dc3545; }}
                .status-indicator {{ font-size: 18px; }}
                .refresh-btn {{ background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }}
                .refresh-btn:hover {{ background: #0056b3; }}
            </style>
            <script>
                function refreshData() {{
                    location.reload();
                }}
                
                // Auto-refresh every 30 seconds
                setInterval(refreshData, 30000);
            </script>
        </head>
        <body>
            <div class="header">
                <h1>🔄 Rotating mitmproxy Dashboard</h1>
                <p>Strategy: <strong>{stats['strategy']}</strong> | 
                   Uptime: <strong>{stats['uptime']:.0f}s</strong> |
                   <button class="refresh-btn" onclick="refreshData()">🔄 Refresh</button>
                </p>
            </div>
            
            <div class="stats">
                <div class="stat-box">
                    <div class="stat-value">{stats['total_requests']}</div>
                    <div class="stat-label">Total Requests</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{stats['success_rate']:.1%}</div>
                    <div class="stat-label">Success Rate</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{stats['healthy_proxies']}/{stats['total_proxies']}</div>
                    <div class="stat-label">Healthy Proxies</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{stats['failed_proxies']}</div>
                    <div class="stat-label">Failed Proxies</div>
                </div>
            </div>
            
            <h2>📊 Proxy Details</h2>
            <table class="proxy-table">
                <thead>
                    <tr>
                        <th>Status</th>
                        <th>Proxy</th>
                        <th>Health</th>
                        <th>Requests</th>
                        <th>Success Rate</th>
                        <th>Avg Response</th>
                        <th>Recent Success</th>
                        <th>Failures</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for proxy in proxies:
            # Determine status indicator
            if proxy['in_timeout']:
                status = "⏸️"
                health_class = "health-bad"
            elif proxy['health_score'] > 0.7:
                status = "🟢"
                health_class = "health-good"
            elif proxy['health_score'] > 0.3:
                status = "🟡"
                health_class = "health-warning"
            else:
                status = "🔴"
                health_class = "health-bad"
            
            html += f"""
                    <tr>
                        <td class="status-indicator">{status}</td>
                        <td>{proxy['id']}</td>
                        <td class="{health_class}">{proxy['health_score']:.2f}</td>
                        <td>{proxy['total_requests']}</td>
                        <td>{proxy['success_rate']:.1%}</td>
                        <td>{proxy['avg_response_time']:.2f}s</td>
                        <td>{proxy['recent_success_rate']:.1%}</td>
                        <td>{proxy['failure_count']}</td>
                    </tr>
            """
        
        html += """
                </tbody>
            </table>
            
            <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px;">
                <h3>📖 Legend</h3>
                <p>
                    🟢 Healthy (Health > 0.7) | 
                    🟡 Warning (Health 0.3-0.7) | 
                    🔴 Unhealthy (Health < 0.3) | 
                    ⏸️ In Timeout
                </p>
                <p><strong>API Endpoints:</strong></p>
                <ul>
                    <li><code>GET /_stats</code> - JSON statistics</li>
                    <li><code>GET /_health</code> - Health check</li>
                </ul>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def log_message(self, format, *args):
        """Override to suppress default logging."""
        pass


class StatsServer:
    """HTTP server for statistics and monitoring."""
    
    def __init__(self, rotator: 'ProxyRotator', port: int):
        self.rotator = rotator
        self.port = port
        self.server = None
        self.thread = None
    
    def start(self):
        """Start the stats server."""
        def handler(*args, **kwargs):
            return StatsHandler(self.rotator, *args, **kwargs)
        
        self.server = HTTPServer(('127.0.0.1', self.port), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the stats server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        if self.thread:
            self.thread.join(timeout=5)
