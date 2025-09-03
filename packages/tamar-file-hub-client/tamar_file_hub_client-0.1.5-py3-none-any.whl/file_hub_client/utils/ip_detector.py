"""
用户真实IP自动检测模块
从当前HTTP请求上下文中自动获取真实用户IP地址
"""

import os
import threading
from typing import Optional, Dict, Any, Callable
from contextvars import ContextVar

# 使用ContextVar存储当前请求的用户IP
current_user_ip: ContextVar[Optional[str]] = ContextVar('current_user_ip', default=None)

# 存储自定义IP提取器
_custom_ip_extractor: Optional[Callable[[], Optional[str]]] = None

# 线程本地存储（fallback）
_thread_local = threading.local()


def set_user_ip_extractor(extractor: Callable[[], Optional[str]]):
    """
    设置自定义用户IP提取器
    
    Args:
        extractor: 返回用户IP的函数，如果无法获取则返回None
    """
    global _custom_ip_extractor
    _custom_ip_extractor = extractor


def set_current_user_ip(ip: str):
    """
    设置当前请求的用户IP（通常在请求开始时调用）
    
    Args:
        ip: 用户真实IP地址
    """
    current_user_ip.set(ip)
    # 同时设置线程本地存储作为fallback
    _thread_local.user_ip = ip


def get_current_user_ip() -> Optional[str]:
    """
    自动获取当前用户的真实IP地址
    
    优先级:
    1. ContextVar中的用户IP
    2. 自定义IP提取器
    3. 常见Web框架自动检测
    4. 环境变量
    5. 线程本地存储
    
    Returns:
        用户真实IP地址，如果无法获取则返回None
    """
    # 1. 优先使用ContextVar
    ip = current_user_ip.get(None)
    if ip:
        return ip
    
    # 2. 尝试自定义提取器
    if _custom_ip_extractor:
        try:
            ip = _custom_ip_extractor()
            if ip:
                return ip
        except:
            pass
    
    # 3. 尝试从常见Web框架中自动获取
    ip = _auto_detect_from_web_frameworks()
    if ip:
        return ip
    
    # 4. 尝试从环境变量获取
    ip = os.environ.get('USER_IP') or os.environ.get('CLIENT_IP')
    if ip:
        return ip
    
    # 5. Fallback到线程本地存储
    try:
        return getattr(_thread_local, 'user_ip', None)
    except:
        return None


def _auto_detect_from_web_frameworks() -> Optional[str]:
    """
    从常见Web框架中自动检测用户IP
    """
    # Flask
    try:
        from flask import request
        if request:
            return _extract_ip_from_headers(request.environ)
    except (ImportError, RuntimeError):
        pass
    
    # Django
    try:
        from django.http import HttpRequest
        from django.utils.deprecation import MiddlewareMixin
        # Django需要通过中间件设置，这里只能检查是否有请求对象
        import django
        from django.core.context_processors import request as django_request
        # Django的请求需要通过其他方式获取，这里先跳过
    except ImportError:
        pass
    
    # FastAPI/Starlette
    try:
        from starlette.requests import Request
        # FastAPI需要在路由处理器中获取，这里先跳过
    except ImportError:
        pass
    
    # Tornado
    try:
        import tornado.web
        # Tornado需要在RequestHandler中获取，这里先跳过
    except ImportError:
        pass
    
    return None


def _extract_ip_from_headers(environ: Dict[str, Any]) -> Optional[str]:
    """
    从HTTP环境变量中提取用户真实IP
    
    Args:
        environ: WSGI environ字典或类似的HTTP环境变量
    
    Returns:
        用户真实IP，优先级: X-Forwarded-For > X-Real-IP > CF-Connecting-IP > Remote-Addr
    """
    # X-Forwarded-For: 最常用的代理头，包含原始客户端IP
    forwarded_for = environ.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        # 取第一个IP（原始客户端IP），忽略代理IP
        return forwarded_for.split(',')[0].strip()
    
    # X-Real-IP: Nginx常用的真实IP头
    real_ip = environ.get('HTTP_X_REAL_IP')
    if real_ip:
        return real_ip.strip()
    
    # CF-Connecting-IP: Cloudflare的连接IP
    cf_ip = environ.get('HTTP_CF_CONNECTING_IP')
    if cf_ip:
        return cf_ip.strip()
    
    # Remote-Addr: 直接连接的IP（可能是代理IP）
    remote_addr = environ.get('REMOTE_ADDR')
    if remote_addr:
        return remote_addr.strip()
    
    return None


def clear_current_user_ip():
    """清除当前请求的用户IP（通常在请求结束时调用）"""
    current_user_ip.set(None)
    try:
        delattr(_thread_local, 'user_ip')
    except AttributeError:
        pass


# Flask集成装饰器
def flask_auto_user_ip(app=None):
    """
    Flask应用自动用户IP检测装饰器
    
    用法:
        from flask import Flask
        from file_hub_client.utils.ip_detector import flask_auto_user_ip
        
        app = Flask(__name__)
        flask_auto_user_ip(app)
    """
    def decorator(app_instance):
        @app_instance.before_request
        def extract_user_ip():
            from flask import request
            ip = _extract_ip_from_headers(request.environ)
            if ip:
                set_current_user_ip(ip)
        
        @app_instance.after_request  
        def clear_user_ip(response):
            clear_current_user_ip()
            return response
            
        return app_instance
    
    if app is None:
        return decorator
    else:
        return decorator(app)


# 上下文管理器
class UserIPContext:
    """
    用户IP上下文管理器
    
    用法:
        with UserIPContext("192.168.1.100"):
            # 在此范围内SDK会自动使用这个IP
            client.upload_file(...)
    """
    
    def __init__(self, user_ip: str):
        self.user_ip = user_ip
        self.token = None
    
    def __enter__(self):
        self.token = current_user_ip.set(self.user_ip)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.token:
            current_user_ip.reset(self.token)