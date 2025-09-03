"""
基础 MCP Server 类
提供公共的服务器功能和配置
"""

from abc import ABC, abstractmethod
from mcp.server.fastmcp import FastMCP

class BaseMCPServer(ABC):
    """MCP Server 基础类"""

    def __init__(self, name: str, transport: str = "streamable-http"):
        """初始化基础 MCP Server

        Args:
            name: MCP Server 名称
            transport: 传输协议类型 (默认: streamable-http)
        """
        self.mcp = FastMCP(name)
        self.transport = transport

        # 子类需要实现这些方法
        self._register_tools()
        self._register_resources()
        self._register_prompts()

    @abstractmethod
    def _register_tools(self):
        """注册所有工具 - 子类必须实现"""
        pass

    @abstractmethod
    def _register_resources(self):
        """注册所有资源 - 子类必须实现"""
        pass

    @abstractmethod
    def _register_prompts(self):
        """注册所有提示 - 子类必须实现"""
        pass


    def run(self, host: str = "0.0.0.0", transport: str = None):
        """启动 MCP Server

        Args:
            host: 服务器主机地址 (默认: 0.0.0.0)
            transport: 传输协议 (可选，如果不提供则使用初始化时的协议)
        """
        self.mcp.settings.host = host
        transport_to_use = transport or self.transport
        self.mcp.run(transport=transport_to_use)
