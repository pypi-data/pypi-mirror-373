"""
SSH客户端实现
"""

import paramiko
import io
from typing import Dict, Any, Optional, List

from .models import SSHConfig


class SSHClient:
    """SSH客户端类"""

    def __init__(self, config: Optional[SSHConfig] = None):
        """初始化SSH客户端

        Args:
            config: SSH连接配置
        """
        self.config = config
        self.client = None
        self.is_connected = False

    def set_config(self, config: SSHConfig):
        """设置SSH配置

        Args:
            config: SSH连接配置
        """
        self.config = config
        if self.is_connected:
            self.disconnect()

    def connect(self) -> str:
        """建立SSH连接

        Returns:
            str: 连接状态信息
        """
        if not self.config:
            raise ValueError("SSH配置未设置")

        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # 准备连接参数
            connect_kwargs = {
                'hostname': self.config.hostname,
                'username': self.config.username,
                'port': self.config.port,
                'timeout': self.config.timeout
            }

            # 使用密码或密钥认证
            if self.config.password:
                connect_kwargs['password'] = self.config.password
            elif self.config.private_key_content:
                # 从字符串内容创建私钥
                key_file = io.StringIO(self.config.private_key_content)
                try:
                    # 尝试不同的私钥类型
                    private_key = paramiko.RSAKey.from_private_key(key_file)
                except paramiko.PasswordRequiredException:
                    raise Exception("私钥需要密码，请提供密码")
                except Exception:
                    # 如果RSA失败，尝试其他类型
                    key_file.seek(0)
                    try:
                        private_key = paramiko.Ed25519Key.from_private_key(key_file)
                    except Exception:
                        key_file.seek(0)
                        try:
                            private_key = paramiko.ECDSAKey.from_private_key(key_file)
                        except Exception:
                            key_file.seek(0)
                            private_key = paramiko.DSSKey.from_private_key(key_file)
                connect_kwargs['pkey'] = private_key
            elif self.config.private_key_path:
                # 从文件路径加载私钥
                private_key = paramiko.RSAKey.from_private_key_file(self.config.private_key_path)
                connect_kwargs['pkey'] = private_key

            self.client.connect(**connect_kwargs)
            self.is_connected = True
            return f"成功连接到 {self.config.username}@{self.config.hostname}:{self.config.port}"

        except Exception as e:
            self.is_connected = False
            raise Exception(f"SSH连接失败: {str(e)}")

    def disconnect(self):
        """断开SSH连接"""
        if self.client:
            self.client.close()
            self.is_connected = False

    def execute_command(self, command: str) -> Dict[str, Any]:
        """执行SSH命令

        Args:
            command: 要执行的命令

        Returns:
            Dict[str, Any]: 包含命令执行结果的字典
        """
        if not self.is_connected:
            self.connect()

        try:
            stdin, stdout, stderr = self.client.exec_command(command)

            # 读取输出
            stdout_content = stdout.read().decode('utf-8')
            stderr_content = stderr.read().decode('utf-8')
            exit_status = stdout.channel.recv_exit_status()

            return {
                'command': command,
                'stdout': stdout_content,
                'stderr': stderr_content,
                'exit_status': exit_status,
                'success': exit_status == 0
            }

        except Exception as e:
            return {
                'command': command,
                'stdout': '',
                'stderr': str(e),
                'exit_status': -1,
                'success': False
            }

    def list_directory(self, path: str = '.') -> List[Dict[str, Any]]:
        """列出目录内容

        Args:
            path: 目录路径

        Returns:
            List[Dict[str, Any]]: 目录内容列表
        """
        result = self.execute_command(f'ls -la "{path}"')
        if not result['success']:
            raise Exception(f"列出目录失败: {result['stderr']}")

        files = []
        lines = result['stdout'].strip().split('\n')[1:]  # 跳过第一行总计信息

        for line in lines:
            if not line.strip():
                continue

            parts = line.split(None, 8)
            if len(parts) >= 9:
                files.append({
                    'permissions': parts[0],
                    'links': parts[1],
                    'owner': parts[2],
                    'group': parts[3],
                    'size': parts[4],
                    'month': parts[5],
                    'day': parts[6],
                    'time_or_year': parts[7],
                    'name': parts[8],
                    'is_directory': parts[0].startswith('d')
                })

        return files

    def upload_file(self, local_path: str, remote_path: str) -> str:
        """上传文件

        Args:
            local_path: 本地文件路径
            remote_path: 远程文件路径

        Returns:
            str: 上传结果信息
        """
        if not self.is_connected:
            self.connect()

        try:
            sftp = self.client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            return f"成功上传 {local_path} 到 {remote_path}"
        except Exception as e:
            raise Exception(f"文件上传失败: {str(e)}")

    def download_file(self, remote_path: str, local_path: str) -> str:
        """下载文件

        Args:
            remote_path: 远程文件路径
            local_path: 本地文件路径

        Returns:
            str: 下载结果信息
        """
        if not self.is_connected:
            self.connect()

        try:
            sftp = self.client.open_sftp()
            sftp.get(remote_path, local_path)
            sftp.close()
            return f"成功下载 {remote_path} 到 {local_path}"
        except Exception as e:
            raise Exception(f"文件下载失败: {str(e)}")

    def get_system_info(self) -> Dict[str, str]:
        """获取系统信息

        Returns:
            Dict[str, str]: 系统信息
        """
        commands = {
            'hostname': 'hostname',
            'os': 'uname -s',
            'kernel': 'uname -r',
            'architecture': 'uname -m',
            'uptime': 'uptime',
            'disk_usage': 'df -h /',
            'memory': 'free -h'
        }

        info = {}
        for key, command in commands.items():
            result = self.execute_command(command)
            if result['success']:
                info[key] = result['stdout'].strip()
            else:
                info[key] = f"获取失败: {result['stderr']}"

        return info
