from setuptools import setup, find_packages
from pathlib import Path

# 使用 UTF-8 编码读取 README.md
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8")

setup(
    name="device-protocol-sdk",
    version="1.0.7",
    packages=find_packages(include=["device_protocol_sdk*", "device_protocol_sdk*"]),
    install_requires=[
        "websockets>=10.0",
        "pydantic>=1.9.0",
    ],
    python_requires=">=3.8",
    author="Your Name",
    description="无人机设备协议开发SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",  # 确保 PyPI 正确渲染 Markdown
)