#!/usr/bin/env python3
"""
Modern SOCKS Handler for urllib.request
Compatible with Python 3.10+

Usage:
    opener = create_opener(socks.SOCKS5, "localhost", 9050)
    response = opener.open("https://httpbin.org/ip")
"""
import socket
import ssl
import urllib.request
import http.client
import socks


def merge_dict(a, b):
    d = a.copy()
    d.update(b)
    return d


def is_ip(s):
    try:
        if ':' in s:
            socket.inet_pton(socket.AF_INET6, s)
        elif '.' in s:
            socket.inet_aton(s)
        else:
            return False
    except (socket.error, OSError, ValueError):
        return False
    else:
        return True


socks4_no_rdns = set()

class SOCKSConnection(http.client.HTTPConnection):
    def __init__(self, proxy_type, proxy_addr, proxy_port=None, rdns=True, 
                 username=None, password=None, *args, **kwargs):
        self.proxy_args = (proxy_type, proxy_addr, proxy_port, rdns, username, password)
        super().__init__(*args, **kwargs)

    def connect(self):
        proxy_type, proxy_addr, proxy_port, rdns, username, password = self.proxy_args
        rdns = rdns and proxy_addr not in socks4_no_rdns
        
        max_retries = 2  # ✅ Batas retry
        for attempt in range(max_retries):
            try:
                sock = socks.create_connection(
                    (self.host, self.port), self.timeout, None,
                    proxy_type, proxy_addr, proxy_port, rdns, username, password,
                    ((socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),))
                break
            except socks.SOCKS4Error as e:
                if attempt < max_retries - 1 and rdns and "0x5b" in str(e) and not is_ip(self.host):
                    rdns = False
                    socks4_no_rdns.add(proxy_addr)
                    continue  # ✅ Try again dengan rdns=False
                raise  # ✅ Re-raise jika sudah max retry
        else:
            raise ConnectionError("Failed to establish SOCKS connection after retries")
        
        self.sock = sock


class SOCKSHTTPSConnection(http.client.HTTPSConnection):
    def __init__(self, proxy_type, proxy_addr, proxy_port=None, rdns=True,
                 username=None, password=None, *args, **kwargs):
        self.proxy_args = (proxy_type, proxy_addr, proxy_port, rdns, username, password)
        super().__init__(*args, **kwargs)

    def connect(self):
        # Create SOCKS connection first
        proxy_type, proxy_addr, proxy_port, rdns, username, password = self.proxy_args
        rdns = rdns and proxy_addr not in socks4_no_rdns
        
        while True:
            try:
                sock = socks.create_connection(
                    (self.host, self.port), self.timeout, None,
                    proxy_type, proxy_addr, proxy_port, rdns, username, password,
                    ((socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),))
                break
            except socks.SOCKS4Error as e:
                if rdns and "0x5b" in str(e) and not is_ip(self.host):
                    rdns = False
                    socks4_no_rdns.add(proxy_addr)
                else:
                    raise
        
        # Wrap with SSL
        self.sock = self._context.wrap_socket(sock, server_hostname=self.host)

        if not self._context.check_hostname and self._check_hostname:
            try:
                ssl.match_hostname(self.sock.getpeercert(), self.host)
            except Exception as e:
                try:
                    self.sock.shutdown(socket.SHUT_RDWR)
                except (OSError, socket.error):
                    pass
                finally:
                    self.sock.close()
                raise ConnectionError(f"SSL hostname verification failed: {e}")


class SOCKSHandler(urllib.request.HTTPHandler, urllib.request.HTTPSHandler):
    def __init__(self, proxy_type, proxy_addr, proxy_port=None, rdns=True,
                 username=None, password=None, **kwargs):
        self.proxy_args = (proxy_type, proxy_addr, proxy_port, rdns, username, password)
        self.connection_kwargs = kwargs
        super().__init__()
    
    def http_open(self, req):
        def build_connection(host, port=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, **kwargs):
            merged_kwargs = {**self.connection_kwargs, **kwargs}
            return SOCKSConnection(*self.proxy_args, host=host, port=port, 
                                 timeout=timeout, **merged_kwargs)
        
        return self.do_open(build_connection, req)
    
    def https_open(self, req):
        def build_connection(host, port=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, **kwargs):
            merged_kwargs = {**self.connection_kwargs, **kwargs}
            return SOCKSHTTPSConnection(*self.proxy_args, host=host, port=port,
                                      timeout=timeout, **merged_kwargs)
        
        return self.do_open(build_connection, req)


def create_opener(proxy_type, proxy_addr, proxy_port=None, rdns=True,
                  username=None, password=None, **handler_kwargs):
    """
    Create urllib opener with SOCKS proxy support
    
    Args:
        proxy_type: socks.SOCKS4, socks.SOCKS5, or socks.HTTP
        proxy_addr: Proxy server address
        proxy_port: Proxy server port (default depends on proxy type)
        rdns: Use remote DNS resolution (default True)
        username: Proxy authentication username (optional)
        password: Proxy authentication password (optional)
    
    Returns:
        urllib.request.OpenerDirector instance
    """
    handler = SOCKSHandler(proxy_type, proxy_addr, proxy_port, rdns,
                          username, password, **handler_kwargs)
    return urllib.request.build_opener(handler)


if __name__ == "__main__":
    import sys
    
    try:
        if len(sys.argv) > 1:
            port = int(sys.argv[1])
        else:
            port = 9050  # Default Tor SOCKS port
    except ValueError:
        print("Usage: python sockshandler.py [port]")
        sys.exit(1)
    
    # Create opener with SOCKS5 proxy
    opener = create_opener(socks.SOCKS5, "localhost", port)
    
    try:
        print("Testing HTTP connection...")
        response = opener.open("http://httpbin.org/ip", timeout=10)
        print(f"HTTP IP: {response.read().decode().strip()}")
        
        print("\nTesting HTTPS connection...")
        response = opener.open("https://httpbin.org/ip", timeout=10)
        print(f"HTTPS IP: {response.read().decode().strip()}")
        
    except Exception as e:
        print(f"Error: {e}")
        print(f"Make sure SOCKS proxy is running on localhost:{port}")
        sys.exit(1)