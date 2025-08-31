# 🧬 BioNext MCP Server - 智能生物信息学分析助手

[![PyPI version](https://badge.fury.io/py/bionext-mcp.svg)](https://badge.fury.io/py/bionext-mcp)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP&Agent挑战赛](https://img.shields.io/badge/MCP%26Agent-挑战赛-red.svg)](https://modelscope.cn/mcp)

## 📋 项目简介

**BioNext MCP Server** 是一个专为 **MCP&Agent挑战赛** 设计的智能生物信息学分析助手，基于Model Context Protocol (MCP) 实现。该服务器使研究人员能够通过自然语言对话与AI助手进行复杂的生物数据分析，无需编程专业知识。

### 🎯 核心特性

- **🤖 智能工作流规划**: 自动分析用户需求并创建完整的生物信息学分析工作流
- **🔧 自动化脚本执行**: 自动检测Python环境，安装依赖包，执行分析脚本
- **📊 专业报告生成**: 生成美观的HTML执行报告，包含详细的执行统计和结果分析
- **🔄 工作流调试**: 提供完整的错误诊断和调试建议
- **🌐 多数据类型支持**: 支持单细胞RNA测序、基因表达、基因组学、蛋白质组学等

### 🧪 应用场景

- **单细胞RNA测序分析**: 细胞类型鉴定、差异表达分析、轨迹推断
- **基因表达分析**: 差异基因识别、功能富集分析、通路分析
- **基因组学分析**: 变异检测、结构变异分析、比较基因组学
- **蛋白质组学分析**: 蛋白质定量、修饰位点分析、互作网络构建

## 🚀 部署指南

### 环境要求

- **Python版本**: 3.8 或更高版本
- **操作系统**: Windows, macOS, Linux
- **内存**: 建议 4GB 以上
- **存储**: 建议 2GB 可用空间

### 安装方法

#### 方法1: 从PyPI安装（推荐）

```bash
# 使用pip安装
pip install bionext-mcp

# 或使用uv安装
uv add bionext-mcp
```

#### 方法2: 从源码安装

```bash
# 克隆仓库
git clone https://github.com/Cherine0205/BioNext-mcp.git
cd BioNext-mcp

# 安装依赖
pip install -r requirements.txt

# 安装包
pip install -e .
```

### MCP客户端配置

#### Cherry Studio 配置

```json
{
  "bionext-mcp": {
    "command": "python",
    "args": ["-m", "bionext_mcp"],
    "env": {
      "PROJECT_PATH": "./analysis"
    }
  }
}
```

#### 使用uvx运行（推荐）

```json
{
  "bionext-mcp": {
    "command": "uvx",
    "args": ["bionext-mcp"]
  }
}
```

### 本地测试

```bash
# 以模块运行
python -m bionext_mcp

# 或使用uvx
uvx bionext-mcp
```

## 💡 使用示例

### 示例1: 单细胞RNA测序分析

**用户请求**: "请帮我分析单细胞RNA测序数据，识别细胞类型并进行差异表达分析"

**MCP工具调用**:
```python
# 1. 分析任务
result = analyze_bioinformatics_task(
    user_request="单细胞RNA测序分析，识别细胞类型并进行差异表达分析",
    data_files=["scRNA_data.h5ad"],
    additional_context="数据包含10000个细胞，20000个基因"
)

# 2. 执行Claude生成的脚本
execution_result = execute_claude_script(
    claude_response="```python\nimport scanpy as sc\n# 分析代码...\n```",
    workflow_id="scRNA_analysis_001"
)
```

**输出结果**: 
- 自动生成的分析工作流
- 细胞类型聚类结果
- 差异表达基因列表
- 可视化图表
- 完整的HTML执行报告

### 示例2: 基因表达差异分析

**用户请求**: "比较对照组和实验组的基因表达差异，找出显著上调的基因"

**执行流程**:
1. 自动检测Python环境
2. 安装必要的包（pandas, numpy, scipy等）
3. 执行差异分析脚本
4. 生成火山图和热图
5. 输出差异基因列表

### 示例3: 工作流调试

当分析过程中遇到问题时：

```python
# 调试工作流
debug_info = debug_workflow(
    workflow_id="failed_workflow_123",
    error_context="脚本执行失败，提示模块导入错误"
)
```

**调试输出**:
- 工作流状态检查
- 错误文件分析
- 环境依赖验证
- 具体的解决建议

## 🔧 核心工具说明

### 1. analyze_bioinformatics_task
- **功能**: 分析用户需求并创建生物信息学工作流
- **输入**: 用户请求、数据文件列表、额外上下文
- **输出**: 工作流ID、分析计划、Claude提示

### 2. debug_workflow
- **功能**: 工作流调试和错误诊断
- **输入**: 工作流ID、错误上下文
- **输出**: 调试报告、问题诊断、解决建议

### 3. execute_claude_script
- **功能**: 自动执行Claude生成的Python脚本
- **输入**: Claude响应内容、工作流ID、执行上下文
- **输出**: 执行结果、HTML报告、错误信息

## 📊 执行报告示例

每次脚本执行后，系统会自动生成专业的HTML报告，包含：

- **执行统计**: 总脚本数、成功/失败数量、成功率
- **详细结果**: 每个脚本的输出、错误信息、执行状态
- **文件路径**: 生成的脚本文件和分析结果位置
- **下一步建议**: 基于执行结果的后续操作指导

## 🛠️ 开发信息

### 技术架构
- **MCP框架**: FastMCP
- **构建工具**: Hatchling
- **包管理**: pip/uv
- **报告生成**: HTML + CSS

### 依赖包
- **核心**: fastmcp>=0.1.0
- **兼容性**: pathlib2 (Python < 3.4)
- **构建**: hatchling

### 项目结构
```
bionext_mcp/
├── __init__.py          # 包初始化
├── __main__.py          # 入口点
├── my_server.py         # MCP服务器实现
└── dist/                # 构建产物
    ├── *.whl            # 轮子包
    └── *.tar.gz         # 源码包
```

## 🤝 贡献指南

我们欢迎社区贡献！如果您想参与项目开发：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持与反馈

- **项目地址**: [https://github.com/Cherine0205/BioNext-mcp](https://github.com/Cherine0205/BioNext-mcp)
- **问题反馈**: [https://github.com/Cherine0205/BioNext-mcp/issues](https://github.com/Cherine0205/BioNext-mcp/issues)
- **PyPI包**: [https://pypi.org/project/bionext-mcp/](https://pypi.org/project/bionext-mcp/)
- **魔搭MCP广场**: [https://modelscope.cn/mcp](https://modelscope.cn/mcp)

## 🙏 致谢

感谢 **MCP&Agent挑战赛** 提供的平台和机会，让我们能够为生物信息学社区贡献这个智能分析工具。

---

**BioNext MCP Server** - 让生物信息学分析更智能、更简单！🧬✨
