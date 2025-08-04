# 安装指南

## 安装步骤

### 1. 克隆项目

```bash
# 使用Git克隆项目
git clone https://github.com/your-username/counseling_system_project.git

# 进入项目目录
cd counseling_system_project/refactored_counseling_system
```

### 2. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 安装依赖包

```bash
# 升级pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

### 4. 验证安装

```bash
# 运行测试
python -m pytest tests/

# 或者运行示例
python example_usage.py
```

## 配置设置

### 1. 环境变量配置

创建 `.env` 文件（可选）：

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
```

### 2. 系统配置

编辑 `config.py` 文件中的默认配置：

```python
# 示例配置
class SystemConfig:
    MAX_DIALOGUE_LENGTH = 70
    MAX_MODIFICATION_ATTEMPTS = 3
    LOG_FILE = "processed_file.log"
    
class ModelConfig:
    CONVERSATION_MODEL = "qwen-turbo"
    REASONING_MODEL = "qwen-turbo"
    SUMMARY_MODEL = "qwen-turbo"
```

## API密钥获取

### 1. 智谱AI (ZhipuAI)
1. 访问 [智谱AI官网](https://open.bigmodel.cn/)
2. 注册账号并登录
3. 创建API密钥
4. 复制密钥到环境变量

### 2. 通义千问 (Qwen)
1. 访问 [阿里云通义千问](https://dashscope.console.aliyun.com/)
2. 注册阿里云账号
3. 开通通义千问服务
4. 获取API密钥

### 3. 月之暗面 (Moonshot)
1. 访问 [Moonshot官网](https://www.moonshot.cn/)
2. 注册开发者账号
3. 创建应用获取API密钥

### 4. OpenAI (可选)
1. 访问 [OpenAI官网](https://platform.openai.com/)
2. 注册账号
3. 创建API密钥
4. 配置代理设置

## 验证安装

### 1. 基本功能测试

```python
# 测试基本导入
from refactored_counseling_system import CounselingSystemApp

# 初始化应用
app = CounselingSystemApp()

# 验证系统
validation = app.validate_system()
print(f"系统验证结果: {validation}")
```

### 2. API连接测试

```python
# 测试LLM客户端
from refactored_counseling_system.llm_client import get_llm_client

client = get_llm_client()
connections = client.validate_connection()
print(f"API连接状态: {connections}")
```

### 3. 运行示例

```bash
# 运行单个会话示例
python example_usage.py
```

## 常见安装问题

### 1. Python版本问题

**问题**: `ModuleNotFoundError: No module named 'typing_extensions'`

**解决方案**:
```bash
pip install typing_extensions
```

### 2. 依赖包冲突

**问题**: 包版本冲突

**解决方案**:
```bash
# 清理并重新安装
pip uninstall -r requirements.txt -y
pip install -r requirements.txt --no-cache-dir
```

### 3. 权限问题

**问题**: 无法创建文件夹或文件

**解决方案**:
```bash
# 检查文件夹权限
ls -la

# 修改权限
chmod 755 refactored_counseling_system/
```

### 4. 网络连接问题

**问题**: 无法下载依赖包

**解决方案**:
```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

## 开发环境设置

### 1. 安装开发依赖

```bash
# 安装开发工具
pip install pytest pytest-cov black flake8 mypy

# 安装调试工具
pip install ipdb ipython
```

### 2. 配置代码格式化

```bash
# 安装pre-commit hooks
pip install pre-commit
pre-commit install
```

### 3. 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=refactored_counseling_system tests/

# 运行特定测试
pytest tests/test_agents.py
```

## 性能优化

### 1. 内存优化

```python
# 在config.py中调整
class SystemConfig:
    MAX_DIALOGUE_LENGTH = 50  # 减少对话长度
    BATCH_SIZE = 10           # 调整批处理大小
```

### 2. 并发优化

```python
# 调整并发线程数
results = app.process_patient_folder_concurrent(
    folder_path="patient_profiles",
    max_workers=3,  # 根据系统性能调整
    is_first_session=True
)
```

## 卸载指南

### 1. 删除虚拟环境

```bash
# 退出虚拟环境
deactivate

# 删除虚拟环境
rm -rf venv/
```

### 2. 清理文件

```bash
# 删除生成的文件
rm -rf dialogue_files/
rm -rf reasoning_files/
rm -rf summary_files/
rm -rf modification_files/
rm -rf original_files/
rm -f processed_file.log
```

### 3. 卸载依赖

```bash
# 卸载所有依赖
pip freeze | xargs pip uninstall -y
```

## 更新指南

### 1. 更新代码

```bash
# 拉取最新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt --upgrade
```

### 2. 迁移配置

```bash
# 备份配置文件
cp config.py config.py.backup

# 更新配置
# 手动合并新的配置项
```

## 技术支持

如果遇到安装问题，请：

1. 检查系统要求是否满足
2. 查看错误日志
3. 参考故障排除文档
4. 提交GitHub Issue

---

**注意**: 确保在安装过程中网络连接稳定，某些依赖包可能需要从国外下载。 