import asyncio
import socket
import logging
from typing import Optional, Dict, Any
from django.conf import settings
from customer_sites.models import Site


logger = logging.getLogger(__name__)


class L4Forwarder:
    """
    Layer 4 TCP forwarding service for high-performance proxying
    """
    
    def __init__(self):
        self.connections = {}
        self.buffer_size = getattr(settings, 'L4_BUFFER_SIZE', 4096)
        self.timeout = getattr(settings, 'L4_TIMEOUT', 30)
    
    async def forward_connection(self, 
                               client_socket: socket.socket, 
                               target_site: Site,
                               client_ip: str) -> None:
        """
        Forward a TCP connection to the target site
        
        Args:
            client_socket: Client connection socket
            target_site: Target site configuration
            client_ip: Original client IP address
        """
        target_socket = None
        
        try:
            # Create connection to target server
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.settimeout(self.timeout)
            
            # Connect to target
            target_socket.connect((target_site.ip, target_site.port))
            
            # Set up bidirectional forwarding
            await asyncio.gather(
                self._forward_data(client_socket, target_socket, "client->target"),
                self._forward_data(target_socket, client_socket, "target->client")
            )
            
        except Exception as e:
            logger.error(f"L4 forwarding error for {target_site.domain}: {e}")
        finally:
            # Clean up connections
            if target_socket:
                target_socket.close()
            client_socket.close()
    
    async def _forward_data(self, 
                          source: socket.socket, 
                          destination: socket.socket, 
                          direction: str) -> None:
        """Forward data between two sockets"""
        try:
            while True:
                data = source.recv(self.buffer_size)
                if not data:
                    break
                
                # Add original client IP header if needed
                if direction == "client->target":
                    data = self._add_client_ip_header(data)
                
                destination.send(data)
                
        except Exception as e:
            logger.debug(f"Data forwarding error ({direction}): {e}")
    
    def _add_client_ip_header(self, data: bytes) -> bytes:
        """Add original client IP to the data stream"""
        # This is a simplified implementation
        # In practice, you might need to modify HTTP headers or use proxy protocol
        return data
    
    async def start_server(self, host: str = "0.0.0.0", port: int = 8080) -> None:
        """Start the L4 forwarding server"""
        server = await asyncio.start_server(
            self._handle_connection,
            host,
            port
        )
        
        logger.info(f"L4 Forwarder started on {host}:{port}")
        
        async with server:
            await server.serve_forever()
    
    async def _handle_connection(self, 
                               reader: asyncio.StreamReader, 
                               writer: asyncio.StreamWriter) -> None:
        """Handle incoming connections"""
        client_ip = writer.get_extra_info('peername')[0]
        
        try:
            # Read initial data to determine target
            data = await asyncio.wait_for(reader.read(1024), timeout=5.0)
            
            # Parse Host header to determine target site
            target_site = self._resolve_target_site(data)
            
            if target_site:
                # Convert to socket for forwarding
                client_socket = self._stream_to_socket(reader, writer)
                await self.forward_connection(client_socket, target_site, client_ip)
            else:
                logger.warning(f"No target site found for connection from {client_ip}")
                writer.close()
                
        except asyncio.TimeoutError:
            logger.warning(f"Connection timeout from {client_ip}")
            writer.close()
        except Exception as e:
            logger.error(f"Connection handling error: {e}")
            writer.close()
    
    def _resolve_target_site(self, data: bytes) -> Optional[Site]:
        """Resolve target site from connection data"""
        try:
            # Parse HTTP Host header
            data_str = data.decode('utf-8', errors='ignore')
            lines = data_str.split('\n')
            
            for line in lines:
                if line.lower().startswith('host:'):
                    host = line.split(':', 1)[1].strip()
                    # Remove port if present
                    host = host.split(':')[0]
                    
                    # Find matching site
                    try:
                        return Site.objects.get(domain=host, is_active=True)
                    except Site.DoesNotExist:
                        continue
            
            return None
            
        except Exception as e:
            logger.error(f"Error resolving target site: {e}")
            return None
    
    def _stream_to_socket(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> socket.socket:
        """Convert asyncio stream to socket (simplified)"""
        # This is a simplified implementation
        # In practice, you'd need a more sophisticated approach
        return socket.socket()


# Global L4 forwarder instance
l4_forwarder = L4Forwarder()
