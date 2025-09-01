from setuptools import setup, find_packages
from pathlib import Path

# 使用 UTF-8 编码读取 README.md
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8")

setup(
    name="device-protocol-sdk",
    version="1.0.8",
    packages=find_packages(include=["device_protocol_sdk*", "device_protocol_sdk*"]),
    install_requires=[
        "grpcio>=1.48.2",  # gRPC 运行时依赖
        "grpcio-tools>=1.48.2",  # gRPC 工具，用于生成 Protobuf 文件
        "paho-mqtt>=1.6.1",  # MQTT 客户端
        "pydantic>=1.9.0",  # 数据验证和设置管理
        "websockets>=10.0",  # Websocket 支持
    ],
    python_requires=">=3.8",
    author="Your Name",
    description="无人机设备协议开发SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",  # 确保 PyPI 正确渲染 Markdown
)