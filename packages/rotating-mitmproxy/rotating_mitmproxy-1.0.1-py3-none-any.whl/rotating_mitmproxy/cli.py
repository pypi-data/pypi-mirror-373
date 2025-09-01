"""Command line interface for rotating mitmproxy."""

import sys
import time
import logging
import signal
from pathlib import Path
from typing import Optional

import click
from mitmproxy.tools.main import mitmdump
from mitmproxy import options

from .config import Config
from .thread_safe_rotator import ThreadSafeProxyRotator as ProxyRotator
from .server import StatsServer
from .monitoring import MonitoringAddon, create_monitoring_addon
# Removed parallel_server - single process handles 100+ concurrent requests perfectly


class VerboseLoggingAddon:
    """Addon for verbose logging based on user preference."""

    def __init__(self, verbose_level: str, rotator=None):
        self.verbose_level = verbose_level
        self.rotator = rotator
        self.request_count = 0
        self.last_stats_time = time.time()
        self.stats_interval = 30  # Show stats every 30 seconds

        self.logger = logging.getLogger("rotating_mitmproxy.verbose")

        # Configure logger based on verbose level
        if verbose_level == 'quiet':
            self.logger.setLevel(logging.WARNING)
        elif verbose_level == 'stats':
            self.logger.setLevel(logging.INFO)
        elif verbose_level == 'requests':
            self.logger.setLevel(logging.INFO)
        elif verbose_level == 'debug':
            self.logger.setLevel(logging.DEBUG)

    def request(self, flow) -> None:
        """Handle request logging."""
        self.request_count += 1

        if self.verbose_level == 'requests':
            proxy_id = getattr(flow, 'proxy_id', 'unknown')
            self.logger.info(f"→ {flow.request.method} {flow.request.pretty_url} via {proxy_id}")

        elif self.verbose_level == 'debug':
            proxy_id = getattr(flow, 'proxy_id', 'unknown')
            self.logger.debug(f"→ REQUEST #{self.request_count}: {flow.request.method} {flow.request.pretty_url}")
            self.logger.debug(f"  Proxy: {proxy_id}")
            self.logger.debug(f"  Headers: {dict(flow.request.headers)}")

    def response(self, flow) -> None:
        """Handle response logging."""
        if self.verbose_level == 'requests':
            status = flow.response.status_code if flow.response else "ERROR"
            response_time = getattr(flow, 'response_time', 0)
            self.logger.info(f"← {status} {flow.request.pretty_url} ({response_time:.2f}s)")

        elif self.verbose_level == 'debug':
            if flow.response:
                self.logger.debug(f"← RESPONSE: {flow.response.status_code} {flow.request.pretty_url}")
                self.logger.debug(f"  Size: {len(flow.response.content)} bytes")
                self.logger.debug(f"  Headers: {dict(flow.response.headers)}")
            else:
                self.logger.debug(f"← ERROR: No response for {flow.request.pretty_url}")

        # Show periodic stats for 'stats' level
        if self.verbose_level == 'stats':
            current_time = time.time()
            if current_time - self.last_stats_time >= self.stats_interval:
                self._show_stats()
                self.last_stats_time = current_time

    def error(self, flow) -> None:
        """Handle error logging."""
        if self.verbose_level in ['requests', 'debug']:
            self.logger.warning(f"✗ ERROR: {flow.request.pretty_url}")

    def _show_stats(self) -> None:
        """Show periodic statistics."""
        if not self.rotator:
            return

        try:
            stats = self.rotator.get_statistics()
            healthy_proxies = sum(1 for p in stats['proxy_details'] if p['health_score'] > 0.2)

            self.logger.info(f"📊 STATS: {stats['total_requests']} requests, "
                           f"{stats['success_rate']:.1%} success, "
                           f"{healthy_proxies}/{stats['total_proxies']} healthy proxies")

            # Show top 3 performing proxies
            top_proxies = sorted(stats['proxy_details'],
                               key=lambda x: x['health_score'], reverse=True)[:3]

            for i, proxy in enumerate(top_proxies, 1):
                self.logger.info(f"  #{i} {proxy['id']}: {proxy['health_score']:.2f} health, "
                               f"{proxy['success_rate']:.1%} success")

        except Exception as e:
            self.logger.debug(f"Error showing stats: {e}")





