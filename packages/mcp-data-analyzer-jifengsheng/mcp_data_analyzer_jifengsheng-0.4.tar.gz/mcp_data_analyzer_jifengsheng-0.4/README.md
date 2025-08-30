# 数据分析助手


## 本地调试

安装依赖包
```
uv sync
```
启动命令
```
uv --directory /Users/morris/Desktop/coding/mcp-data-analzyer-jifengsheng run main.py
```
## 提示词
分析{需要分析的文件路径}的各个方面，包含文字和图表，将分析结果保存为markdown格式的分析报告，
分析报告保存到{文件保存路径}目录下

## MCP 配置
```
{
   "mcp-data-analyzer":{
       "command": "uvx",
      "args": ["mcp-data-analyzer-jifengsheng"]
   }
}

```

