"""
PixelAirDevice - Individual device management and OSC control.

This module provides the PixelAirDevice class that handles individual device state,
packet decoding, and OSC command sending.
"""

import asyncio
import socket
import time
import logging
from typing import Dict, Optional, List, Union, Any

from pythonosc.osc_message_builder import OscMessageBuilder

from .pixelair_generated import PixelAirDevice as PixelAirDeviceFB
from .pixelair_state import PixelAirState

class PixelAirDevice:
    """
    A PixelAir device that automatically decodes FlatBuffer packets and supports OSC control.
    
    This class handles both receiving state packets on port 12345 and sending OSC commands
    to the device on port 6767.
    """
    
    def __init__(self, ip_address: str):
        """
        Initialize a PixelAir device.
        
        Args:
            ip_address: IP address of the device (used as the device identifier)
        """
        self.ip_address = ip_address
        self.port = 12345  # Always use port 12345 for incoming packets
        self.last_seen = time.time()
        self.name: Optional[str] = None
        
        # Device state tracking
        self.last_decoded_state: Optional[PixelAirDeviceFB] = None
        self.decode_errors = 0
        self.successful_decodes = 0
        self.state = PixelAirState()
        
        # Logger for this device
        self.logger = logging.getLogger(f"PixelAirDevice:{self.ip_address}")
    
    async def set_power(self, on: bool) -> bool:
        """
        Set the power state of the device.
        
        Args:
            on: True to turn on, False to turn off
        
        Returns:
            bool: True if command was sent successfully, False otherwise
        """
        route = "/SyYOTiXjQBjW"
        params = [1 if on else 0]
        return await self._send_osc_message(route, params)
    
    async def set_brightness(self, brightness: int) -> bool:
        """
        Set the brightness of the device.
        
        Args:
            brightness: Brightness level (0-100)
        
        Returns:
            bool: True if command was sent successfully, False otherwise
        """
        if brightness < 0 or brightness > 100:
            self.logger.error("Brightness must be between 0 and 100")
            return False
        
        route = "/Uv7aMFw5P2lX"
        params = [float(brightness) / 100.0]
        return await self._send_osc_message(route, params)
    
    async def _send_osc_message(self, route: str, params: List[Union[int, float, str, bool]] = None) -> bool:
        """
        Send a binary OSC message to the device on port 6767.
        
        This is a private helper method for sending OSC commands to the device.
        
        Args:
            route: OSC route/address (e.g., "/device/brightness")
            params: Optional list of parameters to include in the message
        
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        if params is None:
            params = []
        
        try:
            # Build the OSC message
            msg_builder = OscMessageBuilder(route)
            
            # Add parameters to the message
            for param in params:
                if isinstance(param, int):
                    msg_builder.add_arg(param, 'i')  # integer
                elif isinstance(param, float):
                    msg_builder.add_arg(param, 'f')  # float
                elif isinstance(param, str):
                    msg_builder.add_arg(param, 's')  # string
                elif isinstance(param, bool):
                    msg_builder.add_arg(param, 'T' if param else 'F')  # true/false
                else:
                    # Try to convert to string as fallback
                    msg_builder.add_arg(str(param), 's')
            
            # Build the binary message
            osc_message = msg_builder.build()
            
            # Send the message asynchronously
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._send_udp_message, osc_message.dgram)
                
            self.logger.debug(f"Sent OSC message to {self.ip_address}:6767 - Route: {route}, Params: {params}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send OSC message to {self.ip_address}:6767 - Route: {route}, Error: {e}")
            return False
    
    def _send_udp_message(self, dgram: bytes) -> None:
        """
        Send a UDP datagram synchronously.
        
        This method is called from an executor to avoid blocking the event loop.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(5.0)  # 5 second timeout
            sock.sendto(dgram, (self.ip_address, 6767))
    
    def handle_packet(self, payload: bytes, is_response: bool):
        """
        Handle a complete defragmented packet from this device.
        
        This method decodes the payload as a PixelAir FlatBuffer and calls
        the appropriate handler method.
        
        Args:
            payload: Complete defragmented payload
            is_response: True if this is a response to a request, False if proactive
        """
        self.update_last_seen()
        self.logger.info(f"Received packet: {len(payload)} bytes, is_response={is_response}")

        try:
            device_state = PixelAirDeviceFB.GetRootAs(payload)
            self.last_decoded_state = device_state
            self.successful_decodes += 1
            
            # Call the state packet handler
            self.handle_state_packet(device_state, is_response)
            self.logger.info(f"Successfully processed packet from {self.ip_address}")
            
        except Exception as e:
            self.decode_errors += 1
            self.logger.error(f"Failed to decode packet from {self.ip_address}: {e}")
            self.logger.error(f"Payload size: {len(payload)} bytes")
            self.logger.error(f"Payload preview: {payload[:min(50, len(payload))].hex()}")
    
    def handle_state_packet(self, device_state: PixelAirDeviceFB, is_response: bool):
        """
        Handle a decoded PixelAir device state packet.
        
        This method can be overridden by subclasses to implement
        device-specific state handling logic.
        
        Args:
            device_state: Decoded PixelAir device state FlatBuffer
            is_response: True if this is a response to a request, False if proactive
        """
        # Default implementation logs basic device information
        model = device_state.Model() or "Unknown"
        serial = device_state.SerialNumber() or "Unknown"
        
        self.state.model = model
        self.state.serial_number = serial
        
        if device_state.Nickname():
            self.state.nickname = device_state.Nickname().Value()
        
        if device_state.Engine():
            self.state.is_on = device_state.Engine().IsDisplaying().Value()
            if device_state.Engine().Brightness():
                self.state.brightness = device_state.Engine().Brightness().Value() * 100.0

        # Log state update with meaningful information
        power_state = "ON" if self.state.is_on else "OFF"
        self.logger.info(f"State update - Model: {self.state.model}, Power: {power_state}, Brightness: {self.state.brightness:.1f}%")

    def get_device_info(self) -> Optional[Dict[str, Any]]:
        """
        Get device information dictionary.
        
        Returns:
            Dictionary with device information or None if no state available
        """
        if self.last_decoded_state is None:
            return None
        
        return {
            "ip_address": self.ip_address,
            "model": self.state.model,
            "serial_number": self.state.serial_number,
            "nickname": self.state.nickname,
            "is_on": self.state.is_on,
            "brightness": self.state.brightness,
            "last_seen": self.last_seen
        }
    
    def get_decode_stats(self) -> Dict[str, int]:
        """
        Get packet decode statistics.
        
        Returns:
            Dictionary with decode statistics
        """
        return {
            "successful_decodes": self.successful_decodes,
            "decode_errors": self.decode_errors,
            "total_packets": self.successful_decodes + self.decode_errors
        }

    def update_last_seen(self):
        """Update the last seen timestamp."""
        self.last_seen = time.time()
    
    def is_stale(self, timeout: float = 300.0) -> bool:
        """
        Check if this device hasn't been seen recently.
        
        Args:
            timeout: Timeout in seconds (default 5 minutes)
            
        Returns:
            True if device hasn't been seen within timeout period
        """
        return time.time() - self.last_seen > timeout
    
    def __str__(self) -> str:
        return f"PixelAirDevice({self.ip_address})"
    
    def __repr__(self) -> str:
        return self.__str__()
