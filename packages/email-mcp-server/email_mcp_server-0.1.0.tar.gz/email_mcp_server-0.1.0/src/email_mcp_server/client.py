import httpx
import re
from typing import Optional, Dict, Any
from urllib.parse import unquote
import logging

logger = logging.getLogger(__name__)


class EmailSystemClient:
    """邮件系统API客户端"""
    
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.client = httpx.Client(
            timeout=30.0,
            follow_redirects=True,
            verify=False  # 如果遇到SSL问题可以设置
        )
        self.xsrf_token = None
        self.session_cookie = None
        self._logged_in = False
    
    def _extract_cookies(self, response: httpx.Response) -> tuple[Optional[str], Optional[str]]:
        """从响应中提取XSRF-TOKEN和laravel_session"""
        xsrf = None
        session = None
        
        # 获取cookies
        cookies = response.cookies
        
        # 从cookies中提取token
        xsrf_cookie = cookies.get('XSRF-TOKEN')
        if xsrf_cookie:
            xsrf = unquote(xsrf_cookie)
        
        session_cookie = cookies.get('laravel_session')
        if session_cookie:
            session = session_cookie
        
        return xsrf, session
    
    def login(self) -> bool:
        """执行登录流程"""
        try:
            # Step 1: 获取初始Cookie
            logger.info("获取初始Cookie...")
            response = self.client.get(f"{self.base_url}/users/login")
            
            xsrf, session = self._extract_cookies(response)
            
            if not xsrf or not session:
                logger.error("无法获取初始Cookie")
                return False
            
            self.xsrf_token = xsrf
            self.session_cookie = session
            
            # Step 2: 执行登录
            logger.info("执行登录...")
            headers = {
                'X-XSRF-TOKEN': self.xsrf_token,
                'Cookie': f'XSRF-TOKEN={self.xsrf_token}; laravel_session={self.session_cookie}',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            }
            
            login_data = {
                'email': self.username,
                'password': self.password
            }
            
            response = self.client.post(
                f"{self.base_url}/users/login",
                json=login_data,
                headers=headers
            )
            
            # 更新Cookie
            new_xsrf, new_session = self._extract_cookies(response)
            if new_xsrf:
                self.xsrf_token = new_xsrf
            if new_session:
                self.session_cookie = new_session
            
            # 检查登录是否成功
            if response.status_code == 200:
                self._logged_in = True
                logger.info("登录成功")
                return True
            else:
                logger.error(f"登录失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"登录过程出错: {e}")
            return False
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """获取认证后的请求头"""
        if not self._logged_in:
            self.login()
        
        return {
            'X-XSRF-TOKEN': self.xsrf_token,
            'Cookie': f'XSRF-TOKEN={self.xsrf_token}; laravel_session={self.session_cookie}',
            'Accept': 'application/json',
        }
    
    def get_template(self, template_id: int) -> Optional[Dict[str, Any]]:
        """获取邮件模板"""
        if not self._logged_in:
            if not self.login():
                return None
        
        try:
            headers = self._get_auth_headers()
            response = self.client.get(
                f"{self.base_url}/email-templates/{template_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"获取模板失败: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"获取模板出错: {e}")
            return None
    
    def update_template(self, data: Dict[str, Any]) -> bool:
        """更新邮件模板"""
        if not self._logged_in:
            if not self.login():
                return False
        
        try:
            headers = self._get_auth_headers()
            
            # 使用form-data格式
            response = self.client.post(
                f"{self.base_url}/email-templates/update",
                data=data,  # 使用data而不是json
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'ok' in result:
                    logger.info(f"更新成功: {result['ok']}")
                    return True
                else:
                    logger.error(f"更新失败: {result}")
                    return False
            else:
                logger.error(f"更新模板失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"更新模板出错: {e}")
            return False
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'client'):
            self.client.close()