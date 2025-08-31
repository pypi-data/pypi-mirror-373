# Google Search MCP Service

这是一个MCP（模型上下文协议）服务，提供对 Google Custom Search API 的访问。它允许您与 Google 搜索进行交互，并检索网页内容和搜索结果。

## 功能

- 搜索
    - google_search 执行 Google 搜索
    - read_webpage 提取网页内容

- 搜索功能
    - 自定义搜索结果数量
    - 支持多种搜索参数
    - 返回标题、链接、摘要等信息

- 网页内容提取
    - 提取网页文本内容
    - 清理HTML标签
    - 获取页面元数据
    - 支持多种内容格式

- 网络支持
    - HTTP 代理支持
    - SOCKS 代理支持
    - 自定义请求头
    - 超时控制

## 安装

```bash
# 克隆仓库
git clone https://github.com/your-repo/google-search-mcp.git
cd google-search-mcp

# 创建并激活虚拟环境
uv sync
```

## 使用（如Claude客户端）

URL: https://mcpcn.com/docs/quickstart/user/

claude_desktop_config.json
```json
{
    "mcpServers": {
        "google-search": {
            "command": "uv",
            "args": [
                "--directory",
                "/Users/Desktop/google-search-mcp", # 替换为你的目录
                "run",
                "google-search-mcp"
            ],
            "env": {
                "GOOGLE_API_KEY": "your_api_key_here", # 替换为你的 Google API 密钥
                "GOOGLE_SEARCH_ENGINE_ID": "your_engine_id_here" # 替换为你的搜索引擎ID
            }
        }
    }
}
```
or

```json
{
    "mcpServers": {
        "google-search": {
            "command": "uvx",
            "args": [
                "google-search-mcp"
            ],
            "env": {
                "GOOGLE_API_KEY": "your_api_key_here", # 替换为你的 Google API 密钥
                "GOOGLE_SEARCH_ENGINE_ID": "your_engine_id_here" # 替换为你的搜索引擎ID
            }
        }
    }
}
```
