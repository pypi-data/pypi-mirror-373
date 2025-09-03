from abc import ABC, abstractmethod
import threading
import json,uuid,time
from typing import List
from collections import defaultdict
from .model.device_key import DeviceKey
from .model.action_item import ActionItem
from .model.device_status import DeviceStatus,MessageType,MessageLevel
from typing import Dict, Any, Optional
import grpc
from . import device_pb2

from contextlib import contextmanager
from typing import Generator
import logging
logger = logging.getLogger(__name__)





class AbstractDevice(ABC):
    _status_cache: Dict[DeviceKey, dict] = {}
    _connection_pool: Dict[DeviceKey, Any] = {}  # 类级连接池
    _lock = threading.RLock()

    _monitor_flags = defaultdict(bool)  # 状态监控标志
    _monitor_futures = {}
    _lock = threading.Lock()  # 线程安全锁
    _status_lock = threading.RLock()  # 新增：状态读取可重入锁

    def __init__(self):
        self._grpc_stub = None
        self._current_mission_id = None

    def set_grpc_stub(self, grpc_stub):
        """设置gRPC stub用于发送消息"""
        self._grpc_stub = grpc_stub

    def set_current_mission_id(self, mission_id: str):
        """设置当前任务的mission_id"""
        self._current_mission_id = mission_id

    @contextmanager
    def mission_context(self, mission_id: str) -> Generator[None, None, None]:
        """为任务提供独立的上下文"""
        original_mission_id = getattr(self, '_current_mission_id', None)
        try:
            self._current_mission_id = mission_id
            yield
        finally:
            self._current_mission_id = original_mission_id
    def send_message(self, device_id: int, message_type: MessageType, content: str,level:MessageLevel,
                    metadata: Optional[Dict[str, Any]] = None,
                    mission_id: Optional[str] = None) -> bool:
        """
        通过gRPC向服务端发送消息

        Args:
            message_type: 消息类型
            content: 消息内容
            metadata: 附加元数据
            mission_id: 任务ID，如果为None则使用当前任务ID

        Returns:
            bool: 发送是否成功
        """
        target_mission_id = mission_id or self._current_mission_id
        if not target_mission_id:
            logger.warning("未提供mission_id且当前无任务上下文")
            return False

        if not self._grpc_stub:
            logger.warning("gRPC stub未设置，无法发送消息")
            return False

        # 确定mission_id
        target_mission_id = mission_id or self._current_mission_id
        if not target_mission_id:
            logger.warning("未提供mission_id且当前无任务ID，无法发送消息")
            return False

        try:
            # 构建gRPC消息
            device_message = device_pb2.DeviceMessage(
                mission_id=target_mission_id,
                message_type=message_type.value,
                message_level=level.value,
                content=content,
                timestamp=int(time.time()),
                metadata=json.dumps(metadata) if metadata else "",
                device_id=int(device_id)
            )

            # 发送消息（假设服务端有ReceiveDeviceMessage方法）
            self._grpc_stub.ReceiveDeviceMessage(device_message)

        except grpc.RpcError as e:
            logger.error(f"gRPC消息发送失败: {e}")
            return False
        except Exception as e:
            logger.error(f"发送消息时发生异常: {e}")
            return False

    def send_text_message(self, device_id: int, text: str,level:MessageLevel, **kwargs) -> bool:
        """发送纯文本消息的快捷方法"""
        return self.send_message(device_id,MessageType.TEXT, text,level, **kwargs)

    def send_image_message(self, device_id: int, image_data_or_url: str,level:MessageLevel, **kwargs) -> bool:
        """发送图像消息的快捷方法"""
        metadata = kwargs.pop('metadata', {})
        if 'description' not in metadata:
            metadata['description'] = '设备上传的图像'
        return self.send_message(device_id,MessageType.IMAGE, image_data_or_url,level, metadata, **kwargs)

    def send_video_url_message(self, device_id: int, video_url: str,level:MessageLevel, **kwargs) -> bool:
        """发送视频URL消息的快捷方法"""
        metadata = kwargs.pop('metadata', {})
        if 'description' not in metadata:
            metadata['description'] = '设备视频流地址'
        return self.send_message(device_id,MessageType.VIDEO_URL, video_url,level, metadata, **kwargs)

    @property
    @abstractmethod
    def protocol_name(self) -> str:
        pass

    @abstractmethod
    def get_action_list(self) -> List[ActionItem]:
        pass
    def connect(self, device_key: DeviceKey) -> Any:
        """带设备ID的连接池实现"""
        with self._lock:
            if device_key not in self._connection_pool:
                client = self._create_client(device_key.device_id,device_key.connection_str)
                self._connection_pool[device_key] = client

    def disconnect(self, device_key: DeviceKey):
        with self._lock:
            if device_key in self._connection_pool:
                self._close_client(self._connection_pool[device_key],device_key.device_id,device_key.connection_str)
                # 清空连接池中对应device_key的数据
                del self._connection_pool[device_key]
                logger.info(f"已从连接池中移除设备 {device_key}")


    def is_connected(self, device_key: DeviceKey) -> bool:
        with self._lock:
            if conn := self._connection_pool[device_key]:
                return True
        return False

    @abstractmethod
    def _create_client(self,device_id:int, connection_str: str) -> Any:
        pass

    @abstractmethod
    def _close_client(self,client, device_id: int, connection_str: str) -> Any:
        pass

    @abstractmethod
    def get_device_status(self,client,device_id:str,connection_str:str) -> DeviceStatus:
        pass

    def get_status(self, device_id: str, connection_str: str) -> DeviceStatus:
        my_device = DeviceKey(device_id=device_id, connection_str=connection_str)
        this_client = self._connection_pool[my_device]
        return self.get_device_status(this_client, device_id, connection_str)

    def excute_command(self,device_id:str,connection_str:str, command: str, params: Dict[str, Any],
                      mission_id: str):
        my_device = DeviceKey(device_id=device_id, connection_str=connection_str)
        this_client = self._connection_pool[my_device]
        with self.mission_context(mission_id):
            self.execute(this_client,device_id,connection_str,command,params)

    @abstractmethod
    def execute(self,client,device_id:int,connection_str:str, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行控制指令"""

    def to_json(self):
        """序列化设备信息"""
        actions = [item.dict() for item in self.get_action_list()]
        return json.dumps({
            "protocol": self.protocol_name,
            "action_list": actions
        }, ensure_ascii=False)