# Discord Bot 配置管理器

一个简单易用的网页界面，用于管理 Discord Bot 的多账户配置。

## 功能特性

🤖 **多账户管理**
- 支持添加/删除多个机器人账户
- 每个账户独立配置 Token、频道ID 和名称

👥 **白名单管理**
- 为每个账户单独配置白名单用户
- 支持添加/删除白名单用户ID

📦 **配置备份**
- 自动备份配置文件
- 支持恢复历史备份
- 备份文件带时间戳

🎨 **现代化界面**
- 响应式设计，支持手机访问
- 直观的操作界面
- 实时配置验证

## 快速开始

### 1. 启动配置管理器

```bash
# 方式1: 使用启动脚本（推荐）
python3 start_config.py

# 方式2: 直接运行
python3 config_web.py
```

### 2. 打开配置界面

在浏览器中访问: http://localhost:5000

### 3. 配置机器人账户

1. 点击"添加新账户"按钮
2. 填写以下信息：
   - **机器人名称**: 便于识别的名称（如：jinyue_king）
   - **频道ID**: Discord 频道的 ID
   - **Discord Token**: 机器人的 Token
   - **白名单用户**: 允许触发机器人回复的用户ID列表

3. 点击"保存配置"保存设置

## 配置说明

### 获取 Discord Token
1. 访问 [Discord Developer Portal](https://discord.com/developers/applications)
2. 创建或选择你的应用
3. 转到 "Bot" 页面
4. 复制 Token

### 获取频道ID
1. 在 Discord 中右键点击目标频道
2. 选择"复制频道ID"
3. 如果看不到此选项，需要先开启开发者模式：
   - 用户设置 → 高级 → 开发者模式

### 获取用户ID
1. 在 Discord 中右键点击用户
2. 选择"复制用户ID"

## 配置文件结构

配置会保存在 `accounts.json` 文件中：

```json
[
  {
    "token": "MTIzNTgwNTY3MTc5OTI2MzI3NA...",
    "channel_id": "1236263634091380843",
    "name": "jinyue_king",
    "whitelist_users": [
      "1073191903782252554",
      "1354834235420184669",
      "1354826965823000699"
    ]
  }
]
```

## 备份管理

- 每次保存配置时会自动创建备份
- 备份文件保存在 `config_backups/` 目录
- 备份文件命名格式：`accounts_backup_YYYYMMDD_HHMMSS.json`
- 可以通过界面恢复任意历史备份

## 安全提示

⚠️ **重要安全提示**
- Discord Token 是敏感信息，请妥善保管
- 不要将包含 Token 的配置文件上传到公开仓库
- 建议定期更换 Token

## 故障排除

### 端口占用
如果 5000 端口被占用，可以修改 `config_web.py` 中的端口号：
```python
app.run(host='0.0.0.0', port=5001, debug=False)  # 改为其他端口
```

### 权限问题
确保程序有权限读写配置文件和创建备份目录。

### 网络访问
如果需要其他设备访问配置界面，确保防火墙允许对应端口的访问。

## 技术架构

- **后端**: Flask (Python)
- **前端**: HTML + CSS + JavaScript
- **数据存储**: JSON 文件
- **备份策略**: 时间戳备份

## 更新日志

- v1.0.0: 初始版本，支持基本的多账户配置管理