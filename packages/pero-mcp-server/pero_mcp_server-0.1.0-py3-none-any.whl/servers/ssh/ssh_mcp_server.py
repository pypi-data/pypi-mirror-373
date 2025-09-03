"""
SSH MCP Server 实现
"""

import os
from typing import List, Dict, Any, Optional

from .models import SSHConfig
from .ssh_client import SSHClient
from ..base_mcp_server import BaseMCPServer


class SSHMCPServer(BaseMCPServer):
    """SSH MCP Server 类"""

    def __init__(self, name: str = "SSH Server"):
        """初始化 MCP Server

        Args:
            name: MCP Server 名称
        """
        self.client = SSHClient()

        # 从环境变量加载配置
        config = self._load_config_from_env()
        if config:
            self.client.set_config(config)

        # 调用基础类构造函数，使用streamable-http传输协议
        super().__init__(name, transport="streamable-http")

    def _load_config_from_env(self) -> Optional[SSHConfig]:
        """从环境变量加载SSH配置

        Returns:
            SSHConfig 或 None（如果环境变量不完整）
        """
        hostname = os.getenv('SSH_HOSTNAME')
        username = os.getenv('SSH_USERNAME')
        port = int(os.getenv('SSH_PORT', '22'))
        password = os.getenv('SSH_PASSWORD')
        private_key_path = os.getenv('SSH_PRIVATE_KEY_PATH')
        private_key_content = os.getenv('SSH_PRIVATE_KEY_CONTENT')
        timeout = int(os.getenv('SSH_TIMEOUT', '30'))

        # 检查必需的环境变量
        if not all([hostname, username]):
            return None

        # 验证至少有一种认证方式
        if not any([password, private_key_path, private_key_content]):
            return None

        try:
            return SSHConfig(
                hostname=hostname,
                username=username,
                port=port,
                password=password,
                private_key_path=private_key_path,
                private_key_content=private_key_content,
                timeout=timeout
            )
        except ValueError:
            # 如果配置验证失败，返回None
            return None

    def _register_tools(self):
        """注册所有工具"""

        @self.mcp.tool()
        def configure_ssh(hostname: str, username: str, port: int = 22, password: Optional[str] = None,
                         private_key_path: Optional[str] = None, private_key_content: Optional[str] = None,
                         timeout: int = 30) -> str:
            """配置SSH连接信息

            Args:
                hostname: 服务器主机名或IP地址
                username: 用户名
                port: SSH端口(默认22)
                password: 密码(可选)
                private_key_path: 私钥文件路径(可选)
                private_key_content: 私钥内容(可选)
                timeout: 连接超时时间(秒)
            """
            config = SSHConfig(
                hostname=hostname,
                username=username,
                port=port,
                password=password,
                private_key_path=private_key_path,
                private_key_content=private_key_content,
                timeout=timeout
            )
            self.client.set_config(config)
            return f"SSH配置已成功设置: {username}@{hostname}:{port}"

        @self.mcp.tool()
        def connect_ssh() -> str:
            """建立SSH连接"""
            return self.client.connect()

        @self.mcp.tool()
        def disconnect_ssh() -> str:
            """断开SSH连接"""
            self.client.disconnect()
            return "SSH连接已断开"

        @self.mcp.tool()
        def execute_command(command: str) -> Dict[str, Any]:
            """执行SSH命令

            Args:
                command: 要执行的命令
            """
            return self.client.execute_command(command)

        @self.mcp.tool()
        def list_directory(path: str = '.') -> List[Dict[str, Any]]:
            """列出目录内容

            Args:
                path: 目录路径(默认当前目录)
            """
            return self.client.list_directory(path)

        @self.mcp.tool()
        def upload_file(local_path: str, remote_path: str) -> str:
            """上传文件到远程服务器

            Args:
                local_path: 本地文件路径
                remote_path: 远程文件路径
            """
            return self.client.upload_file(local_path, remote_path)

        @self.mcp.tool()
        def download_file(remote_path: str, local_path: str) -> str:
            """从远程服务器下载文件

            Args:
                remote_path: 远程文件路径
                local_path: 本地文件路径
            """
            return self.client.download_file(remote_path, local_path)

        @self.mcp.tool()
        def get_system_info() -> Dict[str, str]:
            """获取远程系统信息"""
            return self.client.get_system_info()

        @self.mcp.tool()
        def create_directory(path: str) -> Dict[str, Any]:
            """创建目录

            Args:
                path: 要创建的目录路径
            """
            return self.client.execute_command(f'mkdir -p "{path}"')

        @self.mcp.tool()
        def remove_file_or_directory(path: str, recursive: bool = False) -> Dict[str, Any]:
            """删除文件或目录

            Args:
                path: 要删除的文件或目录路径
                recursive: 是否递归删除(用于目录)
            """
            command = f'rm -r "{path}"' if recursive else f'rm "{path}"'
            return self.client.execute_command(command)

        @self.mcp.tool()
        def check_file_exists(path: str) -> Dict[str, Any]:
            """检查文件或目录是否存在

            Args:
                path: 文件或目录路径
            """
            result = self.client.execute_command(f'test -e "{path}" && echo "exists" || echo "not found"')
            result['exists'] = result['stdout'].strip() == 'exists'
            return result

        @self.mcp.tool()
        def get_file_content(path: str, lines: int = None) -> Dict[str, Any]:
            """获取文件内容

            Args:
                path: 文件路径
                lines: 限制显示的行数(可选)
            """
            if lines:
                command = f'head -n {lines} "{path}"'
            else:
                command = f'cat "{path}"'
            return self.client.execute_command(command)

        @self.mcp.tool()
        def search_files(pattern: str, path: str = '.', case_sensitive: bool = True) -> Dict[str, Any]:
            """搜索文件

            Args:
                pattern: 搜索模式
                path: 搜索路径(默认当前目录)
                case_sensitive: 是否区分大小写
            """
            find_cmd = 'find' if case_sensitive else 'find'
            name_flag = '-name' if case_sensitive else '-iname'
            command = f'{find_cmd} "{path}" {name_flag} "{pattern}"'
            return self.client.execute_command(command)

        @self.mcp.tool()
        def get_process_list() -> Dict[str, Any]:
            """获取进程列表"""
            return self.client.execute_command('ps aux')

        @self.mcp.tool()
        def kill_process(pid: int, force: bool = False) -> Dict[str, Any]:
            """杀死进程

            Args:
                pid: 进程ID
                force: 是否强制杀死进程
            """
            signal = '-9' if force else '-15'
            return self.client.execute_command(f'kill {signal} {pid}')

    def _register_resources(self):
        """注册所有资源"""

        @self.mcp.resource("ssh://system-info")
        def get_system_info_resource() -> str:
            """获取系统信息资源"""
            if not self.client.config:
                return "请先配置SSH连接信息或设置环境变量 (SSH_HOSTNAME, SSH_USERNAME, SSH_PASSWORD/SSH_PRIVATE_KEY_PATH/SSH_PRIVATE_KEY_CONTENT)"

            try:
                info = self.client.get_system_info()
                result = "系统信息:\n"
                for key, value in info.items():
                    result += f"- {key.title()}: {value}\n"
                return result
            except Exception as e:
                return f"获取系统信息失败: {str(e)}"

        @self.mcp.resource("ssh://directory")
        def get_current_directory_resource() -> str:
            """获取当前目录内容资源"""
            if not self.client.config:
                return "请先配置SSH连接信息或设置环境变量 (SSH_HOSTNAME, SSH_USERNAME, SSH_PASSWORD/SSH_PRIVATE_KEY_PATH/SSH_PRIVATE_KEY_CONTENT)"

            try:
                files = self.client.list_directory('.')
                result = "当前目录内容:\n"
                for file_info in files:
                    file_type = "目录" if file_info['is_directory'] else "文件"
                    result += f"- {file_info['name']} ({file_type}, {file_info['size']} bytes)\n"
                return result
            except Exception as e:
                return f"获取目录内容失败: {str(e)}"

        @self.mcp.resource("ssh://connection-status")
        def get_connection_status_resource() -> str:
            """获取连接状态资源"""
            if not self.client.config:
                return "SSH未配置，请设置环境变量 (SSH_HOSTNAME, SSH_USERNAME, SSH_PASSWORD/SSH_PRIVATE_KEY_PATH/SSH_PRIVATE_KEY_CONTENT)"

            status = "已连接" if self.client.is_connected else "未连接"
            return f"SSH连接状态: {status}\n服务器: {self.client.config.hostname}\n用户: {self.client.config.username}"

    def _register_prompts(self):
        """注册所有提示"""

        @self.mcp.prompt()
        def ssh_management_prompt(action: str, target: str = "", command: str = "") -> str:
            """生成SSH管理提示

            Args:
                action: 操作类型 (connect, execute, upload, download, info)
                target: 目标(文件路径、命令等)
                command: 要执行的命令
            """
            prompts = {
                "connect": "请建立SSH连接到远程服务器",
                "execute": f"请执行命令: {command}",
                "upload": f"请上传文件到远程服务器: {target}",
                "download": f"请从远程服务器下载文件: {target}",
                "info": "请获取远程系统信息",
                "list": f"请列出目录内容: {target or '当前目录'}"
            }

            return prompts.get(action, "请选择有效的SSH管理操作")

        @self.mcp.prompt()
        def file_management_prompt(operation: str, path: str = "", content: str = "") -> str:
            """生成文件管理提示

            Args:
                operation: 操作类型 (create, delete, read, search)
                path: 文件或目录路径
                content: 文件内容或搜索模式
            """
            prompts = {
                "create": f"请创建文件或目录: {path}",
                "delete": f"请删除文件或目录: {path}",
                "read": f"请读取文件内容: {path}",
                "search": f"请在 {path or '当前目录'} 中搜索: {content}"
            }

            return prompts.get(operation, "请选择有效的文件管理操作")

    def get_client(self) -> SSHClient:
        """获取SSH客户端

        Returns:
            SSHClient: SSH客户端实例
        """
        return self.client