def setup_logging(level: str, log_file: Optional[Path] = None) -> None:
    """Setup logging configuration."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


@click.command()
@click.option(
    '--proxy-list', '-p',
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help='Path to proxy list file'
)
@click.option(
    '--port', '-P',
    type=int,
    default=8080,
    help='Listen port for proxy server'
)
@click.option(
    '--host', '-H',
    type=str,
    default='127.0.0.1',
    help='Listen host for proxy server'
)
@click.option(
    '--strategy', '-s',
    type=click.Choice(['round_robin', 'random', 'fastest', 'smart']),
    default='smart',
    help='Proxy selection strategy'
)
@click.option(
    '--min-health',
    type=float,
    default=0.2,
    help='Minimum health score for proxy selection'
)
@click.option(
    '--max-failures',
    type=int,
    default=5,
    help='Maximum failures before proxy timeout'
)
@click.option(
    '--failure-timeout',
    type=int,
    default=300,
    help='Timeout before retrying failed proxy (seconds)'
)
@click.option(
    '--stats-interval',
    type=int,
    default=60,
    help='Statistics logging interval (seconds, 0 to disable)'
)
@click.option(
    '--web-port',
    type=int,
    default=8081,
    help='Web interface port (0 to disable)'
)
@click.option(
    '--log-level',
    type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
    default='INFO',
    help='Logging level'
)
@click.option(
    '--verbose', '-v',
    type=click.Choice(['quiet', 'stats', 'requests', 'debug']),
    default='stats',
    help='Verbose output level: quiet (minimal), stats (periodic stats), requests (each request), debug (everything)'
)
@click.option(
    '--log-file',
    type=click.Path(path_type=Path),
    help='Log file path (optional)'
)
@click.option(
    '--config-file',
    type=click.Path(exists=True, path_type=Path),
    help='Configuration file path (optional)'
)
@click.option(
    '--enable-monitoring',
    is_flag=True,
    default=False,
    help='Enable detailed monitoring and logging'
)
@click.option(
    '--monitoring-log',
    type=click.Path(path_type=Path),
    help='Detailed monitoring log file (JSON format)'
)
@click.option(
    '--ignore-hosts',
    multiple=True,
    help='Regex patterns for hosts to ignore (pass through without interception). Can be used multiple times.'
)
@click.version_option()
def main(
    proxy_list: Path,
    port: int,
    host: str,
    strategy: str,
    min_health: float,
    max_failures: int,
    failure_timeout: int,
    stats_interval: int,
    web_port: int,
    log_level: str,
    log_file: Optional[Path],
    config_file: Optional[Path],
    enable_monitoring: bool,
    monitoring_log: Optional[Path],
    verbose: str,
    ignore_hosts: tuple
) -> None:
    """Rotating mitmproxy - Smart proxy rotator with health monitoring."""
    
    # Setup logging
    setup_logging(log_level, log_file)
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        if config_file:
            config = Config.from_file(config_file)
        else:
            config = Config()
            config.proxy_list_file = proxy_list
            config.load_proxy_list()
        
        # Override with CLI arguments
        config.listen_port = port
        config.listen_host = host
        config.strategy = strategy
        config.min_health_score = min_health
        config.max_failures = max_failures
        config.failure_timeout = failure_timeout
        config.stats_interval = stats_interval
        config.web_port = web_port
        config.log_level = log_level
        config.log_file = log_file
        
        # Validate configuration
        config.validate()
        
        logger.info(f"Starting rotating mitmproxy with {config.proxy_count} proxies")
        logger.info(f"Strategy: {config.strategy}")
        logger.info(f"Listen: {config.listen_host}:{config.listen_port}")
        
        # Create proxy rotator
        rotator = ProxyRotator(config)

        # Create verbose logging addon
        verbose_addon = VerboseLoggingAddon(verbose, rotator)
        logger.info(f"Verbose level: {verbose}")

        # Create monitoring addon if enabled
        monitoring_addon = None
        if enable_monitoring:
            monitoring_addon = create_monitoring_addon(
                rotator=rotator,
                log_file=monitoring_log,
                detailed_logging=True
            )
            logger.info("Detailed monitoring enabled")

        # Start stats server if enabled
        stats_server = None
        if config.web_port > 0:
            stats_server = StatsServer(rotator, config.web_port)
            stats_server.start()
            logger.info(f"Stats server started on port {config.web_port}")
        
        # Setup signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            logger.info("Received shutdown signal, stopping...")
            if stats_server:
                stats_server.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Configure mitmproxy options
        opts = options.Options(
            listen_host=config.listen_host,
            listen_port=config.listen_port,
            confdir='~/.mitmproxy'
        )

        # Add default Google services pass-through to reduce SSL noise
        default_ignore_hosts = [
            r'^(.+\.)?googleapis\.com:443$',      # Google APIs (fonts, autofill, etc.)
            r'^(.+\.)?accounts\.google\.com:443$', # Google account services
            r'^(.+\.)?gstatic\.com:443$',         # Google static content
        ]

        # Combine default ignore hosts with user-specified ones
        all_ignore_hosts = default_ignore_hosts.copy()
        if ignore_hosts:
            all_ignore_hosts.extend(ignore_hosts)
            logger.info(f"User-specified ignore hosts: {list(ignore_hosts)}")

        # Apply all ignore hosts
        if all_ignore_hosts:
            opts.ignore_hosts = all_ignore_hosts
            logger.info(f"Total ignore hosts applied: {len(all_ignore_hosts)}")
            logger.info(f"Default Google services pass-through: {default_ignore_hosts}")
            if ignore_hosts:
                logger.info(f"Additional user ignore hosts: {list(ignore_hosts)}")
        else:
            logger.info("No ignore_hosts patterns specified")
        
        # Prepare addons list
        addons = [rotator, verbose_addon]
        if monitoring_addon:
            addons.append(monitoring_addon)

        # Start mitmproxy with our addons
        logger.info("Starting mitmproxy server...")

        # Use the proper way to start mitmproxy with addons
        import asyncio
        from mitmproxy.tools.dump import DumpMaster

        async def run_proxy():
            master = DumpMaster(opts)
            for addon in addons:
                master.addons.add(addon)
            await master.run()

        # Run the async proxy
        asyncio.run(run_proxy())
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error starting rotating mitmproxy: {e}")
        sys.exit(1)


@click.command()
@click.option(
    '--proxy-list', '-p',
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help='Path to proxy list file'
)
def validate_proxies(proxy_list: Path) -> None:
    """Validate proxy list file format."""
    try:
        config = Config()
        config.proxy_list_file = proxy_list
        config.load_proxy_list()
        
        click.echo(f"✅ Loaded {config.proxy_count} proxies from {proxy_list}")
        
        for i, proxy in enumerate(config.proxy_list, 1):
            click.echo(f"  {i:2d}. {proxy.to_url()}")
        
        config.validate()
        click.echo("✅ Configuration is valid")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@click.command()
@click.option(
    '--url',
    default='http://localhost:8080',
    help='Rotating proxy server URL'
)
def stats(url: str) -> None:
    """Show proxy statistics from running server."""
    import requests
    
    try:
        response = requests.get(f"{url}/_stats", timeout=5)
        response.raise_for_status()
        
        stats_data = response.json()
        
        click.echo("=== Proxy Statistics ===")
        click.echo(f"Uptime: {stats_data['uptime']:.0f}s")
        click.echo(f"Total Requests: {stats_data['total_requests']}")
        click.echo(f"Success Rate: {stats_data['success_rate']:.2%}")
        click.echo(f"Healthy Proxies: {stats_data['healthy_proxies']}/{stats_data['total_proxies']}")
        click.echo(f"Strategy: {stats_data['strategy']}")
        
        click.echo("\n=== Top Proxies ===")
        top_proxies = sorted(
            stats_data['proxy_details'],
            key=lambda x: x['health_score'],
            reverse=True
        )[:10]
        
        for proxy in top_proxies:
            status = "🟢" if proxy['health_score'] > 0.5 else "🟡" if proxy['health_score'] > 0.2 else "🔴"
            click.echo(
                f"{status} {proxy['id']}: "
                f"Health={proxy['health_score']:.2f}, "
                f"Requests={proxy['total_requests']}, "
                f"Success={proxy['success_rate']:.2%}"
            )
        
    except requests.RequestException as e:
        click.echo(f"❌ Error connecting to server: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@click.command()
@click.option(
    '--proxy-list', '-p',
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help='Path to proxy list file'
)
@click.option(
    '--port', '-P',
    type=int,
    default=8080,
    help='Listen port for proxy server'
)
@click.option(
    '--web-port',
    type=int,
    default=8081,
    help='Web interface port'
)
@click.option(
    '--strategy', '-s',
    type=click.Choice(['round_robin', 'random', 'fastest', 'smart']),
    default='smart',
    help='Proxy selection strategy'
)
@click.option(
    '--enable-monitoring',
    is_flag=True,
    default=True,
    help='Enable detailed monitoring (default: enabled for web mode)'
)
@click.option(
    '--monitoring-log',
    type=click.Path(path_type=Path),
    help='Detailed monitoring log file (JSON format)'
)
def web(
    proxy_list: Path,
    port: int,
    web_port: int,
    strategy: str,
    enable_monitoring: bool,
    monitoring_log: Optional[Path]
) -> None:
    """Start rotating mitmproxy with web interface for monitoring."""

    from mitmproxy.tools.main import mitmweb
    from mitmproxy import options

    # Setup logging
    setup_logging("INFO")
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        config = Config()
        config.proxy_list_file = proxy_list
        config.load_proxy_list()
        config.listen_port = port
        config.strategy = strategy
        config.web_port = web_port
        config.validate()

        logger.info(f"Starting rotating mitmproxy web interface")
        logger.info(f"Proxy server: http://localhost:{port}")
        logger.info(f"Web interface: http://localhost:{web_port}")
        logger.info(f"Strategy: {strategy}")
        logger.info(f"Proxies: {config.proxy_count}")

        # Create rotator and monitoring
        rotator = ProxyRotator(config)

        monitoring_addon = create_monitoring_addon(
            rotator=rotator,
            log_file=monitoring_log,
            detailed_logging=enable_monitoring
        )

        # Configure mitmproxy options
        opts = options.Options(
            listen_host="127.0.0.1",
            listen_port=port,
            web_host="127.0.0.1",
            web_port=web_port,
            confdir='~/.mitmproxy'
        )

        # Start mitmproxy web interface with our addons
        logger.info("Starting mitmproxy web interface...")

        import asyncio
        from mitmproxy.tools.web.master import WebMaster

        async def run_web_proxy():
            master = WebMaster(opts)
            master.addons.add(rotator)
            master.addons.add(monitoring_addon)
            await master.run()

        # Run the async web proxy
        asyncio.run(run_web_proxy())

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error starting rotating mitmproxy web interface: {e}")
        sys.exit(1)


# Create CLI group
@click.group()
def cli():
    """Rotating mitmproxy - Smart proxy rotator with health monitoring."""
    pass


cli.add_command(main, name='start')
cli.add_command(web, name='web')
cli.add_command(validate_proxies, name='validate')
cli.add_command(stats, name='stats')


# Parallel server removed - single process handles 100+ concurrent requests perfectly


if __name__ == '__main__':
    main()
