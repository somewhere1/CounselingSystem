# 配置指南

## 配置概述

心理咨询系统支持多种配置方式，包括环境变量、配置文件、代码配置等。本指南详细介绍各种配置选项及其使用方法。

## 配置方式

### 1. 环境变量配置

系统优先从环境变量读取配置，这是最安全和推荐的方式。

#### 设置环境变量

**Windows**:
```cmd
set ZHIPU_API_KEY=your_zhipu_api_key_here
set QWEN_API_KEY=your_qwen_api_key_here
set MOONSHOT_API_KEY=your_moonshot_api_key_here
```

**macOS/Linux**:
```bash
export ZHIPU_API_KEY=your_zhipu_api_key_here
export QWEN_API_KEY=your_qwen_api_key_here
export MOONSHOT_API_KEY=your_moonshot_api_key_here
```

#### 使用.env文件

创建 `.env` 文件在项目根目录：

```bash
# .env 文件示例
ZHIPU_API_KEY=your_zhipu_api_key_here
QWEN_API_KEY=your_qwen_api_key_here
MOONSHOT_API_KEY=your_moonshot_api_key_here
OPENAI_PROXY_API_KEY=your_openai_proxy_key_here
OPENAI_PROXY_BASE_URL=https://api.openai-proxy.org/v1

# 系统配置
MAX_DIALOGUE_LENGTH=70
DEFAULT_TEMPERATURE=0.8
MAX_MODIFICATION_ATTEMPTS=3
```

### 2. 代码配置

直接在 `config.py` 文件中修改配置：

```python
# config.py 示例
import os

class APIConfig:
    ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "your_default_key")
    QWEN_API_KEY = os.getenv("QWEN_API_KEY", "your_default_key")
    MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY", "your_default_key")
    
class SystemConfig:
    MAX_DIALOGUE_LENGTH = int(os.getenv("MAX_DIALOGUE_LENGTH", "70"))
    DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.8"))
    MAX_MODIFICATION_ATTEMPTS = int(os.getenv("MAX_MODIFICATION_ATTEMPTS", "3"))
```

## 配置分类详解

### 1. API配置 (APIConfig)

管理各种AI模型的API密钥和连接设置。

#### 智谱AI配置
```python
class APIConfig:
    ZHIPU_API_KEY = "your_zhipu_api_key"
    ZHIPU_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
```

#### 通义千问配置
```python
class APIConfig:
    QWEN_API_KEY = "your_qwen_api_key"
    QWEN_BASE_URL = "https://dashscope.aliyuncs.com/api/v1"
```

#### 月之暗面配置
```python
class APIConfig:
    MOONSHOT_API_KEY = "your_moonshot_api_key"
    MOONSHOT_BASE_URL = "https://api.moonshot.cn/v1"
```

#### OpenAI代理配置
```python
class APIConfig:
    OPENAI_PROXY_API_KEY = "your_openai_proxy_key"
    OPENAI_PROXY_BASE_URL = "https://api.openai-proxy.org/v1"
```

### 2. 系统配置 (SystemConfig)

控制系统行为和性能的参数。

#### 对话长度控制
```python
class SystemConfig:
    MAX_DIALOGUE_LENGTH = 70  # 最大对话轮数
    MIN_DIALOGUE_LENGTH = 5   # 最小对话轮数
```

#### 推理优化配置
```python
class SystemConfig:
    MAX_MODIFICATION_ATTEMPTS = 3  # 最大修改尝试次数
    REASONING_THRESHOLD = 0.7      # 推理质量阈值
    ENABLE_REASONING = True         # 是否启用推理
```

#### 并发处理配置
```python
class SystemConfig:
    MAX_WORKERS = 3                 # 最大并发线程数
    BATCH_SIZE = 10                 # 批处理大小
    ENABLE_CONCURRENT = True        # 是否启用并发
```

#### 文件管理配置
```python
class SystemConfig:
    LOG_FILE = "processed_file.log"  # 日志文件路径
    BACKUP_ENABLED = True           # 是否启用备份
    AUTO_CLEANUP = False            # 是否自动清理
```

### 3. 模型配置 (ModelConfig)

配置AI模型的使用策略。

