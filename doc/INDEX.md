# 心理咨询系统文档索引

## 📚 文档概览

欢迎使用心理咨询系统文档！本索引将帮助您快速找到所需的文档。

## 📖 文档列表

### 🚀 入门文档
- **[README.md](README.md)** - 项目主文档，包含项目概述、功能特点和使用指南
- **[INSTALLATION.md](INSTALLATION.md)** - 详细的安装指南，包括系统要求、安装步骤和配置设置

### 📖 使用文档
- **[USER_GUIDE.md](USER_GUIDE.md)** - 完整的使用教程，包含基本用法、高级功能和最佳实践
- **[API_REFERENCE.md](API_REFERENCE.md)** - 详细的API文档，包含所有类、方法和数据结构的说明

### 🏗️ 技术文档
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - 系统架构文档，详细说明系统设计和技术实现
- **[CONFIGURATION.md](CONFIGURATION.md)** - 配置指南，包含各种配置选项和调优建议

### 🔧 维护文档
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - 故障排除指南，包含常见问题和解决方案

## 🎯 按需求查找

### 新用户入门
1. **[README.md](README.md)** - 了解项目概况
2. **[INSTALLATION.md](INSTALLATION.md)** - 安装和配置系统
3. **[USER_GUIDE.md](USER_GUIDE.md)** - 学习基本使用方法

### 开发者参考
1. **[API_REFERENCE.md](API_REFERENCE.md)** - 查看API文档
2. **[ARCHITECTURE.md](ARCHITECTURE.md)** - 了解系统架构
3. **[CONFIGURATION.md](CONFIGURATION.md)** - 配置和调优

### 问题解决
1. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - 查找常见问题解决方案
2. **[USER_GUIDE.md](USER_GUIDE.md)** - 查看使用最佳实践

### 系统维护
1. **[CONFIGURATION.md](CONFIGURATION.md)** - 系统配置和维护
2. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - 故障诊断和修复

## 📋 快速参考

### 常用命令
```bash
# 安装依赖
pip install -r requirements.txt

# 运行示例
python example_usage.py

# 运行测试
python -m pytest tests/

# 验证系统
python -c "from refactored_counseling_system import CounselingSystemApp; app = CounselingSystemApp(); print(app.validate_system())"
```

### 重要文件
- `main.py` - 主应用模块
- `agents.py` - 智能体模块
- `config.py` - 配置管理
- `example_usage.py` - 使用示例

### 关键配置
```python
# API密钥配置
ZHIPU_API_KEY=your_zhipu_key
QWEN_API_KEY=your_qwen_key
MOONSHOT_API_KEY=your_moonshot_key

# 系统配置
MAX_DIALOGUE_LENGTH=70
MAX_MODIFICATION_ATTEMPTS=3
```

## 🔍 搜索指南

### 按功能搜索
- **对话处理**: 查看 [USER_GUIDE.md](USER_GUIDE.md) 和 [API_REFERENCE.md](API_REFERENCE.md)
- **批量处理**: 查看 [USER_GUIDE.md](USER_GUIDE.md) 中的并发处理部分
- **文件管理**: 查看 [ARCHITECTURE.md](ARCHITECTURE.md) 中的文件工具部分
- **配置调优**: 查看 [CONFIGURATION.md](CONFIGURATION.md)

### 按问题搜索
- **安装问题**: 查看 [INSTALLATION.md](INSTALLATION.md)
- **API连接问题**: 查看 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **性能问题**: 查看 [CONFIGURATION.md](CONFIGURATION.md) 中的性能调优部分
- **文件问题**: 查看 [TROUBLESHOOTING.md](TROUBLESHOOTING.md) 中的文件操作问题

## 📞 获取帮助

### 文档反馈
如果您发现文档中的错误或有改进建议，请：
1. 提交GitHub Issue
2. 发送邮件给项目维护者
3. 在项目讨论区提出建议

### 技术支持
如果遇到技术问题，请：
1. 查看 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. 搜索GitHub Issues
3. 提交新的Issue并附上详细信息

### 贡献指南
如果您想为项目做出贡献：
1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 📝 文档更新

### 版本历史
- **v1.0.0** - 初始版本，包含基本功能文档
- **v1.1.0** - 添加并发处理和文件组织功能
- **v1.2.0** - 完善API文档和故障排除指南

### 更新计划
- [ ] 添加视频教程
- [ ] 完善API示例
- [ ] 添加性能基准测试文档
- [ ] 创建部署指南

---

**提示**: 建议按照文档索引的顺序阅读，这样可以更好地理解和使用系统。如果您是新手，建议从README.md开始；如果您是开发者，可以直接查看API_REFERENCE.md和ARCHITECTURE.md。 