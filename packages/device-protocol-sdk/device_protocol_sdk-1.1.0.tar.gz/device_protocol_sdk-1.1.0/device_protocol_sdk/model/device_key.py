# device_key.py
from dataclasses import dataclass

@dataclass(frozen=True)
class DeviceKey:
    """不可变的设备唯一标识"""
    device_id: str  # 业务唯一字符串
    connection_str: str  # 连接参数（如IP/串口号）