# 故障排除指南

## 常见问题及解决方案

### 1. API连接问题

#### 问题：API密钥无效
**症状**: 
```
Error: 401 Unauthorized
Error: 无效的sk token，请检查token是否正确
```

**解决方案**:
1. 检查API密钥是否正确
2. 确认API密钥是否过期
3. 验证API服务是否正常

```python
# 验证API密钥
from refactored_counseling_system.llm_client import get_llm_client

client = get_llm_client()
connections = client.validate_connection()

for model, status in connections.items():
    if not status:
        print(f"❌ {model} 连接失败，请检查API密钥")
```

#### 问题：网络连接超时
**症状**:
```
Error: Connection timeout
Error: Network error
```

**解决方案**:
1. 检查网络连接
2. 配置代理设置
3. 增加超时时间

```python
# 配置代理（如果需要）
import os
os.environ['HTTP_PROXY'] = 'http://proxy.example.com:8080'
os.environ['HTTPS_PROXY'] = 'https://proxy.example.com:8080'
```

### 2. 系统验证失败

#### 问题：系统验证失败
**症状**:
```
System validation failed!
Validation results: {'config_valid': False, 'llm_connections': {...}}
```

**解决方案**:
1. 检查配置文件
2. 验证API连接
3. 确保文件夹权限

```python
# 详细验证
from refactored_counseling_system import CounselingSystemApp

app = CounselingSystemApp()
validation = app.validate_system()

print("详细验证结果:")
for key, value in validation.items():
    print(f"  {key}: {value}")
```

### 3. 文件操作问题

#### 问题：文件权限错误
**症状**:
```
PermissionError: [Errno 13] Permission denied
```

**解决方案**:
1. 检查文件权限
2. 以管理员身份运行
3. 修改文件夹权限

```bash
# Linux/macOS 修改权限
chmod 755 refactored_counseling_system/
chmod 644 *.py

# Windows 以管理员身份运行
# 右键点击命令提示符，选择"以管理员身份运行"
```

#### 问题：磁盘空间不足
**症状**:
```
OSError: [Errno 28] No space left on device
```

**解决方案**:
1. 清理临时文件
2. 删除不需要的文件
3. 增加磁盘空间

```python
# 清理临时文件
import shutil
import os

folders_to_clean = [
    "dialogue_files", "reasoning_files", "summary_files",
    "modification_files", "original_files", "__pycache__"
]

for folder in folders_to_clean:
    if os.path.exists(folder):
        shutil.rmtree(folder)
        print(f"已清理: {folder}")
```

### 4. 内存问题

#### 问题：内存不足
**症状**:
```
MemoryError: Unable to allocate memory
```

**解决方案**:
1. 减少批处理大小
2. 增加系统内存
3. 优化代码

```python
# 减少内存使用
from refactored_counseling_system import config

# 减少对话长度
config.system.MAX_DIALOGUE_LENGTH = 30

# 减少批处理大小
config.system.BATCH_SIZE = 5

# 禁用缓存
config.system.ENABLE_CACHING = False
```

### 5. 并发处理问题

#### 问题：线程死锁
**症状**:
```
程序卡住，无响应
```

**解决方案**:
1. 减少并发数
2. 增加超时设置
3. 检查线程锁

```python
# 减少并发数
results = app.process_patient_folder_concurrent(
    folder_path="patient_profiles",
    max_workers=1,  # 减少到1个线程
    is_first_session=True
)
```

#### 问题：API限制
**症状**:
```
Error: Rate limit exceeded
Error: Too many requests
```

**解决方案**:
1. 减少并发数
2. 增加请求间隔
3. 使用多个API密钥

```python
# 添加请求间隔
import time

def process_with_delay():
    for i in range(10):
        # 处理文件
        process_file(f"patient_{i:03d}.txt")
        # 等待1秒
        time.sleep(1)
```

### 6. 依赖包问题

#### 问题：模块导入错误
**症状**:
```
ModuleNotFoundError: No module named 'xxx'
ImportError: cannot import name 'xxx'
```

**解决方案**:
1. 安装缺失的依赖
2. 检查Python版本
3. 重新安装依赖

```bash
# 重新安装依赖
pip uninstall -r requirements.txt -y
pip install -r requirements.txt --no-cache-dir

# 检查Python版本
python --version
# 确保版本 >= 3.8
```

#### 问题：版本冲突
**症状**:
```
VersionConflict: xxx requires yyy==1.0.0 but you have yyy==2.0.0
```

**解决方案**:
1. 创建虚拟环境
2. 使用兼容版本
3. 更新依赖版本

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 7. 配置问题

#### 问题：配置参数错误
**症状**:
```
ValueError: Invalid configuration value
TypeError: Expected int but got str
```

**解决方案**:
1. 检查配置文件
2. 验证参数类型
3. 使用默认配置

```python
# 重置为默认配置
from refactored_counseling_system import config

# 重置系统配置
config.system.MAX_DIALOGUE_LENGTH = 70
config.system.MAX_MODIFICATION_ATTEMPTS = 3
config.system.LOG_FILE = "processed_file.log"

# 重置模型配置
config.model.CONVERSATION_MODEL = "qwen-turbo"
config.model.REASONING_MODEL = "qwen-turbo"
config.model.DEFAULT_TEMPERATURE = 0.8
```

