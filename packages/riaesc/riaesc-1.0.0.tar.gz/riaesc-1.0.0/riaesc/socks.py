import asyncio
import socket
import struct
from typing import Optional, Tuple, Union

__version__ = "1.0.0"
__author__ = "AsyncSOCKS"
__all__ = ["AsyncSOCKSSocket", "SOCKSError", "AuthenticationError", "ConnectionError", "create_connection"]


class SOCKSError(Exception):
    """Base SOCKS proxy error"""
    pass


class AuthenticationError(SOCKSError):
    """SOCKS authentication failed"""
    pass


class ConnectionError(SOCKSError):
    """SOCKS connection failed"""
    pass


class AsyncSOCKSSocket:
    """Async SOCKS5 socket for Pyrogram/Hydrogram TCP connections"""
    
    def __init__(self):
        self._proxy_host: Optional[str] = None
        self._proxy_port: Optional[int] = None
        self._username: Optional[str] = None
        self._password: Optional[str] = None
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._connected: bool = False

    def set_proxy(self, proxy_host: str, proxy_port: int, 
                  username: Optional[str] = None, password: Optional[str] = None) -> None:
        """Configure SOCKS5 proxy settings"""
        self._proxy_host = proxy_host
        self._proxy_port = proxy_port
        self._username = username
        self._password = password

    async def connect(self, target_host: str, target_port: int, 
                     timeout: float = 30.0, source_address: Optional[Tuple[str, int]] = None) -> None:
        """Connect to target through SOCKS5 proxy with optional source binding"""
        if not self._proxy_host or not self._proxy_port:
            raise SOCKSError("Proxy not configured")

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setblocking(False)
            
            if source_address:
                sock.bind(source_address)

            await asyncio.wait_for(
                asyncio.get_event_loop().sock_connect(sock, (self._proxy_host, self._proxy_port)),
                timeout=timeout
            )

            # Create reader/writer from socket
            self._reader, self._writer = await asyncio.open_connection(sock=sock)

            # SOCKS5 handshake
            await self._socks5_handshake(target_host, target_port, timeout)
            self._connected = True

        except asyncio.TimeoutError:
            raise ConnectionError(f"Timeout connecting to proxy {self._proxy_host}:{self._proxy_port}")
        except OSError as e:
            raise ConnectionError(f"Failed to connect to proxy: {e}")

    async def _socks5_handshake(self, target_host: str, target_port: int, timeout: float) -> None:
        """Perform SOCKS5 handshake with authentication support"""
        # Method selection
        if self._username and self._password:
            auth_methods = b'\x02\x00\x02'  # No-auth + Username/Password
        else:
            auth_methods = b'\x01\x00'  # No-auth only

        self._writer.write(b'\x05' + auth_methods)
        await asyncio.wait_for(self._writer.drain(), timeout=timeout)

        # Read method selection response
        response = await asyncio.wait_for(self._reader.read(2), timeout=timeout)
        if len(response) != 2 or response[0] != 0x05:
            raise SOCKSError("Invalid SOCKS5 response")

        selected_method = response[1]
        
        if selected_method == 0x00:  # No authentication
            pass
        elif selected_method == 0x02:  # Username/Password
            await self._authenticate(timeout)
        elif selected_method == 0xFF:  # No acceptable methods
            raise AuthenticationError("No acceptable authentication methods")
        else:
            raise SOCKSError(f"Unsupported authentication method: {selected_method}")

        # Connection request
        await self._connect_request(target_host, target_port, timeout)

    async def _authenticate(self, timeout: float) -> None:
        """Perform username/password authentication"""
        if not self._username or not self._password:
            raise AuthenticationError("Username/password required")

        username_bytes = self._username.encode('utf-8')
        password_bytes = self._password.encode('utf-8')

        if len(username_bytes) > 255 or len(password_bytes) > 255:
            raise AuthenticationError("Username or password too long")

        # Send auth request
        auth_request = (b'\x01' + 
                       bytes([len(username_bytes)]) + username_bytes +
                       bytes([len(password_bytes)]) + password_bytes)
        
        self._writer.write(auth_request)
        await asyncio.wait_for(self._writer.drain(), timeout=timeout)

        # Read auth response
        response = await asyncio.wait_for(self._reader.read(2), timeout=timeout)
        if len(response) != 2 or response[0] != 0x01:
            raise AuthenticationError("Invalid authentication response")

        if response[1] != 0x00:
            raise AuthenticationError("Authentication failed")

    async def _connect_request(self, target_host: str, target_port: int, timeout: float) -> None:
        """Send SOCKS5 connect request"""
        # Build connect request
        request = b'\x05\x01\x00'  # SOCKS5, CONNECT, Reserved

        # Address type and address
        if self._is_ipv4(target_host):
            request += b'\x01' + socket.inet_aton(target_host)
        elif self._is_ipv6(target_host):
            request += b'\x04' + socket.inet_pton(socket.AF_INET6, target_host)
        else:
            # Domain name
            domain_bytes = target_host.encode('utf-8')
            if len(domain_bytes) > 255:
                raise SOCKSError("Domain name too long")
            request += b'\x03' + bytes([len(domain_bytes)]) + domain_bytes

        # Port
        request += struct.pack('>H', target_port)

        self._writer.write(request)
        await asyncio.wait_for(self._writer.drain(), timeout=timeout)

        # Read connect response
        response = await asyncio.wait_for(self._reader.read(4), timeout=timeout)
        if len(response) != 4:
            raise ConnectionError("Incomplete SOCKS5 response")

        if response[0] != 0x05:
            raise SOCKSError("Invalid SOCKS5 version")

        reply_code = response[1]
        if reply_code != 0x00:
            self._raise_connection_error(reply_code)

        # Read bound address (skip it)
        addr_type = response[3]
        if addr_type == 0x01:  # IPv4
            await asyncio.wait_for(self._reader.read(6), timeout=timeout)
        elif addr_type == 0x03:  # Domain
            domain_len = (await asyncio.wait_for(self._reader.read(1), timeout=timeout))[0]
            await asyncio.wait_for(self._reader.read(domain_len + 2), timeout=timeout)
        elif addr_type == 0x04:  # IPv6
            await asyncio.wait_for(self._reader.read(18), timeout=timeout)
        else:
            raise SOCKSError(f"Unknown address type: {addr_type}")

    def _is_ipv4(self, host: str) -> bool:
        """Check if host is IPv4 address"""
        try:
            socket.inet_aton(host)
            return True
        except socket.error:
            return False

    def _is_ipv6(self, host: str) -> bool:
        """Check if host is IPv6 address"""
        try:
            socket.inet_pton(socket.AF_INET6, host)
            return True
        except socket.error:
            return False

    def _raise_connection_error(self, reply_code: int) -> None:
        """Raise appropriate error based on SOCKS5 reply code"""
        error_messages = {
            0x01: "General SOCKS server failure",
            0x02: "Connection not allowed by ruleset",
            0x03: "Network unreachable",
            0x04: "Host unreachable",
            0x05: "Connection refused",
            0x06: "TTL expired",
            0x07: "Command not supported",
            0x08: "Address type not supported"
        }
        message = error_messages.get(reply_code, f"Unknown SOCKS error: {reply_code}")
        raise ConnectionError(message)

    @property
    def reader(self) -> Optional[asyncio.StreamReader]:
        """Get asyncio StreamReader for reading data"""
        return self._reader

    @property
    def writer(self) -> Optional[asyncio.StreamWriter]:
        """Get asyncio StreamWriter for writing data"""
        return self._writer

    @property
    def connected(self) -> bool:
        """Check if socket is connected"""
        return self._connected

    def close(self) -> None:
        """Synchronously close connection"""
        if self._writer:
            self._writer.close()
        self._connected = False

    async def aclose(self) -> None:
        """Asynchronously close connection"""
        if self._writer:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except Exception:
                pass
        self._reader = None
        self._writer = None
        self._connected = False


def create_connection(address: Tuple[str, int], **kwargs) -> AsyncSOCKSSocket:
  
    return AsyncSOCKSSocket()


# Example usage
async def main():
    s = AsyncSOCKSSocket()
    s.set_proxy("127.0.0.1", 1080, "user", "pass")
    await s.connect("149.154.167.50", 443)
    reader, writer = s.reader, s.writer
    await s.aclose()


if __name__ == "__main__":
    asyncio.run(main())