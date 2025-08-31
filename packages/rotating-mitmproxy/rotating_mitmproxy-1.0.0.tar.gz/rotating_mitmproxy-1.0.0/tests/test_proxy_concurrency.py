#!/usr/bin/env python3
"""
Comprehensive proxy concurrency test for rotating-mitmproxy.

This test verifies:
1. True concurrency with multiple threads
2. Proxy rotation functionality 
3. IP verification against proxy list
4. Performance metrics
"""

import threading
import time
import requests
import json
import argparse
import sys
from pathlib import Path
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Set, Tuple


class ProxyTester:
    """Test proxy rotation and concurrency."""
    
    def __init__(self, proxy_url: str = "http://localhost:9090", proxy_list_file: str = "proxy_list.txt"):
        self.proxy_url = proxy_url
        self.proxy_list_file = proxy_list_file
        self.proxy_ips = self._load_proxy_ips()
        self.results = []
        self.lock = threading.Lock()
        
    def _load_proxy_ips(self) -> Set[str]:
        """Load proxy IPs from proxy list file."""
        proxy_ips = set()
        proxy_file = Path(self.proxy_list_file)
        
        if not proxy_file.exists():
            print(f"❌ Proxy list file not found: {self.proxy_list_file}")
            return proxy_ips
            
        try:
            with open(proxy_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Extract IP from various formats
                        if '@' in line:
                            # user:pass@ip:port
                            ip = line.split('@')[1].split(':')[0]
                        elif '://' in line:
                            # protocol://ip:port
                            ip = line.split('://')[1].split(':')[0]
                        else:
                            # ip:port
                            ip = line.split(':')[0]
                        proxy_ips.add(ip)
                        
            print(f"📋 Loaded {len(proxy_ips)} proxy IPs from {self.proxy_list_file}")
            return proxy_ips
            
        except Exception as e:
            print(f"❌ Error loading proxy list: {e}")
            return proxy_ips
    
    def make_request(self, request_id: int) -> Dict:
        """Make a single request through the proxy."""
        start_time = time.time()
        
        try:
            response = requests.get(
                'http://httpbin.org/ip',
                proxies={'http': self.proxy_url, 'https': self.proxy_url},
                timeout=15
            )
            
            duration = time.time() - start_time
            data = response.json()
            origin_ip = data.get('origin', 'unknown')
            
            result = {
                'id': request_id,
                'success': True,
                'ip': origin_ip,
                'duration': round(duration, 2),
                'status': response.status_code,
                'timestamp': time.time()
            }
            
        except Exception as e:
            duration = time.time() - start_time
            result = {
                'id': request_id,
                'success': False,
                'error': str(e),
                'duration': round(duration, 2),
                'timestamp': time.time()
            }
        
        # Thread-safe result storage
        with self.lock:
            self.results.append(result)
            
        return result
    
    def run_concurrency_test(self, num_threads: int = 20) -> Dict:
        """Run concurrent proxy test."""
        print(f"🚀 Starting {num_threads} concurrent requests...")
        print(f"🎯 Target proxy: {self.proxy_url}")
        print(f"📊 Expected proxy IPs: {len(self.proxy_ips)}")
        print("-" * 60)
        
        start_time = time.time()
        
        # Use ThreadPoolExecutor for true concurrency
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            # Submit all requests
            futures = [
                executor.submit(self.make_request, i+1) 
                for i in range(num_threads)
            ]
            
            # Collect results as they complete
            completed = 0
            for future in as_completed(futures):
                completed += 1
                result = future.result()
                if result['success']:
                    print(f"✅ Request {result['id']:2d}: {result['ip']} ({result['duration']:.2f}s)")
                else:
                    print(f"❌ Request {result['id']:2d}: {result['error']} ({result['duration']:.2f}s)")
        
        total_time = time.time() - start_time
        return self._analyze_results(total_time)
    
    def _analyze_results(self, total_time: float) -> Dict:
        """Analyze test results."""
        successful = [r for r in self.results if r['success']]
        failed = [r for r in self.results if not r['success']]
        
        # Collect unique IPs
        unique_ips = set(r['ip'] for r in successful)
        ip_counts = Counter(r['ip'] for r in successful)
        
        # Check which IPs are from proxy list
        proxy_ips_used = unique_ips.intersection(self.proxy_ips)
        non_proxy_ips = unique_ips - self.proxy_ips
        
        # Calculate metrics
        avg_duration = sum(r['duration'] for r in successful) / len(successful) if successful else 0
        success_rate = len(successful) / len(self.results) * 100 if self.results else 0
        
        # Determine proxy effectiveness
        proxy_working = len(proxy_ips_used) > 0
        rotation_working = len(unique_ips) > 1
        
        analysis = {
            'total_requests': len(self.results),
            'successful_requests': len(successful),
            'failed_requests': len(failed),
            'success_rate': success_rate,
            'unique_ips': len(unique_ips),
            'proxy_ips_used': len(proxy_ips_used),
            'non_proxy_ips': len(non_proxy_ips),
            'avg_response_time': avg_duration,
            'total_time': total_time,
            'proxy_working': proxy_working,
            'rotation_working': rotation_working,
            'all_ips': list(unique_ips),
            'proxy_ips_found': list(proxy_ips_used),
            'non_proxy_ips_found': list(non_proxy_ips),
            'ip_distribution': dict(ip_counts)
        }
        
        self._print_analysis(analysis)
        return analysis
    
    def _print_analysis(self, analysis: Dict):
        """Print detailed analysis."""
        print("\n" + "="*60)
        print("📊 PROXY CONCURRENCY TEST RESULTS")
        print("="*60)
        
        # Basic metrics
        print(f"✅ Successful requests: {analysis['successful_requests']}/{analysis['total_requests']} "
              f"({analysis['success_rate']:.1f}%)")
        print(f"❌ Failed requests: {analysis['failed_requests']}")
        print(f"⚡ Average response time: {analysis['avg_response_time']:.2f}s")
        print(f"⏱️  Total test time: {analysis['total_time']:.2f}s")
        
        # Concurrency analysis
        theoretical_time = analysis['avg_response_time'] * analysis['total_requests']
        if theoretical_time > 0:
            concurrency_factor = theoretical_time / analysis['total_time']
            print(f"🚀 Concurrency factor: {concurrency_factor:.1f}x (vs sequential)")
        
        print(f"\n🌍 IP Analysis:")
        print(f"   Unique IPs found: {analysis['unique_ips']}")
        print(f"   Proxy IPs used: {analysis['proxy_ips_used']}")
        print(f"   Non-proxy IPs: {analysis['non_proxy_ips']}")
        
        # Proxy status
        print(f"\n🎯 Proxy Status:")
        if analysis['proxy_working']:
            print(f"   ✅ Proxies WORKING - Found {analysis['proxy_ips_used']} proxy IPs")
        else:
            print(f"   ❌ Proxies NOT WORKING - No proxy IPs detected")
            
        if analysis['rotation_working']:
            print(f"   ✅ Rotation WORKING - {analysis['unique_ips']} different IPs")
        else:
            print(f"   ❌ Rotation NOT WORKING - Only 1 IP used")
        
        # Show IP details
        if analysis['proxy_ips_found']:
            print(f"\n✅ Proxy IPs found:")
            for ip in analysis['proxy_ips_found']:
                count = analysis['ip_distribution'][ip]
                print(f"   - {ip} (used {count} times)")
                
        if analysis['non_proxy_ips_found']:
            print(f"\n⚠️  Non-proxy IPs found:")
            for ip in analysis['non_proxy_ips_found']:
                count = analysis['ip_distribution'][ip]
                print(f"   - {ip} (used {count} times) ← Likely your home IP!")


def main():
    """Main test function."""
    parser = argparse.ArgumentParser(description='Test rotating-mitmproxy concurrency and proxy rotation')
    parser.add_argument('--threads', '-t', type=int, default=20, 
                       help='Number of concurrent threads (default: 20)')
    parser.add_argument('--proxy-url', '-p', default='http://localhost:9090',
                       help='Proxy URL (default: http://localhost:9090)')
    parser.add_argument('--proxy-list', '-l', default='proxy_list.txt',
                       help='Proxy list file (default: proxy_list.txt)')
    
    args = parser.parse_args()
    
    # Create tester
    tester = ProxyTester(args.proxy_url, args.proxy_list)
    
    if not tester.proxy_ips:
        print("❌ No proxy IPs loaded. Please check your proxy list file.")
        sys.exit(1)
    
    # Run test
    results = tester.run_concurrency_test(args.threads)
    
    # Exit with appropriate code
    if results['proxy_working'] and results['rotation_working']:
        print(f"\n🎉 SUCCESS: Proxy rotation working perfectly!")
        sys.exit(0)
    else:
        print(f"\n❌ FAILURE: Proxy issues detected!")
        sys.exit(1)


if __name__ == '__main__':
    main()
