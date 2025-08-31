# ZX RPA

对常见的功能函数和一些平台的API进行封装。

## 安装

```bash
pip install zx-rpa
```

## 注意事项

主要是自用，所以版本更新可能会存在不兼容的情况，或者停止更新等情况，慎用！

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

- 飞书多维表操作  FeishuAPI
- Photoshop自动化 PhotoshopAPI
- 图鉴验证码识别 TjCaptcha