#### 模型选择
```python
class ModelConfig:
    CONVERSATION_MODEL = "qwen-turbo"    # 对话模型
    REASONING_MODEL = "qwen-turbo"       # 推理模型
    SUMMARY_MODEL = "qwen-turbo"         # 摘要模型
```

#### 模型参数
```python
class ModelConfig:
    DEFAULT_TEMPERATURE = 0.8            # 默认温度参数
    MAX_TOKENS = 2048                    # 最大token数
    TOP_P = 0.9                          # Top-p参数
```

#### 模型优先级
```python
class ModelConfig:
    PRIMARY_MODEL = "qwen-turbo"         # 主模型
    FALLBACK_MODELS = [                  # 备用模型列表
        "moonshot-v1-8k",
        "zhipu-turbo"
    ]
```

### 4. 路径配置 (PathConfig)

配置各种文件路径。

#### 文件夹路径
```python
class PathConfig:
    DIALOGUE_FOLDER = "dialogue_files"           # 对话文件目录
    WITH_SUGGESTION_PATH = "Awith_suggestion"    # 有建议路径
    HALF_SUGGESTION_PATH = "Ahalf_suggestion"    # 半建议路径
    WITHOUT_SUGGESTION_PATH = "Awithout_suggestion"  # 无建议路径
```

#### 输出路径
```python
class PathConfig:
    OUTPUT_DIR = "output"                        # 输出目录
    LOG_DIR = "logs"                            # 日志目录
    BACKUP_DIR = "backups"                      # 备份目录
```

## 配置验证

### 1. 系统验证

```python
from refactored_counseling_system import CounselingSystemApp

app = CounselingSystemApp()
validation = app.validate_system()

if validation.get("overall_status", False):
    print("✅ 系统配置验证通过")
else:
    print("❌ 系统配置验证失败")
    print(f"错误详情: {validation}")
```

### 2. API连接验证

```python
from refactored_counseling_system.llm_client import get_llm_client

client = get_llm_client()
connections = client.validate_connection()

print("API连接状态:")
for model, status in connections.items():
    status_icon = "✅" if status else "❌"
    print(f"  {status_icon} {model}: {'连接正常' if status else '连接失败'}")
```

### 3. 配置检查工具

```python
def check_configuration():
    """检查系统配置"""
    from refactored_counseling_system import config
    
    print("=== 配置检查 ===")
    
    # 检查API密钥
    api_keys = [
        ("ZHIPU_API_KEY", config.api.ZHIPU_API_KEY),
        ("QWEN_API_KEY", config.api.QWEN_API_KEY),
        ("MOONSHOT_API_KEY", config.api.MOONSHOT_API_KEY)
    ]
    
    for name, key in api_keys:
        if key and key != "your_default_key":
            print(f"✅ {name}: 已配置")
        else:
            print(f"❌ {name}: 未配置")
    
    # 检查系统配置
    print(f"📊 最大对话长度: {config.system.MAX_DIALOGUE_LENGTH}")
    print(f"📊 最大修改次数: {config.system.MAX_MODIFICATION_ATTEMPTS}")
    print(f"📊 默认温度: {config.model.DEFAULT_TEMPERATURE}")

# 运行配置检查
check_configuration()
```

## 性能调优配置

### 1. 内存优化

```python
# 减少内存使用
class SystemConfig:
    MAX_DIALOGUE_LENGTH = 50          # 减少对话长度
    BATCH_SIZE = 5                    # 减少批处理大小
    ENABLE_CACHING = False            # 禁用缓存
```

### 2. 速度优化

```python
# 提高处理速度
class SystemConfig:
    MAX_WORKERS = 5                   # 增加并发数
    ENABLE_CONCURRENT = True          # 启用并发
    SKIP_REASONING = False            # 保留推理
```

### 3. 质量优化

```python
# 提高输出质量
class SystemConfig:
    MAX_MODIFICATION_ATTEMPTS = 5     # 增加修改次数
    REASONING_THRESHOLD = 0.8         # 提高质量阈值
    ENABLE_DETAILED_LOGGING = True    # 启用详细日志
```

## 环境特定配置

### 1. 开发环境

