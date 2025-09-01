# action_item.py
from dataclasses import dataclass, asdict
from typing import Dict, Any
@dataclass
class ActionItem:
    name: str  # 动作名称
    command_type: str  # 动作唯一标识
    description: str  # 描述
    params: Dict[str, Any]  # JSON Schema 或简单 dict 描述

    def dict(self) -> Dict[str, Any]:
        return asdict(self)