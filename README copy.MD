# 心理咨询系统 (Counseling System)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

一个基于大语言模型的智能心理咨询系统，支持患者-咨询师对话模拟、CBT认知行为疗法、推理评估等功能。

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 网络连接（用于访问AI模型API）

### 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd roleplay2

# 安装依赖
pip install openai zhipuai pathlib dataclasses typing
```

### 配置API密钥

有两种方式配置API密钥：

#### 方式1：环境变量（推荐）
```bash
# Windows
set ZHIPU_API_KEY=your_zhipu_api_key
set QWEN_API_KEY=your_qwen_api_key
set MOONSHOT_API_KEY=your_moonshot_api_key

# Linux/Mac
export ZHIPU_API_KEY=your_zhipu_api_key
export QWEN_API_KEY=your_qwen_api_key
export MOONSHOT_API_KEY=your_moonshot_api_key
```

#### 方式2：修改配置文件
编辑 `refactored_counseling_system/config.py` 文件，直接修改API密钥：

```python
@dataclass
class APIConfig:
    ZHIPU_API_KEY: str = "your_zhipu_api_key"
    QWEN_API_KEY: str = "your_qwen_api_key"
    MOONSHOT_API_KEY: str = "your_moonshot_api_key"
    # ...
```

### 快速运行

```bash
# 运行示例程序
python example_usage.py
```

## 📖 详细使用指南

### 1. 运行单个咨询会话

```python
from refactored_counseling_system import ConversationSession, ConversationMode

# 定义患者信息
patient_info = """
患者：张三
年龄：28岁
主要问题：工作压力大，经常感到焦虑
症状：失眠、注意力不集中、情绪低落
持续时间：3个月
背景：软件工程师，最近项目压力大
"""

# 创建会话
session = ConversationSession(
    patient_info=patient_info,
    is_first_session=True,  # 是否为首次会话
    conversation_mode=ConversationMode.PATIENT_FIRST  # 患者先说话
)

# 运行完整会话
results = session.run_full_session()

# 查看结果
print(f"会话完成，共进行了 {results['statistics']['total_turns']} 轮对话")
print(f"推理评估次数：{len(results['session_data']['reasoning_history'])}")
```

### 2. 批量处理患者档案

```python
from refactored_counseling_system import CounselingSystemApp

# 初始化应用
app = CounselingSystemApp()

# 批量处理文件夹中的患者档案
results = app.process_patient_folder(
    folder_path="Original_Profile",  # 患者档案文件夹
    is_first_session=True,
    conversation_mode=ConversationMode.PATIENT_FIRST
)

print(f"处理结果：")
print(f"- 总文件数：{results['total_files']}")
print(f"- 成功处理：{results['processed']}")
print(f"- 跳过文件：{results['skipped']}")
print(f"- 错误文件：{results['errors']}")
```

### 3. 生成CBT认知模型

```python
# 从对话文件生成CBT认知模型
cbt_results = app.generate_cbt_models(
    dialogue_folder="Adialogue_files",           # 对话文件夹
    with_suggestion_path="Awith_suggestion",     # 包含建议的CBT模型
    half_suggestion_path="Ahalf_suggestion",     # 部分建议的CBT模型
    without_suggestion_path="Awithout_suggestion" # 不含建议的CBT模型
)

print(f"CBT模型生成完成：{cbt_results['processed']} 个文件")
```

### 4. 系统状态检查

```python
# 验证系统配置
validation = app.validate_system()
if validation["overall_status"]:
    print("✅ 系统配置正确，可以正常运行")
else:
    print("❌ 系统配置有问题：")
    print(f"  配置验证：{validation['config_valid']}")
    print(f"  LLM连接：{validation['llm_connections']}")
    print(f"  目录检查：{validation['directories_ok']}")

