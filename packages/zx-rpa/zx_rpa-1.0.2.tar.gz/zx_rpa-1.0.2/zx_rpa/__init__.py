"""
ZX RPA - 自动化工具包
"""

__version__ = "0.1.0"

# 导入各个模块的主要类
from .feishu_api import FeishuAPI
from .photoshop_api import PhotoshopAPI
from .tujian_api import TjCaptcha

# 定义包的公开接口
__all__ = [
    "FeishuAPI",
    "PhotoshopAPI",
    "TjCaptcha",
]
