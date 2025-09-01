# device_status.py
from typing import TypedDict, Optional
from enum import Enum

class DeviceStatus(TypedDict, total=False):
    """设备状态固定格式"""
    is_lock: Optional[int]  # 必填
    heartbeat: Optional[int]  # 必填
    battery: Optional[float]  # 必填
    airspeed: Optional[float]  # 必填
    groundspeed: Optional[float]  # 必填
    yaw_degrees: Optional[float]  # 必填
    roll: Optional[float]  # 必填
    pitch: Optional[float]  # 必填
    yaw: Optional[float]  # 必填
    lat: Optional[float]  # 必填
    lon: Optional[float]  # 必填
    alt: Optional[float]  # 必填
    vzspeed: Optional[float]  # 必填
    height: Optional[float]  # 必填


class MessageType(Enum):
    TEXT = "text"  # 纯文本消息
    IMAGE = "image"  # 图像消息
    VIDEO_URL = "video_url"  # 视频流URL
    PROGRESS = "progress"  # 进度更新
    STATUS = "status"  # 状态更新

#消息级别: failed, warning, info, success
class MessageLevel(Enum):
    FAILED = "failed"  # 纯文本消息
    WARNING = "warning"  # 图像消息
    INFO = "info"  # 视频流URL
    SUCCESS = "success"  # 进度更新