# 查看系统状态
status = app.get_system_status()
print(f"系统状态：{status}")
```

## ⚙️ 配置说明

### 主要配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `MAX_DIALOGUE_LENGTH` | 70 | 最大对话轮数 |
| `MAX_MODIFICATION_ATTEMPTS` | 4 | 最大修改尝试次数 |
| `SUMMARY_START_SIZE` | 13 | 开始摘要的对话轮数 |
| `SUMMARY_BUFFER_SIZE` | 6 | 摘要缓冲区大小 |
| `DEFAULT_TEMPERATURE` | 0.8 | 默认模型温度 |
| `REASONING_TEMPERATURE` | 0.9 | 推理模型温度 |

### 模型配置

系统支持多种AI模型：

- **Qwen系列**: `qwen-plus`, `qwen-max`
- **DeepSeek**: `deepseek-r1` (用于推理)
- **Moonshot**: `moonshot-v1-8k`
- **OpenAI**: 通过代理访问

### 目录结构

```
roleplay2/
├── refactored_counseling_system/    # 重构后的系统
│   ├── config.py                    # 配置管理
│   ├── prompts.py                   # 提示词管理
│   ├── llm_client.py               # AI客户端
│   ├── dialogue_manager.py         # 对话管理
│   ├── reasoning_engine.py         # 推理引擎
│   ├── agents.py                   # 代理系统
│   ├── file_utils.py               # 文件工具
│   └── main.py                     # 主程序
├── Original_Profile/               # 原始患者档案
├── Adialogue_files/               # 对话文件
├── Awith_suggestion/              # 包含建议的CBT模型
├── Ahalf_suggestion/              # 部分建议的CBT模型
├── Awithout_suggestion/           # 不含建议的CBT模型
├── example_usage.py               # 使用示例
├── B.py                          # 原始系统文件
└── README.md                     # 本文档
```

## 🛠️ 开发指南

### 添加新的AI模型

1. 在 `config.py` 中添加模型配置
2. 在 `llm_client.py` 中添加客户端支持
3. 更新模型路由逻辑

### 自定义提示词

编辑 `prompts.py` 文件，修改或添加新的提示词模板：

```python
class PromptTemplates:
    # 添加新的提示词模板
    YOUR_CUSTOM_PROMPT = """
    你的自定义提示词内容...
    """
```

### 扩展代理功能

在 `agents.py` 中继承基类创建新的代理：

```python
class CustomAgent(BaseAgent):
    def generate_response(self, dialogue_manager, context=None):
        # 实现自定义逻辑
        pass
```

## 📊 功能特性

### ✅ 已实现功能

- [x] 多轮对话管理
- [x] R1推理评估
- [x] CBT认知模型生成
- [x] 批量文件处理
- [x] 自动摘要生成
- [x] 配置管理
- [x] 错误处理和日志
- [x] 会话数据持久化

### 🔄 计划中功能

- [ ] Web界面
- [ ] 数据库集成
- [ ] 实时监控面板
- [ ] 多语言支持
- [ ] RESTful API
- [ ] 单元测试覆盖

## 🐛 常见问题

### 1. API连接失败

**问题**：提示API密钥错误或连接超时

**解决方法**：
```bash
# 检查API密钥是否正确设置
python -c "from refactored_counseling_system import config; print(config.api.QWEN_API_KEY)"

# 验证网络连接
python -c "from refactored_counseling_system import CounselingSystemApp; app = CounselingSystemApp(); print(app.validate_system())"
```

### 2. 文件路径错误

**问题**：找不到患者档案文件

**解决方法**：
```python
import os
# 检查文件是否存在
folder_path = "Original_Profile"
if os.path.exists(folder_path):
    files = os.listdir(folder_path)
    print(f"找到 {len(files)} 个文件")
else:
    print("文件夹不存在，请检查路径")
```

### 3. 模型响应异常

**问题**：AI模型返回格式错误

**解决方法**：
- 检查模型配置和温度设置
- 查看日志文件了解详细错误信息
- 尝试降低温度参数

### 4. 内存使用过高

**问题**：处理大量文件时内存占用过高

**解决方法**：
- 减少 `SUMMARY_BUFFER_SIZE` 参数
- 分批处理文件
- 增加系统内存

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/新功能`)
3. 提交更改 (`git commit -am '添加新功能'`)
4. 推送到分支 (`git push origin feature/新功能`)
5. 创建 Pull Request

### 代码规范

- 遵循 PEP 8 代码风格
- 添加适当的类型提示
- 编写清晰的文档字符串
- 添加必要的单元测试

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 创建 Issue
- 发送邮件至：[your-email@example.com]
- 项目主页：[https://github.com/your-username/counseling-system]

---

## 🎯 快速测试

运行以下命令快速测试系统：

```bash
# 测试系统配置
python -c "
from refactored_counseling_system import CounselingSystemApp
app = CounselingSystemApp()
result = app.validate_system()
print('系统状态:', '✅ 正常' if result['overall_status'] else '❌ 异常')
print('详细信息:', result)
"

# 运行完整示例
python example_usage.py
```

如果一切正常，你应该看到系统正常运行的输出信息。

**祝你使用愉快！** 🎉