## 调试工具

### 1. 日志分析

```python
import logging

# 启用详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 运行程序并查看日志
from refactored_counseling_system import CounselingSystemApp

app = CounselingSystemApp()
results = app.run_single_session(
    patient_info="测试患者信息",
    filename="debug_test"
)
```

### 2. 性能监控

```python
import time
import psutil

def monitor_performance():
    """监控系统性能"""
    start_time = time.time()
    start_memory = psutil.virtual_memory().percent
    
    # 运行任务
    app = CounselingSystemApp()
    results = app.run_single_session(...)
    
    end_time = time.time()
    end_memory = psutil.virtual_memory().percent
    
    print(f"执行时间: {end_time - start_time:.2f} 秒")
    print(f"内存使用: {start_memory:.1f}% → {end_memory:.1f}%")
    print(f"内存变化: {end_memory - start_memory:.1f}%")
```

### 3. 网络诊断

```python
import requests

def test_api_connections():
    """测试API连接"""
    apis = [
        ("智谱AI", "https://open.bigmodel.cn/api/paas/v4"),
        ("通义千问", "https://dashscope.aliyuncs.com/api/v1"),
        ("月之暗面", "https://api.moonshot.cn/v1")
    ]
    
    for name, url in apis:
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ {name}: 连接正常")
        except Exception as e:
            print(f"❌ {name}: 连接失败 - {e}")
```

## 预防措施

### 1. 定期维护

```python
def system_maintenance():
    """系统维护"""
    import os
    import shutil
    
    # 清理临时文件
    temp_files = ["*.log", "*.tmp", "__pycache__"]
    for pattern in temp_files:
        # 删除匹配的文件
        pass
    
    # 检查磁盘空间
    disk_usage = shutil.disk_usage(".")
    free_space_gb = disk_usage.free / (1024**3)
    print(f"可用磁盘空间: {free_space_gb:.1f} GB")
    
    # 检查内存使用
    memory = psutil.virtual_memory()
    print(f"内存使用率: {memory.percent:.1f}%")
```

### 2. 备份策略

```python
def create_backup():
    """创建备份"""
    import shutil
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_{timestamp}"
    
    # 备份重要文件
    important_files = [
        "config.py",
        "processed_file.log",
        "dialogue_files/",
        "reasoning_files/"
    ]
    
    for file in important_files:
        if os.path.exists(file):
            shutil.copy2(file, backup_dir)
    
    print(f"备份已创建: {backup_dir}")
```

### 3. 健康检查

```python
def health_check():
    """系统健康检查"""
    issues = []
    
    # 检查API连接
    from refactored_counseling_system.llm_client import get_llm_client
    client = get_llm_client()
    connections = client.validate_connection()
    
    if not any(connections.values()):
        issues.append("所有API连接失败")
    
    # 检查磁盘空间
    import shutil
    disk_usage = shutil.disk_usage(".")
    free_space_gb = disk_usage.free / (1024**3)
    
    if free_space_gb < 1.0:
        issues.append("磁盘空间不足")
    
    # 检查内存使用
    import psutil
    memory = psutil.virtual_memory()
    
    if memory.percent > 90:
        issues.append("内存使用率过高")
    
    return issues

# 运行健康检查
issues = health_check()
if issues:
    print("发现系统问题:")
    for issue in issues:
        print(f"  ⚠️  {issue}")
else:
    print("✅ 系统健康检查通过")
```

## 获取帮助

### 1. 查看日志

```python
def analyze_logs():
    """分析日志文件"""
    log_file = "processed_file.log"
    
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"日志文件: {log_file}")
        print(f"总行数: {len(lines)}")
        
        # 查找错误
        errors = [line for line in lines if "ERROR" in line]
        if errors:
            print(f"发现 {len(errors)} 个错误:")
            for error in errors[-5:]:  # 显示最后5个错误
                print(f"  {error.strip()}")
```

### 2. 系统信息

```python
def system_info():
    """获取系统信息"""
    import platform
    import sys
    
    print("=== 系统信息 ===")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {sys.version}")
    print(f"架构: {platform.machine()}")
    
    # 检查依赖包
    import pkg_resources
    installed_packages = [d.project_name for d in pkg_resources.working_set]
    
    required_packages = [
        "openai", "zhipuai", "requests", "pathlib"
    ]
    
    print("\n=== 依赖包检查 ===")
    for package in required_packages:
        if package in installed_packages:
            print(f"✅ {package}")
        else:
            print(f"❌ {package} - 未安装")
```

### 3. 联系支持

如果以上方法都无法解决问题，请：

1. **收集信息**:
   - 错误日志
   - 系统信息
   - 配置信息
   - 复现步骤

2. **提交Issue**:
   - 在GitHub上提交Issue
   - 提供详细的错误描述
   - 附上相关的日志和配置

3. **寻求帮助**:
   - 查看项目文档
   - 搜索相关问题
   - 联系项目维护者

---

**注意**: 在尝试任何修复操作前，建议先备份重要数据。对于生产环境，请在测试环境中验证修复方案。 