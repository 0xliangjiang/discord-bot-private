# Discord Bot Manager - GUI版本使用说明

## 🚀 快速开始

### 1. 构建可执行文件（开发者）

#### Windows系统：
```bash
# 方法1：使用批处理脚本（推荐）
双击运行 build.bat

# 方法2：手动执行
pip install -r requirements_gui.txt
python build_exe.py
```

#### macOS/Linux系统：
```bash
pip install -r requirements_gui.txt
python build_exe.py
```

### 2. 分发给客户

构建完成后，将整个 `dist/DiscordBotManager/` 文件夹打包分发给客户。

## 🖥️ 界面介绍

### 主界面布局
```
┌─────────────────────────────────────────────────────────┐
│  状态: 未运行    [启动Bot] [停止Bot] [重启Bot]             │
├─────────────────┬───────────────────────────────────────┤
│  账户配置       │                                       │
│  ┌─────────────┴─┐    运行日志                          │
│  │  通用配置      │    ┌─────────────────────────────┐   │
│  └───────────────┘    │ [时间] 系统启动               │   │
│                       │ [时间] 加载配置完成            │   │
│                       │ [时间] Bot开始运行...          │   │
│                       └─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 功能标签页

#### 📱 账户配置
- **添加账户**：添加新的Discord Bot账户
- **账户信息**：
  - 名称：自定义账户名称
  - Token：Discord Bot Token
  - 频道ID：监控的频道ID
  - 白名单用户：逗号分隔的用户ID列表
- **保存配置**：保存到 `accounts.json`
- **重新加载**：从文件重新加载配置

#### ⚙️ 通用配置
- **AI配置**：
  - API Key：AI服务密钥
  - API URL：AI服务地址
  - 模型：使用的AI模型
- **Bot配置**：
  - 回复语言：中文/English/日本語
  - 消息限制：每次获取的消息数量
  - 延迟设置：回复的随机延迟范围
- **白名单配置**：
  - 启用白名单模式
  - 聊天历史长度限制

## 📋 详细使用流程

### 第一步：获取Discord Bot Token

1. 访问 [Discord Developer Portal](https://discord.com/developers/applications)
2. 创建新应用程序
3. 在Bot页面创建Bot用户
4. 复制Token（注意保密）
5. 设置必要的权限：
   - Send Messages
   - Read Message History
   - View Channels

### 第二步：获取频道ID

1. 在Discord中启用开发者模式：
   - 用户设置 → 高级 → 开发者模式
2. 右键点击要监控的频道
3. 选择"复制ID"

### 第三步：配置程序

#### 账户配置：
```
名称：主账户
Token：YOUR_BOT_TOKEN_HERE
频道ID：1234567890123456789
白名单用户：1111111111,2222222222,3333333333
```

#### AI配置：
```
API Key：YOUR_API_KEY
API URL：https://api.openai.com/v1/chat/completions
模型：gpt-3.5-turbo
```

### 第四步：启动运行

1. 确保所有配置填写完整
2. 点击"启动Bot"按钮
3. 观察日志输出确认运行状态
4. Bot开始监控指定频道并自动回复

## 🛠️ 高级功能

### 关键词回复

编辑 `keyword_responses.json` 文件添加关键词回复：

```json
{
  "你好": ["你好！", "嗨！", "哈喽"],
  "再见": ["再见！", "拜拜", "下次见"],
  "谢谢": ["不客气", "不用谢", "😊"]
}
```

### 环境变量配置

程序会自动生成 `.env` 文件，也可以手动编辑：

```env
AI_API_KEY=your_api_key_here
AI_API_URL=https://api.openai.com/v1/chat/completions
AI_MODEL=gpt-3.5-turbo
ENABLE_WHITELIST_MODE=True
REPLY_DELAY_MIN=30
REPLY_DELAY_MAX=60
```

### 日志和调试

- **实时日志**：右侧窗口显示实时运行日志
- **日志文件**：保存在 `logs/bot.log`
- **配置备份**：自动备份到 `config_backups/`

## 🚨 故障排除

### 常见问题

#### 1. 程序无法启动
- **检查**：是否有杀毒软件阻止
- **解决**：添加程序到白名单

#### 2. Bot无法连接Discord
- **检查**：Token是否正确
- **检查**：网络连接是否正常
- **检查**：Bot是否被邀请到服务器

#### 3. AI回复异常
- **检查**：API Key是否有效
- **检查**：API余额是否充足
- **检查**：API URL是否正确

#### 4. 白名单用户无回复
- **检查**：用户ID是否正确
- **检查**：是否启用了白名单模式
- **检查**：用户是否在指定频道发言

### 错误代码说明

| 错误类型 | 说明 | 解决方法 |
|---------|------|----------|
| 401 | Token无效 | 检查Discord Bot Token |
| 403 | 权限不足 | 检查Bot权限设置 |
| 429 | 请求限制 | 增加延迟时间 |
| 500 | 服务器错误 | 稍后重试 |

## 📁 文件结构

```
DiscordBotManager/
├── DiscordBotManager.exe    # 主程序
├── accounts.json            # 账户配置
├── .env                     # 环境变量
├── keyword_responses.json   # 关键词回复
├── data/                    # 聊天记录
├── logs/                    # 日志文件
├── config_backups/          # 配置备份
└── README.txt              # 使用说明
```

## 🔧 开发者信息

### 技术栈
- **界面**：PyQt6
- **网络**：requests
- **打包**：PyInstaller
- **配置**：JSON + .env

### 自定义修改

如需修改功能，编辑以下文件：
- `gui_main.py`：主界面逻辑
- `src/bot.py`：Bot核心功能
- `src/config.py`：配置管理
- `src/chat_history.py`：聊天记录管理

### 重新构建
```bash
python build_exe.py
```

## 📞 技术支持

如遇到问题：
1. 查看程序日志文件
2. 检查配置是否正确
3. 确认网络连接正常
4. 联系技术支持并提供日志文件

---

**版本**：v1.0  
**更新日期**：2024年  
**兼容系统**：Windows 10/11, macOS 10.15+, Linux Ubuntu 18.04+