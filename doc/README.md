# 心理咨询系统 (Counseling System)

## 项目概述

这是一个基于人工智能的心理咨询系统，支持自动化的心理咨询对话、推理评估和结果分析。系统采用模块化设计，支持多种AI模型，具备并发处理能力，能够高效处理大量患者档案。

## 🚀 主要功能

### 核心功能
- **智能对话系统**: 支持患者与AI咨询师的自动对话
- **推理评估机制**: 基于R1推理的咨询师回复优化
- **批量处理**: 支持并发处理大量患者档案
- **多模型支持**: 集成多种AI模型（Qwen、Moonshot、GPT等）
- **结果分析**: 自动生成对话摘要和修改历史

### 高级功能
- **并发处理**: 同时处理多个患者档案，大幅提升效率
- **文件组织**: 按类型自动分类保存结果文件
- **断点续传**: 支持中断后继续处理
- **错误处理**: 完善的错误处理和日志记录

## 📁 项目结构

```
refactored_counseling_system/
├── doc/                          # 文档目录
│   ├── README.md                 # 项目主文档
│   ├── INSTALLATION.md           # 安装指南
│   ├── USER_GUIDE.md             # 用户使用指南
│   ├── API_REFERENCE.md          # API参考文档
│   ├── ARCHITECTURE.md           # 系统架构文档
│   ├── CONFIGURATION.md          # 配置指南
│   └── TROUBLESHOOTING.md        # 故障排除指南
├── agents.py                     # 智能体模块
├── config.py                     # 配置管理
├── dialogue_manager.py           # 对话管理
├── file_utils.py                 # 文件工具
├── llm_client.py                 # LLM客户端
├── main.py                       # 主应用模块
├── prompts.py                    # 提示词管理
├── reasoning_engine.py           # 推理引擎
├── example_usage.py              # 使用示例
├── tests/                        # 测试目录
├── utils/                        # 工具模块
└── requirements.txt              # 依赖包列表
```

## 🛠️ 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置API密钥
```bash
# 设置环境变量
export ZHIPU_API_KEY="your_zhipu_key"
export QWEN_API_KEY="your_qwen_key"
export MOONSHOT_API_KEY="your_moonshot_key"
```

### 3. 运行示例
```python
from refactored_counseling_system import CounselingSystemApp

# 初始化应用
app = CounselingSystemApp()

# 运行单个会话
results = app.run_single_session(
    patient_info="患者信息...",
    filename="patient_001",
    is_first_session=True
)
```

## 📊 性能特点

### 并发处理性能
- **串行处理**: 支持串行处理
- **并发处理**: 支持并发处理

### 文件组织
- 自动创建分类文件夹
- 支持断点续传
- 线程安全的文件处理


## 📚 文档导航

- [安装指南](INSTALLATION.md) - 详细的安装和配置说明
- [用户指南](USER_GUIDE.md) - 完整的使用教程
- [API参考](API_REFERENCE.md) - 详细的API文档
- [系统架构](ARCHITECTURE.md) - 技术架构说明
- [配置指南](CONFIGURATION.md) - 系统配置详解
- [故障排除](TROUBLESHOOTING.md) - 常见问题解决方案


### 开发环境设置
1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证。



**注意**: 这是一个研究性质的项目，不应用于实际的临床心理咨询。请确保遵守相关的伦理和法律要求。 