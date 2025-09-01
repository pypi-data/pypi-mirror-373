import asyncio
import json
import logging
import time
from typing import Callable, Dict
import grpc
import paho.mqtt.client as mqtt
from . import device_pb2
from . import device_pb2_grpc
from .model.device_key import DeviceKey

logger = logging.getLogger(__name__)


class DevicePusher:
    def __init__(self, device_factory: Callable[[], 'AbstractDevice']):
        self.device_factory = device_factory
        self.devices: Dict[DeviceKey, 'AbstractDevice'] = {}
        self.status_tasks: Dict[DeviceKey, asyncio.Task] = {}
        self.mqtt_client = None
        self.grpc_stub = None
        self.protocol_name = ""
        self.mqtt_connected = False

        # MQTT配置
        self.mqtt_broker = "192.168.1.174"
        self.mqtt_port = 1883
        self.mqtt_username = "admin"
        self.mqtt_password = "public"

    def on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT连接回调"""
        if rc == 0:
            self.mqtt_connected = True
            logger.info("MQTT connected successfully")
            # 订阅相关主题（如果需要接收命令）
            try:
                client.subscribe([
                    (f"devices/{self.protocol_name}/command", 1),
                    (f"devices/{self.protocol_name}/+/command", 1)
                ])
                logger.info("MQTT订阅成功")
            except Exception as e:
                logger.error(f"MQTT订阅失败: {e}")
        else:
            self.mqtt_connected = False
            error_messages = {
                1: "Connection Refused: incorrect protocol version",
                2: "Connection Refused: identifier rejected",
                3: "Connection Refused: server unavailable",
                4: "Connection Refused: bad username or password",
                5: "Connection Refused: not authorized"
            }
            error_msg = error_messages.get(rc, f"Unknown error code: {rc}")
            logger.error(f"MQTT连接失败: {error_msg}")

    def on_mqtt_disconnect(self, client, userdata, rc):
        """MQTT断开连接回调"""
        self.mqtt_connected = False
        disconnect_messages = {
            0: "正常断开",
            1: "意外断开: 传输层错误",
            2: "意外断开: 协议错误",
            3: "意外断开: 客户端主动断开",
            4: "意外断开: 网络错误",
            5: "意外断开: 被服务器断开",
            6: "意外断开: 保活超时",
            7: "意外断开: 会话被接管"
        }
        message = disconnect_messages.get(rc, f"未知断开原因: {rc}")
        logger.warning(f"MQTT连接断开: {message}")

    def on_mqtt_message(self, client, userdata, msg):
        """MQTT消息回调"""
        try:
            logger.debug(f"收到MQTT消息: {msg.topic}")
            # 这里可以处理接收到的MQTT命令
            payload = msg.payload.decode('utf-8')
            data = json.loads(payload)
            logger.debug(f"消息内容: {data}")
        except Exception as e:
            logger.error(f"处理MQTT消息错误: {e}")

    def on_mqtt_log(self, client, userdata, level, buf):
        """MQTT日志回调"""
        if level == mqtt.MQTT_LOG_DEBUG:
            logger.debug(f"MQTT: {buf}")
        elif level == mqtt.MQTT_LOG_INFO:
            logger.info(f"MQTT: {buf}")
        elif level == mqtt.MQTT_LOG_WARNING:
            logger.warning(f"MQTT: {buf}")
        elif level == mqtt.MQTT_LOG_ERR:
            logger.error(f"MQTT: {buf}")

    async def setup_mqtt(self):
        """设置MQTT连接"""
        max_retries = 3
        retry_count = 0

        # 检查配置是否完整
        if not self.mqtt_broker or not self.mqtt_port:
            logger.error("MQTT配置不完整，请先完成设备注册")
            return False

        while retry_count < max_retries:
            try:
                retry_count += 1
                logger.info(f"尝试连接MQTT (尝试 {retry_count}/{max_retries})")

                # 生成唯一的客户端ID - 使用UUID避免重复
                import uuid
                unique_id = str(uuid.uuid4())[:8]  # 取前8位
                client_id = f"{self.protocol_name}_{unique_id}"

                logger.info(f"使用客户端ID: {client_id}")

                self.mqtt_client = mqtt.Client(
                    client_id=client_id,  # 使用生成的唯一ID
                    protocol=mqtt.MQTTv311,
                    transport="tcp",
                    clean_session=True
                )

                # 设置回调
                self.mqtt_client.on_connect = self.on_mqtt_connect
                self.mqtt_client.on_message = self.on_mqtt_message
                self.mqtt_client.on_disconnect = self.on_mqtt_disconnect
                self.mqtt_client.on_log = self.on_mqtt_log

                # 设置认证信息（如果有）
                if self.mqtt_username and self.mqtt_password:
                    logger.info("使用用户名密码认证")
                    self.mqtt_client.username_pw_set(self.mqtt_username, self.mqtt_password)
                else:
                    logger.info("使用匿名连接")

                # 设置连接超时
                self.mqtt_client.connect_timeout = 10

                logger.info(f"连接到MQTT Broker: {self.mqtt_broker}:{self.mqtt_port}")

                # 连接Broker
                try:
                    result = self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)

                    if result != mqtt.MQTT_ERR_SUCCESS:
                        logger.error(f"MQTT连接失败: {mqtt.error_string(result)}")
                        if retry_count < max_retries:
                            await asyncio.sleep(2)
                            continue
                        return False
                except Exception as e:
                    logger.error(f"MQTT连接异常: {e}")
                    if retry_count < max_retries:
                        await asyncio.sleep(2)
                        continue
                    return False

                # 启动MQTT循环
                self.mqtt_client.loop_start()

                # 等待连接建立
                max_wait_time = 15
                wait_time = 0
                while not self.mqtt_connected and wait_time < max_wait_time:
                    await asyncio.sleep(0.5)
                    wait_time += 0.5

                if self.mqtt_connected:
                    logger.info(f"MQTT连接成功: {self.mqtt_broker}:{self.mqtt_port}")
                    return True
                else:
                    logger.error("MQTT连接超时")
                    try:
                        self.mqtt_client.loop_stop()
                        self.mqtt_client.disconnect()
                    except:
                        pass
                    if retry_count < max_retries:
                        await asyncio.sleep(3)
                        continue

            except Exception as e:
                logger.error(f"设置MQTT连接失败: {e}")
                if self.mqtt_client:
                    try:
                        self.mqtt_client.loop_stop()
                        self.mqtt_client.disconnect()
                    except:
                        pass
                if retry_count < max_retries:
                    await asyncio.sleep(2)
                    continue
                return False

        return False

    async def ensure_mqtt_connection(self):
        """确保MQTT连接正常"""
        if not self.mqtt_connected:
            logger.warning("MQTT连接断开，尝试重新连接...")
            return await self.setup_mqtt()
        return True
    async def _report_status_continuously(self, device: 'AbstractDevice', deviceKey: DeviceKey, report_interval=1):
        """通过MQTT持续上报设备状态"""
        """通过MQTT持续上报设备状态，状态为空时停止并清理"""
        drone_id = deviceKey.device_id
        connection_str = deviceKey.connection_str
        topic = f"devices/{drone_id}/{connection_str}/status"
        try:
            while True:
                if device.is_connected(deviceKey) and self.mqtt_connected:
                    # 确保MQTT连接正常
                    if not await self.ensure_mqtt_connection():
                        logger.warning("MQTT重连失败，等待后重试")
                        await asyncio.sleep(5)
                        continue
                    try:
                        status = device.get_status(drone_id, connection_str)

                        if not status:
                            logger.warning(f"设备 {deviceKey} 状态为空，停止上报并断开连接")
                            break

                        payload = json.dumps({
                            "status": status,
                            "timestamp": time.time(),
                            "drone_id": drone_id,
                            "connection_str": connection_str
                        })

                        # 发布消息并等待确认
                        result = self.mqtt_client.publish(topic, payload, qos=1)
                        if result.rc == mqtt.MQTT_ERR_SUCCESS:
                            logger.debug(f"状态上报成功: {topic}")
                        else:
                            logger.warning(f"状态上报失败: {mqtt.error_string(result.rc)}")

                    except Exception as e:
                        logger.warning(f"设备 {deviceKey} 状态上报失败: {e}")
                elif not self.mqtt_connected:
                    logger.warning("MQTT未连接，暂停状态上报")
                    await asyncio.sleep(5)  # MQTT断开时等待更长时间
                    continue

                await asyncio.sleep(report_interval)
        except asyncio.CancelledError:
            logger.info(f"设备 {deviceKey} 状态上报任务被取消")
        except Exception as e:
            logger.error(f"设备 {deviceKey} 状态上报任务异常: {e}")
        finally:
            # 清理逻辑：状态为空或任务结束时执行
            try:
                # 1. 清空MQTT话题数据（发送空消息）
                if self.mqtt_connected:
                    empty_payload = json.dumps({
                        "status": None,
                        "timestamp": time.time(),
                        "drone_id": drone_id,
                        "connection_str": connection_str,
                        "message": "device_disconnected"
                    })
                    result = self.mqtt_client.publish(topic, empty_payload, qos=1)
                    if result.rc == mqtt.MQTT_ERR_SUCCESS:
                        logger.info(f"已清空话题 {topic} 的数据")
                    else:
                        logger.warning(f"清空话题数据失败: {mqtt.error_string(result.rc)}")

                # 2. 断开设备连接
                if deviceKey in self.devices:
                    try:
                        device.disconnect(deviceKey)
                        logger.info(f"设备 {deviceKey} 已断开连接")
                    except Exception as e:
                        logger.error(f"断开设备 {deviceKey} 连接时出错: {e}")

                # 3. 从设备字典中移除
                if deviceKey in self.devices:
                    del self.devices[deviceKey]
                    logger.info(f"已从设备字典中移除 {deviceKey}")

                # 4. 取消并移除状态上报任务
                if deviceKey in self.status_tasks:
                    task = self.status_tasks[deviceKey]
                    if not task.done():
                        task.cancel()
                    del self.status_tasks[deviceKey]
                    logger.info(f"已取消并移除 {deviceKey} 的状态上报任务")

            except Exception as e:
                logger.error(f"清理设备 {deviceKey} 资源时出错: {e}")

    async def send_heartbeat(self):
        """通过MQTT发送心跳"""
        while True:
            try:
                if self.mqtt_connected:
                    topic = f"devices/{self.protocol_name}/heartbeat"
                    payload = json.dumps({
                        "protocol": self.protocol_name,
                        "timestamp": time.time(),
                        "status": "online"
                    })

                    result = self.mqtt_client.publish(topic, payload, qos=0)
                    if result.rc == mqtt.MQTT_ERR_SUCCESS:
                        logger.debug("心跳发送成功")
                    else:
                        logger.warning(f"心跳发送失败: {mqtt.error_string(result.rc)}")
                else:
                    logger.warning("MQTT未连接，无法发送心跳")
                    await asyncio.sleep(5)  # MQTT断开时等待更长时间
                    continue

                await asyncio.sleep(10)  # 10秒心跳间隔
            except Exception as e:
                logger.error(f"心跳发送失败: {e}")
                await asyncio.sleep(1)

    async def command_stream_handler(self):
        """处理gRPC命令流"""
        try:
            # 创建metadata包含protocol_name
            metadata = [('protocol_name', self.protocol_name)]

            # 创建双向流，携带metadata
            command_stream = self.grpc_stub.CommandStream(metadata=metadata)

            async for command_request in command_stream:
                try:
                    logger.info(f"收到命令请求: {command_request}")
                    # 处理命令
                    mission_id = command_request.mission_id
                    selected_devices = json.loads(command_request.params)
                    result = ""

                    for selected_device in selected_devices:
                        # 解析参数
                        device_id = selected_device['device_id']
                        connection_str = selected_device['connection_str']
                        actions = selected_device['actions']
                        deviceKey = DeviceKey(device_id=device_id, connection_str=connection_str)
                        if mission_id == 'connect':
                            # 获取或创建设备实例
                            if deviceKey not in self.devices:
                                logger.info(f"创建新设备实例: {deviceKey}")
                                device = self.device_factory()
                                self.devices[deviceKey] = device
                                result = "创建连接成功"
                                # 连接设备
                                try:
                                    device.connect(deviceKey)
                                    if deviceKey not in self.status_tasks:
                                        self.status_tasks[deviceKey] = asyncio.create_task(
                                            self._report_status_continuously(device, deviceKey))
                                        logger.info(f"为设备 {deviceKey} 启动状态上报任务")
                                except Exception as e:
                                    result = "创建连接失败"
                                    raise ValueError(f"设备连接失败: {e}")
                        else:
                            for action in actions:
                                command_type = action['name']
                                params = action['parameters']
                                # 获取或创建设备实例
                                if deviceKey not in self.devices:
                                    logger.info(f"创建新设备实例: {deviceKey}")
                                    device = self.device_factory()
                                    device.set_grpc_stub(self.grpc_stub)
                                    self.devices[deviceKey] = device
                                    # 连接设备
                                    try:
                                        device.connect(deviceKey)
                                        if deviceKey not in self.status_tasks:
                                            self.status_tasks[deviceKey] = asyncio.create_task(
                                                self._report_status_continuously(device, deviceKey))
                                            logger.info(f"为设备 {deviceKey} 启动状态上报任务")
                                    except Exception as e:
                                        raise ValueError(f"设备连接失败: {e}")

                                device = self.devices[deviceKey]
                                # 执行命令
                                try:
                                    result = device.excute_command(device_id, connection_str, command_type, params, mission_id)
                                except Exception as e:
                                    raise ValueError(f"命令执行失败: {e}")

                    # 发送成功确认
                    ack = device_pb2.CommandAck(
                        command_id=command_request.command_id,
                        mission_id=mission_id,
                        success=True,
                        data=json.dumps(result) if result else ""
                    )
                    await command_stream.write(ack)
                    logger.info(f"命令执行成功: {command_request.command_id}")

                except Exception as e:
                    logger.error(f"处理命令失败: {e}")
                    # 发送错误确认
                    ack = device_pb2.CommandAck(
                        command_id=command_request.command_id if command_request else "unknown",
                        success=False,
                        message=str(e)
                    )
                    await command_stream.write(ack)


        except grpc.aio.AioRpcError as e:
            logger.error(f"gRPC命令流错误: {e}")
            raise
        except Exception as e:
            logger.error(f"命令流处理异常: {e}")
            raise

    def _update_all_devices_grpc_stub(self):
        """更新所有设备实例的grpc_stub"""
        for device_key, device in self.devices.items():
            try:
                device.set_grpc_stub(self.grpc_stub)
                logger.info(f"已更新设备 {device_key} 的grpc_stub")
            except Exception as e:
                logger.error(f"更新设备 {device_key} 的grpc_stub失败: {e}")
    async def connect_server(self, grpc_server_url: str,type_description:str):
        """连接到gRPC服务器并注册设备"""
        delay = 1

        while True:
            try:
                # 创建gRPC通道
                async with grpc.aio.insecure_channel(grpc_server_url) as channel:
                    self.grpc_stub = device_pb2_grpc.DeviceServiceStub(channel)
                    # 更新所有已存在设备的grpc_stub
                    self._update_all_devices_grpc_stub()
                    # 注册设备
                    device = self.device_factory()
                    self.protocol_name = device.protocol_name
                    register_request = device_pb2.RegisterRequest(
                        protocol_name=self.protocol_name,
                        auth_token="your_auth_token",  # 需要实现认证
                        capabilities=device.to_json(),
                        type_description=type_description
                    )

                    response = await self.grpc_stub.Register(register_request)

                    if response.success:
                        logger.info(f"设备注册成功: {response.message}")

                        # 如果服务器返回了MQTT配置，使用服务器的配置
                        if hasattr(response, 'mqtt_broker_url') and response.mqtt_broker_url:
                            self.mqtt_broker = response.mqtt_broker_url
                        if hasattr(response, 'mqtt_broker_port') and response.mqtt_broker_port:
                            self.mqtt_broker_port = response.mqtt_broker_port
                        if hasattr(response, 'mqtt_username') and response.mqtt_username:
                            self.mqtt_username = response.mqtt_username
                        if hasattr(response, 'mqtt_password') and response.mqtt_password:
                            self.mqtt_password = response.mqtt_password

                        # 配置MQTT
                        mqtt_success = await self.setup_mqtt()
                        if not mqtt_success:
                            logger.error("MQTT连接失败，继续尝试gRPC连接")
                            await asyncio.sleep(delay)
                            delay = min(delay * 2, 30)
                            continue

                        # 启动心跳任务
                        heartbeat_task = asyncio.create_task(self.send_heartbeat())

                        # 启动命令流处理
                        await self.command_stream_handler()

                    else:
                        logger.error(f"设备注册失败: {response.message}")
                        await asyncio.sleep(delay)
                        delay = min(delay * 2, 30)

            except Exception as e:
                logger.warning(f"gRPC连接失败，{delay}s后重试: {e}")
                await asyncio.sleep(delay)
                delay = min(delay * 2, 30)

    async def cleanup(self):
        """清理资源"""
        # 首先取消所有状态上报任务
        for deviceKey, task in list(self.status_tasks.items()):
            if not task.done():
                task.cancel()
            try:
                await task  # 等待任务完成清理
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"取消任务 {deviceKey} 时出错: {e}")

        # 断开所有设备连接
        for deviceKey, device in list(self.devices.items()):
            try:
                device.disconnect(deviceKey)
                logger.info(f"设备 {deviceKey} 已断开连接")
            except Exception as e:
                logger.error(f"断开设备 {deviceKey} 连接时出错: {e}")

        # 清空设备字典和任务字典
        self.devices.clear()
        self.status_tasks.clear()

        # 关闭MQTT连接
        if self.mqtt_client:
            try:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
                logger.info("MQTT连接已关闭")
            except Exception as e:
                logger.error(f"关闭MQTT连接时出错: {e}")

        # 取消其他任务
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)