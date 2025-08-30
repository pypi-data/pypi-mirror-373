# ZX RPA

一个简单的RPA工具包，包含各种自动化操作类。

## 安装

```bash
pip install zx-rpa
```

## 使用示例

```python
from zx_rpa import FeishuAPI, PhotoshopAPI

# 飞书操作
feishu = FeishuAPI(app_id="your_app_id", app_secret="your_secret")
feishu.create_table()

# Photoshop操作  
ps = PhotoshopAPI()
ps.open_file("image.psd")
```

## 功能模块

- 飞书多维表操作
- Photoshop自动化
- 更多功能开发中...
