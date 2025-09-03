"""
App Store Connect MCP Server 实现
"""

import os
import requests
from typing import List, Dict, Any, Optional

from .models import AppStoreConnectConfig
from .appstore_client import AppStoreConnectClient
from ..base_mcp_server import BaseMCPServer


class AppStoreConnectMCPServer(BaseMCPServer):
    """App Store Connect MCP Server 类"""

    def __init__(self, name: str = "App Store Connect Server"):
        """初始化 MCP Server

        Args:
            name: MCP Server 名称
        """
        # 从环境变量加载配置
        config = self._load_config_from_env()

        # 初始化App Store Connect客户端
        self.client = AppStoreConnectClient(config=config)

        # 调用基础类构造函数，使用sse传输协议
        super().__init__(name, transport="sse")

    def _load_config_from_env(self) -> Optional[AppStoreConnectConfig]:
        """从环境变量加载App Store Connect配置

        Returns:
            AppStoreConnectConfig 或 None（如果环境变量不完整）
        """
        key_id = os.getenv('APPSTORE_KEY_ID')
        issuer_id = os.getenv('APPSTORE_ISSUER_ID')
        private_key = os.getenv('APPSTORE_PRIVATE_KEY')
        app_id = os.getenv('APPSTORE_APP_ID')  # 可选

        # 检查必需的环境变量
        if not all([key_id, issuer_id, private_key]):
            return None

        return AppStoreConnectConfig(
            key_id=key_id,
            issuer_id=issuer_id,
            private_key=private_key,
            app_id=app_id
        )

    def _register_tools(self):
        """注册所有工具"""

        @self.mcp.tool()
        def configure_appstore_connect(key_id: str, issuer_id: str, private_key: str, app_id: str = None) -> str:
            """配置 App Store Connect API 凭据

            Args:
                key_id: API Key ID
                issuer_id: Issuer ID
                private_key: 私钥内容(PEM格式)
                app_id: 应用ID(可选)
            """
            config = AppStoreConnectConfig(
                key_id=key_id,
                issuer_id=issuer_id,
                private_key=private_key,
                app_id=app_id
            )
            self.client.set_config(config)
            return "App Store Connect 配置已成功设置"

        @self.mcp.tool()
        def list_team_members() -> List[Dict[str, Any]]:
            """获取团队成员列表"""
            return self.client.get_team_members()

        @self.mcp.tool()
        def invite_team_member(email: str, first_name: str, last_name: str, roles: List[str], provisioning_allowed: bool = False) -> str:
            """邀请新的团队成员

            Args:
                email: 成员邮箱
                first_name: 名字
                last_name: 姓氏
                roles: 角色列表 (如: ['DEVELOPER', 'ADMIN'])
                provisioning_allowed: 是否允许配置文件管理
            """
            self.client.invite_team_member(email, first_name, last_name, roles, provisioning_allowed)
            return f"成功邀请 {email} 加入团队"

        @self.mcp.tool()
        def remove_team_member(user_id: str) -> str:
            """移除团队成员

            Args:
                user_id: 用户ID
            """
            self.client.remove_team_member(user_id)
            return f"成功移除用户 {user_id}"

        @self.mcp.tool()
        def list_apps() -> List[Dict[str, Any]]:
            """获取应用列表"""
            return self.client.get_apps()

        @self.mcp.tool()
        def create_testflight_group(app_id: str, group_name: str, is_internal: bool = True, public_link_enabled: bool = False) -> str:
            """创建 TestFlight 测试组

            Args:
                app_id: 应用ID
                group_name: 测试组名称
                is_internal: 是否为内部测试组
                public_link_enabled: 是否启用公共链接
            """
            self.client.create_beta_group(app_id, group_name, is_internal, public_link_enabled)
            return f"成功创建测试组: {group_name}"

        @self.mcp.tool()
        def list_testflight_groups(app_id: str = None) -> List[Dict[str, Any]]:
            """获取 TestFlight 测试组列表

            Args:
                app_id: 应用ID(可选，如果不提供则显示所有应用的测试组)
            """
            return self.client.get_beta_groups(app_id)

        @self.mcp.tool()
        def add_tester_to_group(group_id: str, tester_email: str, first_name: str = None, last_name: str = None) -> str:
            """将测试者添加到 TestFlight 测试组

            Args:
                group_id: 测试组ID
                tester_email: 测试者邮箱
                first_name: 测试者名字(可选)
                last_name: 测试者姓氏(可选)
            """
            # 首先尝试创建测试者(如果不存在)
            try:
                tester_result = self.client.create_beta_tester(tester_email, first_name, last_name)
                tester_id = tester_result['data']['id']
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 409:  # 测试者已存在
                    existing_tester = self.client.find_beta_tester_by_email(tester_email)
                    if existing_tester:
                        tester_id = existing_tester['id']
                    else:
                        return f"无法找到测试者: {tester_email}"
                else:
                    raise

            # 将测试者添加到组
            self.client.add_tester_to_group(group_id, tester_id)
            return f"成功将 {tester_email} 添加到测试组"

        @self.mcp.tool()
        def remove_tester_from_group(group_id: str, tester_id: str) -> str:
            """从 TestFlight 测试组移除测试者

            Args:
                group_id: 测试组ID
                tester_id: 测试者ID
            """
            self.client.remove_tester_from_group(group_id, tester_id)
            return f"成功从测试组移除测试者"

    def _register_resources(self):
        """注册所有资源"""

        @self.mcp.resource("appstore://apps")
        def get_apps_resource() -> str:
            """获取应用列表资源"""
            if not self.client.config:
                return "请先配置 App Store Connect 凭据或设置环境变量 (APPSTORE_KEY_ID, APPSTORE_ISSUER_ID, APPSTORE_PRIVATE_KEY)"

            try:
                apps = self.client.get_apps()
                return f"找到 {len(apps)} 个应用:\n" + "\n".join([f"- {app['name']} ({app['bundle_id']})" for app in apps])
            except Exception as e:
                return f"获取应用列表失败: {str(e)}"

        @self.mcp.resource("appstore://members")
        def get_team_members_resource() -> str:
            """获取团队成员资源"""
            if not self.client.config:
                return "请先配置 App Store Connect 凭据或设置环境变量 (APPSTORE_KEY_ID, APPSTORE_ISSUER_ID, APPSTORE_PRIVATE_KEY)"

            try:
                members = self.client.get_team_members()
                return f"团队共有 {len(members)} 名成员:\n" + "\n".join([f"- {m['email']} ({', '.join(m['roles'])})" for m in members])
            except Exception as e:
                return f"获取团队成员失败: {str(e)}"

    def _register_prompts(self):
        """注册所有提示"""

        @self.mcp.prompt()
        def manage_testflight_prompt(action: str, app_name: str = "", group_name: str = "", tester_email: str = "") -> str:
            """生成 TestFlight 管理提示

            Args:
                action: 操作类型 (create_group, add_tester, remove_tester)
                app_name: 应用名称
                group_name: 测试组名称
                tester_email: 测试者邮箱
            """
            prompts = {
                "create_group": f"请为应用 '{app_name}' 创建一个名为 '{group_name}' 的 TestFlight 测试组",
                "add_tester": f"请将测试者 '{tester_email}' 添加到 '{group_name}' 测试组",
                "remove_tester": f"请从 '{group_name}' 测试组中移除测试者 '{tester_email}'"
            }

            return prompts.get(action, "请选择有效的 TestFlight 管理操作")


    def get_client(self) -> AppStoreConnectClient:
        """获取 App Store Connect 客户端

        Returns:
            AppStoreConnectClient: API 客户端实例
        """
        return self.client
