"""
Debug Port Manager
==================

Manages allocation and release of debug ports for Chrome browsers.
Each browser instance needs a unique debug port for remote debugging.
"""

import asyncio
import logging
from typing import Set

logger = logging.getLogger(__name__)


class DebugPortManager:
    """Manages debug port allocation for browser instances"""
    
    def __init__(self, port_start: int = 9222, port_end: int = 9322):
        """
        Initialize debug port manager.
        
        Args:
            port_start: Starting port number (inclusive)
            port_end: Ending port number (exclusive)
        """
        if port_start <= 0 or port_end <= 0:
            raise ValueError("Port numbers must be positive")
        
        if port_end <= port_start:
            raise ValueError("port_end must be greater than port_start")
        
        self.port_start = port_start
        self.port_end = port_end
        
        # Available and used port tracking
        self.available_ports: Set[int] = set(range(port_start, port_end))
        self.used_ports: Set[int] = set()
        
        # Thread-safe port operations
        self._port_lock = asyncio.Lock()
        
        logger.info(f"DebugPortManager initialized: {len(self.available_ports)} ports available ({port_start}-{port_end-1})")
    
    async def allocate_port(self) -> int:
        """
        Allocate a debug port for browser use.
        
        Returns:
            Available port number
            
        Raises:
            RuntimeError: If no ports are available
        """
        async with self._port_lock:
            if not self.available_ports:
                raise RuntimeError(f"No available debug ports (range: {self.port_start}-{self.port_end-1})")
            
            port = self.available_ports.pop()
            self.used_ports.add(port)
            
            logger.debug(f"Allocated debug port: {port} ({len(self.available_ports)} remaining)")
            return port
    
    async def release_port(self, port: int):
        """
        Release a debug port back to the available pool.
        
        Args:
            port: Port number to release
        """
        async with self._port_lock:
            if port in self.used_ports:
                self.used_ports.remove(port)
                self.available_ports.add(port)
                logger.debug(f"Released debug port: {port} ({len(self.available_ports)} available)")
            else:
                logger.warning(f"Attempted to release port {port} that was not in use")
    
    async def get_stats(self) -> dict:
        """
        Get port allocation statistics.
        
        Returns:
            Dictionary with port statistics
        """
        async with self._port_lock:
            return {
                'total_ports': self.port_end - self.port_start,
                'available_ports': len(self.available_ports),
                'used_ports': len(self.used_ports),
                'port_range': f"{self.port_start}-{self.port_end-1}",
                'used_port_list': sorted(list(self.used_ports)),
                'available_port_list': sorted(list(self.available_ports))
            }
    
    def is_port_available(self, port: int) -> bool:
        """
        Check if a specific port is available (non-async for quick checks).
        
        Args:
            port: Port number to check
            
        Returns:
            True if port is available, False otherwise
        """
        return port in self.available_ports
    
    def get_available_count(self) -> int:
        """
        Get count of available ports (non-async for quick checks).
        
        Returns:
            Number of available ports
        """
        return len(self.available_ports)
    
    def get_used_count(self) -> int:
        """
        Get count of used ports (non-async for quick checks).
        
        Returns:
            Number of used ports
        """
        return len(self.used_ports)
    
    async def reset(self):
        """
        Reset all ports to available state.
        Useful for cleanup or testing.
        """
        async with self._port_lock:
            self.used_ports.clear()
            self.available_ports = set(range(self.port_start, self.port_end))
            logger.info(f"Reset all ports: {len(self.available_ports)} ports available")
    
    async def reserve_ports(self, count: int) -> list[int]:
        """
        Reserve multiple ports at once.
        
        Args:
            count: Number of ports to reserve
            
        Returns:
            List of allocated port numbers
            
        Raises:
            RuntimeError: If not enough ports are available
        """
        if count <= 0:
            return []
        
        async with self._port_lock:
            if len(self.available_ports) < count:
                raise RuntimeError(f"Not enough ports available: requested {count}, available {len(self.available_ports)}")
            
            allocated_ports = []
            for _ in range(count):
                port = self.available_ports.pop()
                self.used_ports.add(port)
                allocated_ports.append(port)
            
            logger.debug(f"Reserved {count} ports: {allocated_ports}")
            return allocated_ports
    
    async def release_ports(self, ports: list[int]):
        """
        Release multiple ports at once.
        
        Args:
            ports: List of port numbers to release
        """
        async with self._port_lock:
            for port in ports:
                if port in self.used_ports:
                    self.used_ports.remove(port)
                    self.available_ports.add(port)
            
            logger.debug(f"Released {len(ports)} ports")
    
    def __str__(self) -> str:
        """String representation of port manager state."""
        return f"DebugPortManager(range={self.port_start}-{self.port_end-1}, available={len(self.available_ports)}, used={len(self.used_ports)})"
    
    def __repr__(self) -> str:
        """Detailed representation of port manager state."""
        return f"DebugPortManager(port_start={self.port_start}, port_end={self.port_end}, available_ports={len(self.available_ports)}, used_ports={len(self.used_ports)})"
