"""
MCP Server 启动脚本
"""

import threading
import time
from typing import Any

from servers.appstoreconnect import AppStoreConnectMCPServer
from servers.ssh import SSHMCPServer


# 服务器配置，包含类和端口信息，从8000开始
SERVER_CONFIGS = {
    'ssh': {
        'class': SSHMCPServer,
        'port': 8000
    },
    'appstore': {
        'class': AppStoreConnectMCPServer,
        'port': 8001
    }
}

class MultiServerManager:
    """多服务器管理器"""

    def __init__(self):
        self.servers = {}
        self.server_threads = {}

    def create_server(self, server_type: str, port: int) -> Any:
        """创建服务器实例（延迟配置）"""
        server_class = SERVER_CONFIGS[server_type]['class']
        # 创建不带配置的服务器实例，配置将在客户端连接时提供
        server = server_class()
        return server

    def start_server(self, server_type: str, server: Any, port: int):
        """在指定端口启动服务器"""
        def run_server():
            try:
                print(f"正在启动 {server_type} MCP Server on port {port}...")
                # 修改run方法以支持端口参数
                if hasattr(server, 'run_with_port'):
                    server.run_with_port(port=port)
                else:
                    # 临时修改FastMCP的端口设置
                    server.mcp.settings.port = port
                    server.run()
            except Exception as e:
                print(f"启动 {server_type} 服务器失败: {e}")

        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        self.server_threads[server_type] = thread
        return thread

    def start_all_servers(self):
        """启动所有服务器"""
        print("正在启动所有MCP服务器...")
        print("服务器配置:")
        for server_type, config in SERVER_CONFIGS.items():
            print(f"  {server_type}: {config['class'].__name__} on port {config['port']}")

        for server_type, config in SERVER_CONFIGS.items():
            server = self.create_server(server_type, config['port'])
            self.servers[server_type] = server
            self.start_server(server_type, server, config['port'])

        print("所有服务器启动完成!")
        print("客户端可以连接到以下端口:")
        for server_type, config in SERVER_CONFIGS.items():
            print(f"  {server_type}: http://localhost:{config['port']}")

        return self.servers

def main():
    """启动所有MCP Servers"""
    # 启动所有服务器
    manager = MultiServerManager()
    servers = manager.start_all_servers()

    try:
        # 保持主程序运行
        print("服务器正在运行中... 按 Ctrl+C 退出")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在关闭所有服务器...")

if __name__ == '__main__':
    main()