```python
# 开发环境配置
class DevConfig:
    LOG_LEVEL = "DEBUG"
    ENABLE_MOCK = True
    MAX_WORKERS = 1
    SKIP_API_CALLS = False
```

### 2. 测试环境

```python
# 测试环境配置
class TestConfig:
    LOG_LEVEL = "INFO"
    ENABLE_MOCK = True
    MAX_WORKERS = 2
    SKIP_API_CALLS = True
```

### 3. 生产环境

```python
# 生产环境配置
class ProdConfig:
    LOG_LEVEL = "WARNING"
    ENABLE_MOCK = False
    MAX_WORKERS = 3
    SKIP_API_CALLS = False
```

## 配置管理最佳实践

### 1. 安全性

- **不要硬编码敏感信息**: 使用环境变量存储API密钥
- **使用.gitignore**: 确保.env文件不被提交到版本控制
- **定期轮换密钥**: 定期更新API密钥

```bash
# .gitignore 示例
.env
*.log
__pycache__/
*.pyc
```

### 2. 可维护性

- **使用配置类**: 将相关配置组织到类中
- **添加注释**: 为每个配置项添加说明
- **版本控制**: 使用版本号管理配置变更

```python
# 配置版本管理
class ConfigVersion:
    VERSION = "1.0.0"
    LAST_UPDATED = "2024-01-01"
```

### 3. 灵活性

- **支持多环境**: 为不同环境提供不同配置
- **配置继承**: 使用配置继承减少重复
- **动态配置**: 支持运行时配置修改

```python
# 环境配置继承
class BaseConfig:
    LOG_LEVEL = "INFO"
    MAX_WORKERS = 3

class DevConfig(BaseConfig):
    LOG_LEVEL = "DEBUG"
    MAX_WORKERS = 1

class ProdConfig(BaseConfig):
    LOG_LEVEL = "WARNING"
    MAX_WORKERS = 5
```

## 故障排除

### 1. 配置问题诊断

```python
def diagnose_config_issues():
    """诊断配置问题"""
    issues = []
    
    # 检查API密钥
    if not config.api.ZHIPU_API_KEY or config.api.ZHIPU_API_KEY == "your_default_key":
        issues.append("ZHIPU_API_KEY 未配置")
    
    # 检查系统配置
    if config.system.MAX_DIALOGUE_LENGTH < 1:
        issues.append("MAX_DIALOGUE_LENGTH 设置过小")
    
    # 检查路径配置
    import os
    for path_name, path_value in config.paths.__dict__.items():
        if not os.path.exists(path_value):
            issues.append(f"路径不存在: {path_name} = {path_value}")
    
    return issues

# 运行诊断
issues = diagnose_config_issues()
if issues:
    print("发现配置问题:")
    for issue in issues:
        print(f"  ❌ {issue}")
else:
    print("✅ 配置检查通过")
```

### 2. 常见配置错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| API密钥无效 | 密钥过期或错误 | 重新生成API密钥 |
| 路径不存在 | 文件夹未创建 | 手动创建文件夹 |
| 权限不足 | 文件权限问题 | 修改文件权限 |
| 内存不足 | 配置过大 | 减少批处理大小 |

### 3. 配置恢复

```python
def reset_to_default_config():
    """重置为默认配置"""
    import shutil
    import os
    
    # 备份当前配置
    if os.path.exists("config.py"):
        shutil.copy("config.py", "config.py.backup")
    
    # 恢复默认配置
    default_config = """
# 默认配置
import os

class APIConfig:
    ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")
    QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
    MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY", "")

class SystemConfig:
    MAX_DIALOGUE_LENGTH = 70
    MAX_MODIFICATION_ATTEMPTS = 3
    LOG_FILE = "processed_file.log"

class ModelConfig:
    CONVERSATION_MODEL = "qwen-turbo"
    REASONING_MODEL = "qwen-turbo"
    DEFAULT_TEMPERATURE = 0.8
"""
    
    with open("config.py", "w", encoding="utf-8") as f:
        f.write(default_config)
    
    print("✅ 配置已重置为默认值")
```

---

**注意**: 修改配置后建议重启应用程序以确保配置生效。对于生产环境，建议先在测试环境中验证配置变更。 