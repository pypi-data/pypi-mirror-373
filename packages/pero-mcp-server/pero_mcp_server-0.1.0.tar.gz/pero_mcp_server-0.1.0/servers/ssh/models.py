"""
SSH连接配置模型
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SSHConfig:
    """SSH连接配置"""
    hostname: str
    username: str
    port: int = 22
    password: Optional[str] = None
    private_key_path: Optional[str] = None
    private_key_content: Optional[str] = None
    timeout: int = 30

    def __post_init__(self):
        """验证配置"""
        if not self.password and not self.private_key_path and not self.private_key_content:
            raise ValueError("必须提供密码或私钥之一")
