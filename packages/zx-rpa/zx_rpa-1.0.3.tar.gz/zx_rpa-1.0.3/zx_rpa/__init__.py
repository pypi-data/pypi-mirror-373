"""
ZX RPA - 自动化工具包
对常见的功能函数和一些平台的API进行封装

📦 模块列表 (按功能分类):

⚙️ 全局配置模块:
    - global_config.py       # 全局YAML配置管理 | 链式访问 | 自动保存
      └── init_global_config # 初始化全局配置函数 | 支持G.xx.xx无限层级访问

🔐 验证码识别模块:
    - tujian_api.py          # 图鉴验证码识别服务 | 验证码破解 | 自动识别
      └── TjCaptcha          # 图鉴验证码识别类 | 支持多种验证码类型

📢 消息通知模块:
    - wecom_notification_api.py    # 企业微信群机器人通知 | 微信群消息 | 工作通知
      └── wecom_notification       # 企业微信通知函数 | 文本消息发送
    - dingtalk_notification_api.py # 钉钉群机器人通知 | 钉钉群消息 | 工作提醒
      └── dingtalk_notification    # 钉钉通知函数 | 带签名验证
    - feishu_notification_api.py   # 飞书群机器人通知 | 飞书群消息 | 团队协作
      └── feishu_notification      # 飞书通知函数 | 文本消息推送

🤖 AI接口模块:
    - deepseek_api.py        # DeepSeek AI接口 | 人工智能 | 对话生成 | 代码生成
      └── deepseek_chat      # DeepSeek API调用类 | 智能问答

☁️ 云存储模块:
    - qiniuyun_api.py        # 七牛云存储 | 文件上传 | 对象存储 (需安装: pip install zx_rpa[qiniuyun])
      └── QiniuManager       # 七牛云管理类 | 文件上传下载

🎨 设计工具模块:


📊 办公协作模块:

操作系统模块:

使用方式：
    # 全局配置管理（推荐在应用启动时初始化）
    from zx_rpa.global_config import init_global_config
    G = init_global_config('config.yaml')

    # 设置配置（支持无限层级）
    G.api.qiniu.access_key = "your_key"
    G.database.mysql.host = "localhost"
    G.servers = ["server1", "server2"]

    # 读取配置（链式访问）
    timeout = G.api.timeout          # 获取简单值
    qiniu_config = G.api.qiniu.value()  # 获取字典用于传递函数

    # 验证码识别
    from zx_rpa.tujian_api import TjCaptcha
    captcha = TjCaptcha("用户名", "密码")
    result = captcha.main_captcha("图片路径或base64")

    # 消息通知
    from zx_rpa.wecom_notification_api import wecom_notification
    wecom_notification("消息内容", "webhook地址")

    # AI对话
    from zx_rpa.deepseek_api import DeepSeekAPI
    ai = DeepSeekAPI("api_key")
    response = ai.chat("你好")

    # 七牛云存储（需要额外安装依赖）
    from zx_rpa.qiniuyun_api import QiniuManager
    qiniu = QiniuManager("access_key", "secret_key", "bucket_name", "domain")
    result = qiniu.upload_file("本地文件.jpg", "远程路径/文件.jpg")

关键词索引：
全局配置 | YAML配置 | 链式访问 | G.xx.xx | 配置管理
验证码 | 图鉴 | 识别 | 破解 | 自动化
微信 | 企业微信 | 钉钉 | 飞书 | 消息 | 通知 | 群机器人
AI | 人工智能 | DeepSeek | 对话 | 生成
七牛云 | 对象存储 | 文件上传 | CDN | 云存储
Photoshop | PS | 图片处理 | 批量操作 | 设计
多维表格 | 数据管理 | 办公 | 协作
"""

__version__ = "1.0.3"

# 便捷导入全局配置功能
from .global_config import init_global_config

# 导出常用功能
__all__ = [
    "init_global_config",
]
