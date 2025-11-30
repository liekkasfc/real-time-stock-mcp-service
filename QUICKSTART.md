# 快速开始指南

本指南将帮助你快速配置并运行股票数据 MCP Server。

## 1. 安装 uv 包管理器

### Windows (PowerShell)
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Linux/MacOS
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 2. 安装项目依赖

在项目根目录执行:

```bash
cd my_stock_mcp_server
uv sync
```

这将自动创建虚拟环境并安装所有依赖。

## 3. 配置 API 密钥 (可选)

如果 stockapi.com.cn 需要 API 密钥，请创建 `.env` 文件:

```bash
cp .env.example .env
```

然后编辑 `.env` 文件，填入你的 API Token:

```
STOCKAPI_TOKEN=你的API密钥
```

## 4. 测试运行

直接运行服务器:

```bash
uv run mcp_server.py
```

服务器将启动并等待 MCP 客户端连接。

## 5. 在 Claude Desktop 中配置

### 5.1 找到配置文件

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

### 5.2 编辑配置文件

在配置文件中添加以下内容（注意替换路径）:

```json
{
  "mcpServers": {
    "stock-data": {
      "command": "uv",
      "args": [
        "--directory",
        "F:/Project/PyCharm/all-MCP-servers/my_stock_mcp_server",
        "run",
        "mcp_server.py"
      ]
    }
  }
}
```

**重要**: 
- Windows 用户请使用双反斜杠 `\\` 或单斜杠 `/`
- 路径必须是绝对路径
- 不要使用 `~` 或环境变量

**Linux/MacOS 示例**:
```json
{
  "mcpServers": {
    "stock-data": {
      "command": "uv",
      "args": [
        "--directory",
        "/home/username/projects/stock_mcp_server",
        "run",
        "mcp_server.py"
      ]
    }
  }
}
```

### 5.3 重启 Claude Desktop

保存配置文件后，完全退出 Claude Desktop（确保后台进程也已关闭），然后重新启动。

## 6. 验证安装

在 Claude Desktop 中，你应该能看到一个工具图标（通常是锤子或扳手图标）。点击它可以看到所有可用的股票数据工具。

尝试询问 Claude:

- "搜索贵州茅台的股票代码"
- "查询600519的实时行情"
- "获取最新交易日"
- "分析000001最近一个月的K线走势"

## 7. 常见问题

### Q: 提示找不到 uv 命令
**A**: 确保 uv 已正确安装并添加到系统 PATH。重启终端或电脑后再试。

### Q: Claude Desktop 看不到工具
**A**: 
1. 检查配置文件路径是否正确（使用绝对路径）
2. 确保 JSON 格式正确（可以用 JSON 验证器检查）
3. 完全退出 Claude Desktop 重启
4. 查看 Claude Desktop 的日志文件

### Q: 工具调用失败
**A**: 
1. 检查 API Token 是否正确配置
2. 查看服务器日志输出
3. 确认网络连接正常
4. 确认 stockapi.com.cn 服务可用

### Q: Windows 路径问题
**A**: Windows 路径示例:
- ✅ `"C:\\Users\\YourName\\projects\\stock_mcp_server"`
- ✅ `"C:/Users/YourName/projects/stock_mcp_server"`
- ❌ `"C:\Users\YourName\projects\stock_mcp_server"` (单反斜杠会转义)

## 8. 查看日志

如需查看详细日志，可以修改 `mcp_server.py` 中的日志级别:

```python
setup_logging(level=logging.DEBUG)  # 改为 DEBUG 级别
```

## 9. 下一步

- 阅读 [README.md](README.md) 了解所有可用工具
- 查看项目结构了解如何添加新功能
- 探索各个工具模块的实现

## 需要帮助?

如遇到问题，请检查:
1. 日志输出
2. Claude Desktop 的错误信息
3. API 配置是否正确
4. 网络连接状态

祝使用愉快! 📈
