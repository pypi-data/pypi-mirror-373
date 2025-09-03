"""
App Store Connect API 客户端
处理所有与 App Store Connect API 的交互
"""

import jwt
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from .models import AppStoreConnectConfig


class AppStoreConnectClient:
    """App Store Connect API 客户端"""

    def __init__(self, config: Optional[AppStoreConnectConfig] = None):
        self.config = config

    def set_config(self, config: AppStoreConnectConfig):
        """设置配置"""
        self.config = config

    def generate_jwt_token(self) -> str:
        """生成 App Store Connect API JWT token"""
        if not self.config:
            raise ValueError("App Store Connect 配置未设置")

        now = datetime.now()
        payload = {
            'iss': self.config.issuer_id,
            'iat': int(now.timestamp()),
            'exp': int((now + timedelta(minutes=20)).timestamp()),
            'aud': 'appstoreconnect-v1'
        }

        return jwt.encode(
            payload,
            self.config.private_key,
            algorithm='ES256',
            headers={'kid': self.config.key_id}
        )

    def make_api_request(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None) -> Dict[str, Any]:
        """发送 App Store Connect API 请求"""
        if not self.config:
            raise ValueError("App Store Connect 配置未设置")

        token = self.generate_jwt_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        url = f'https://api.appstoreconnect.apple.com/v1/{endpoint}'

        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        elif method == 'PATCH':
            response = requests.patch(url, headers=headers, json=data)
        else:
            raise ValueError(f"不支持的 HTTP 方法: {method}")

        response.raise_for_status()
        return response.json() if response.content else {}

    # 团队成员相关 API
    def get_team_members(self) -> List[Dict[str, Any]]:
        """获取团队成员列表"""
        result = self.make_api_request("users")

        members = []
        for user in result.get('data', []):
            attrs = user.get('attributes', {})
            members.append({
                'id': user.get('id'),
                'email': attrs.get('username'),
                'first_name': attrs.get('firstName'),
                'last_name': attrs.get('lastName'),
                'roles': attrs.get('roles', []),
                'provisioning_allowed': attrs.get('provisioningAllowed', False)
            })

        return members

    def invite_team_member(self, email: str, first_name: str, last_name: str,
                          roles: List[str], provisioning_allowed: bool = False) -> Dict[str, Any]:
        """邀请新的团队成员"""
        data = {
            'data': {
                'type': 'userInvitations',
                'attributes': {
                    'email': email,
                    'firstName': first_name,
                    'lastName': last_name,
                    'roles': roles,
                    'provisioningAllowed': provisioning_allowed
                }
            }
        }

        return self.make_api_request("userInvitations", method='POST', data=data)

    def remove_team_member(self, user_id: str) -> None:
        """移除团队成员"""
        self.make_api_request(f"users/{user_id}", method='DELETE')

    # 应用相关 API
    def get_apps(self) -> List[Dict[str, Any]]:
        """获取应用列表"""
        result = self.make_api_request("apps")

        apps = []
        for app in result.get('data', []):
            attrs = app.get('attributes', {})
            apps.append({
                'id': app.get('id'),
                'name': attrs.get('name'),
                'bundle_id': attrs.get('bundleId'),
                'sku': attrs.get('sku'),
                'primary_locale': attrs.get('primaryLocale')
            })

        return apps

    # TestFlight 相关 API
    def create_beta_group(self, app_id: str, group_name: str,
                         is_internal: bool = True, public_link_enabled: bool = False) -> Dict[str, Any]:
        """创建 TestFlight 测试组"""
        data = {
            'data': {
                'type': 'betaGroups',
                'attributes': {
                    'name': group_name,
                    'isInternalGroup': is_internal,
                    'publicLinkEnabled': public_link_enabled
                },
                'relationships': {
                    'app': {
                        'data': {
                            'type': 'apps',
                            'id': app_id
                        }
                    }
                }
            }
        }

        return self.make_api_request("betaGroups", method='POST', data=data)

    def get_beta_groups(self, app_id: str = None) -> List[Dict[str, Any]]:
        """获取 TestFlight 测试组列表"""
        if app_id:
            endpoint = f"apps/{app_id}/betaGroups"
        else:
            endpoint = "betaGroups"

        result = self.make_api_request(endpoint)

        groups = []
        for group in result.get('data', []):
            attrs = group.get('attributes', {})
            groups.append({
                'id': group.get('id'),
                'name': attrs.get('name'),
                'is_internal_group': attrs.get('isInternalGroup'),
                'public_link_enabled': attrs.get('publicLinkEnabled'),
                'public_link_limit': attrs.get('publicLinkLimit')
            })

        return groups

    def create_beta_tester(self, email: str, first_name: str = None, last_name: str = None) -> Dict[str, Any]:
        """创建 Beta 测试者"""
        tester_data = {
            'data': {
                'type': 'betaTesters',
                'attributes': {
                    'email': email
                }
            }
        }

        if first_name:
            tester_data['data']['attributes']['firstName'] = first_name
        if last_name:
            tester_data['data']['attributes']['lastName'] = last_name

        return self.make_api_request("betaTesters", method='POST', data=tester_data)

    def find_beta_tester_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """通过邮箱查找 Beta 测试者"""
        result = self.make_api_request(f"betaTesters?filter[email]={email}")
        if result.get('data'):
            return result['data'][0]
        return None

    def add_tester_to_group(self, group_id: str, tester_id: str) -> None:
        """将测试者添加到测试组"""
        relationship_data = {
            'data': [
                {
                    'type': 'betaTesters',
                    'id': tester_id
                }
            ]
        }

        self.make_api_request(f"betaGroups/{group_id}/relationships/betaTesters", method='POST', data=relationship_data)

    def remove_tester_from_group(self, group_id: str, tester_id: str) -> None:
        """从测试组移除测试者"""
        relationship_data = {
            'data': [
                {
                    'type': 'betaTesters',
                    'id': tester_id
                }
            ]
        }

        self.make_api_request(f"betaGroups/{group_id}/relationships/betaTesters", method='DELETE', data=relationship_data)
