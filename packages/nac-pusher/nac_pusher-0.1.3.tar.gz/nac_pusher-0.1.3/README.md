# NAC Pusher

一个用于向飞书(Lark)推送消息的Python包。

## 安装

```bash
pip install nac-pusher -U
```

## 使用方法

在使用之前，请设置以下环境变量：

- `FEISHU_APP_ID`: 飞书应用的App ID
- `FEISHU_APP_SECRET`: 飞书应用的App Secret

然后在Python代码中使用：
```python
from nac_pusher.feishu import FeishuBot

bot = FeishuBot()
bot.append_push_txt('Hello, World!').send()
```
## 更新日志

- 0.1.3: 初始版本，基本功能实现

## 许可证

本项目采用MIT许可证 - 详见[LICENSE](LICENSE)文件了解详情。