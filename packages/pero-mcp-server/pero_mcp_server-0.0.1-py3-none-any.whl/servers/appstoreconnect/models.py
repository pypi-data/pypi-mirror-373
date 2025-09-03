"""
数据模型定义
"""

from typing import List, Optional
from pydantic import BaseModel


class AppStoreConnectConfig(BaseModel):
    """App Store Connect API 配置"""
    key_id: str
    issuer_id: str
    private_key: str
    app_id: Optional[str] = None


class TeamMember(BaseModel):
    """团队成员模型"""
    id: str
    email: str
    first_name: str
    last_name: str
    roles: List[str]
    provisioning_allowed: bool


class TestFlightGroup(BaseModel):
    """TestFlight 测试组模型"""
    id: str
    name: str
    is_internal_group: bool
    public_link_enabled: bool
    public_link_limit: Optional[int] = None


class App(BaseModel):
    """应用模型"""
    id: str
    name: str
    bundle_id: str
    sku: str
    primary_locale: str


class BetaTester(BaseModel):
    """Beta 测试者模型"""
    id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
