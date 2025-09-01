from dataclasses import dataclass
from typing import Dict, Optional, Any
import time

from .pixelair_generated import PixelAirDevice

@dataclass
class DeviceInfo:
    """Information about a discovered PixelAir device in the registry."""
    ip_address: str
    last_seen: float
    nickname: Optional[str] = None
    mac_address: Optional[str] = None
    device_model: Optional[str] = None

    def __post_init__(self):
        if self.last_seen is None:
            self.last_seen = time.time()
    
    def update_from_packet(self, device_state: PixelAirDevice) -> None:
        """Update device information from a decoded FlatBuffer packet."""
        # Update device model
        if device_state.Model():
            self.device_model = device_state.Model().decode('utf-8')
        
        # Update nickname
        if device_state.Nickname() and device_state.Nickname().Value():
            self.nickname = device_state.Nickname().Value().decode('utf-8')
        
        # Update MAC address from network info
        if device_state.Network() and device_state.Network().MacAddress():
            self.mac_address = device_state.Network().MacAddress().decode('utf-8')
        
        # Update last seen timestamp
        self.last_seen = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for easy serialization/display."""
        return {
            'ip_address': self.ip_address,
            'nickname': self.nickname,
            'mac_address': self.mac_address,
            'device_model': self.device_model,
            'last_seen': self.last_seen
        }

