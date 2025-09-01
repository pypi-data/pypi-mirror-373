"""
PixelAirClient - UDP client for receiving fragmented packets from PixelAir devices.

This module provides the main client class that listens for UDP packets on port 12345,
manages fragmented packet reassembly, and maintains a registry of connected devices.
"""

import socket
import threading
import time
import ipaddress
from typing import Dict, Optional
import logging

import netifaces
from pythonosc.osc_message_builder import OscMessageBuilder

from .fragmented_state_manager import FragmentedStateManager
from .pixelair_generated import PixelAirDevice as PixelAirDeviceFB
from .pixelair_device import PixelAirDevice
from .device_info import DeviceInfo

class PixelAirClient:
    """
    UDP client for receiving fragmented packets from PixelAir devices.
    
    This class manages:
    - UDP socket listening on port 12345
    - Device registry to track connected devices
    - Fragmented packet reassembly per device
    - Packet routing to appropriate devices
    """
    
    def __init__(self):
        """
        Initialize the PixelAir client.
        
        Args:
            mtu: Maximum transmission unit (default 2048)
            bind_address: Address to bind to (default "0.0.0.0" for all interfaces)
            device_timeout: Timeout for considering devices stale (default 5 minutes)
        """
        
        # Device registry: IP address -> PixelAirDevice (manually registered/configured devices)
        self.devices: Dict[str, PixelAirDevice] = {}
        self.devices_lock = threading.RLock()
        
        # Discovered devices: IP address -> discovery info (separate from registered devices)
        self.discovered_devices: Dict[str, DeviceInfo] = {}
        self.discovered_lock = threading.RLock()
        
        # Fragment managers per device: IP address -> FragmentedStateManager
        self.fragment_managers: Dict[str, FragmentedStateManager] = {}
        self.fragment_lock = threading.RLock()
        
        # Socket and threading
        self.socket: Optional[socket.socket] = None
        self.discovery_socket: Optional[socket.socket] = None
        self.running = False
        self.listen_thread: Optional[threading.Thread] = None
        self.cleanup_thread: Optional[threading.Thread] = None
        self.discovery_thread: Optional[threading.Thread] = None

        # Logging
        self.logger = logging.getLogger("PixelAirClient")
    
    def start(self) -> bool:
        """
        Start the UDP listener and background threads.
        
        Returns:
            True if started successfully, False otherwise
        """
        if self.running:
            self.logger.warning("Client is already running")
            return False
        
        try:
            # Create and bind socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Set receive buffer size based on MTU
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2048 * 16)
            
            self.socket.bind(("0.0.0.0", 12345))
            self.socket.settimeout(1.0)  # 1 second timeout for clean shutdown
            
            # Create discovery socket for broadcasting
            self.discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            self.running = True
            
            # Start listener thread
            self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listen_thread.start()
            
            # Start cleanup thread
            self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
            self.cleanup_thread.start()
            
            # Start discovery thread
            self.discovery_thread = threading.Thread(target=self._discovery_loop, daemon=True)
            self.discovery_thread.start()
            
            # Send initial discovery broadcast
            self._send_discovery_broadcast()
            
            self.logger.info("PixelAirClient started.")
            return True
            
        except Exception as e:
            self.logger.error("Failed to start client (OSError): %s", e)
            self.running = False
            if self.socket:
                self.socket.close()
                self.socket = None
            return False
    
    def stop(self):
        """Stop the UDP listener and background threads."""
        if not self.running:
            return
        
        self.logger.info("Stopping PixelAirClient...")
        self.running = False
        
        # Close socket
        if self.socket:
            self.socket.close()
            self.socket = None
            
        # Close discovery socket
        if self.discovery_socket:
            self.discovery_socket.close()
            self.discovery_socket = None
        
        # Wait for threads to finish
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=2.0)
        
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=2.0)
        
        # Shutdown all fragment managers
        with self.fragment_lock:
            for manager in self.fragment_managers.values():
                manager.shutdown()
            self.fragment_managers.clear()
        
        self.logger.info("PixelAirClient stopped")
    
    def register_device(self, ip_address: str) -> bool:
        """
        Register a device in the client registry (creates PixelAirDevice instance).
        
        Args:
            ip_address: IP address of the device to register
            
        Returns:
            True if registered successfully, False if already exists
        """
        with self.devices_lock:
            if ip_address in self.devices:
                self.logger.warning("Device %s already registered", ip_address)
                return False
            
            # Create PixelAirDevice instance directly (no more circular import)
            device = PixelAirDevice(ip_address)
            self.devices[ip_address] = device
            self.logger.info("Registered PixelAir device: %s", ip_address)
            return True
    
    def unregister_device(self, ip_address: str) -> bool:
        """
        Unregister a device from the client registry.
        
        Args:
            ip_address: IP address of device to unregister
            
        Returns:
            True if unregistered successfully, False if not found
        """
        with self.devices_lock:
            if ip_address not in self.devices:
                return False
            
            device = self.devices.pop(ip_address)
            self.logger.info("Unregistered device: %s", device.ip_address)
            
            # Clean up fragment manager for this device
            with self.fragment_lock:
                if ip_address in self.fragment_managers:
                    self.fragment_managers[ip_address].shutdown()
                    del self.fragment_managers[ip_address]
            
            return True
    
    def get_device(self, ip_address: str) -> Optional[PixelAirDevice]:
        """
        Get a registered device by IP address.
        
        Args:
            ip_address: IP address of the device
            
        Returns:
            PixelAirDevice instance or None if not found
        """
        with self.devices_lock:
            return self.devices.get(ip_address)
    
    def get_all_devices(self) -> Dict[str, PixelAirDevice]:
        """
        Get all registered devices.
        
        Returns:
            Dictionary mapping IP addresses to PixelAirDevice instances
        """
        with self.devices_lock:
            return self.devices.copy()
    
    def get_registered_devices(self) -> Dict[str, PixelAirDevice]:
        """
        Get all registered devices (alias for get_all_devices).
        
        Returns:
            Dictionary mapping IP addresses to PixelAirDevice instances
        """
        return self.get_all_devices()
    
    def get_discovered_devices(self) -> Dict[str, DeviceInfo]:
        """
        Get all discovered devices (not registered/configured).
        
        Returns:
            Dictionary mapping IP addresses to DeviceInfo instances
        """
        with self.discovered_lock:
            return self.discovered_devices.copy()
        
    def _handle_discovery(self, ip_address: str, device_state: PixelAirDeviceFB) -> DeviceInfo:
        """
        Track a discovered device (does NOT auto-register it).
        
        Args:
            ip_address: IP address of the device (used as the device identifier)
            device_state: Optional decoded device state for extracting additional info
            
        Returns:
            The DeviceInfo for the discovered device
        """
        with self.discovered_lock:
            if ip_address in self.discovered_devices:
                # Update existing discovery info
                device_info = self.discovered_devices[ip_address]
                device_info.last_seen = time.time()
                
                # Update from packet data if available
                if device_state:
                    device_info.update_from_packet(device_state)
            else:
                # Add new discovered device
                device_info = DeviceInfo(
                    ip_address=ip_address,
                    last_seen=time.time(),
                )
                
                # Update from packet data if available
                if device_state:
                    device_info.update_from_packet(device_state)
                
                self.discovered_devices[ip_address] = device_info
        
        return device_info
    
    def _get_fragment_manager(self, ip_address: str) -> FragmentedStateManager:
        """Get or create a fragment manager for a device."""
        with self.fragment_lock:
            if ip_address not in self.fragment_managers:
                # Create callback that routes complete payloads to the device
                def payload_callback(payload: bytes, is_response: bool):
                    self._handle_complete_payload(ip_address, payload, is_response)
                
                self.fragment_managers[ip_address] = FragmentedStateManager(payload_callback)
            
            return self.fragment_managers[ip_address]
    
    def _handle_complete_payload(self, ip_address: str, payload: bytes, is_response: bool):
        """Handle a complete defragmented payload from a device."""
        
        # Check if this is a registered device
        device = self.get_device(ip_address)
        if device is not None:
            device.handle_packet(payload, is_response)
        else:
            # Decode the payload to extract device information
            device_state = PixelAirDeviceFB.GetRootAs(payload)
            self._handle_discovery(ip_address, device_state=device_state)
    
    def _listen_loop(self):
        """Main UDP listening loop."""
        self.logger.info("UDP listener started")
        
        while self.running and self.socket:
            try:
                data, address = self.socket.recvfrom(2048)
                ip_address = address[0]
                
                self.logger.info(f"Received {len(data)} bytes from {ip_address}")

                # Get fragment manager for this device
                fragment_manager = self._get_fragment_manager(ip_address)
                fragment_manager.process_buffer(data)
            except Exception:
                continue
        
        self.logger.info("UDP listener stopped")
    
    def _cleanup_loop(self):
        """Background cleanup loop for stale devices and connections."""
        while self.running:
            try:
                time.sleep(30)  # Clean up every 30 seconds
                
                if not self.running:
                    break
                
                current_time = time.time()
                stale_devices = []
                stale_discovered = []
                
                # Find stale registered devices
                with self.devices_lock:
                    for ip_address, device in self.devices.items():
                        if device.is_stale(300):
                            stale_devices.append(ip_address)
                
                # Find stale discovered devices
                with self.discovered_lock:
                    for ip_address, device_info in self.discovered_devices.items():
                        if current_time - device_info.last_seen > 300:
                            stale_discovered.append(ip_address)
                
                # Remove stale registered devices
                for ip_address in stale_devices:
                    self.unregister_device(ip_address)
                
            except Exception:
                continue
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
    
    def _get_interface_ips(self) -> Dict[str, Dict[str, str]]:
        """Get all network interface IP addresses with netmask information."""
        interface_data = {}
        try:
            for interface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    for addr_info in addrs[netifaces.AF_INET]:
                        ip = addr_info.get('addr')
                        netmask = addr_info.get('netmask', '255.255.255.0')  # Default netmask
                        if ip and ip != '127.0.0.1':  # Skip localhost
                            interface_data[interface] = {
                                'ip': ip,
                                'netmask': netmask
                            }
        except Exception as e:
            self.logger.error(f"Error getting interface IPs: {e}")
        return interface_data
    
    def _send_discovery_packet(self, interface_ip: str, netmask: str):
        """
        Send a discovery packet on a specific interface.
        
        Args:
            interface_name: Name of the network interface
            interface_ip: IP address of the interface
            netmask: Netmask of the interface
        """
        
        builder = OscMessageBuilder("/fluoraDiscovery")
        
        # Convert IP address to ASCII integers
        for char in interface_ip:
            builder.add_arg(ord(char))
        
        # Get the OSC message bytes
        msg = builder.build()
        osc_bytes = msg.dgram
        
        # Calculate proper broadcast address using ipaddress module
        try:
            network = ipaddress.IPv4Network(f"{interface_ip}/{netmask}", strict=False)
            broadcast_ip = str(network.broadcast_address)

        except (ipaddress.AddressValueError, ipaddress.NetmaskValueError):
            ip_parts = interface_ip.split('.')
            if len(ip_parts) == 4:
                broadcast_ip = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.255"
            else:
                broadcast_ip = "255.255.255.255"
        
        if hasattr(self.discovery_socket, 'sendto') is False:
            self.logger.info("Discovery socket is not available for sending")
            return
        
        # Send to port 9090
        self.discovery_socket.sendto(osc_bytes, (broadcast_ip, 9090))
        self.logger.info(f"Sent discovery packet on {interface_ip} (broadcast {broadcast_ip})")
    
    def _send_discovery_broadcast(self):
        """Send discovery packets on all available interfaces."""
        if not self.discovery_socket:
            return
            
        interface_data = self._get_interface_ips()
        
        if not interface_data:
            self.logger.warning("No network interfaces found for discovery broadcast")
            return
            
        for _, data in interface_data.items():
            self._send_discovery_packet(data['ip'], data['netmask'])

    def _discovery_loop(self):
        """Background loop for sending discovery packets every minute."""
        while self.running:
            try:
                time.sleep(5)  # Wait 60 seconds between broadcasts
                
                if not self.running:
                    break
                    
                self._send_discovery_broadcast()
                
            except Exception:
                continue
