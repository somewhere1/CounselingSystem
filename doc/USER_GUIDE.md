# 用户使用指南

## 快速入门

### 1. 基本使用流程

```python
from refactored_counseling_system import CounselingSystemApp, ConversationMode

# 初始化应用
app = CounselingSystemApp()

# 验证系统
validation = app.validate_system()
if not validation.get("overall_status", False):
    print("系统验证失败，请检查配置")
    exit()

# 运行单个会话
results = app.run_single_session(
    patient_info="患者信息...",
    filename="patient_001",
    is_first_session=True,
    conversation_mode=ConversationMode.PATIENT_FIRST
)

print(f"会话完成，共{results['statistics']['total_turns']}轮对话")
```

### 2. 批量处理患者档案

```python
# 并发处理多个患者档案
results = app.process_patient_folder_concurrent(
    folder_path="patient_profiles",
    max_workers=3,  # 同时处理3个患者
    is_first_session=True,
    conversation_mode=ConversationMode.PATIENT_FIRST
)

print(f"处理完成：{results['processed']}个成功，{results['errors']}个错误")
```

## 详细功能说明

### 1. 单个会话处理

#### 基本会话
```python
# 创建患者信息
patient_info = """
患者信息：
姓名：张三
年龄：28岁
主要问题：工作压力大，经常感到焦虑
症状：失眠、注意力不集中、情绪低落
持续时间：3个月
"""

# 运行会话
results = app.run_single_session(
    patient_info=patient_info,
    filename="zhang_san",
    is_first_session=True,
    conversation_mode=ConversationMode.PATIENT_FIRST
)
```

#### 会话模式选择
```python
# 患者先发言模式
results = app.run_single_session(
    patient_info=patient_info,
    filename="patient_first",
    conversation_mode=ConversationMode.PATIENT_FIRST
)

# 咨询师先发言模式
results = app.run_single_session(
    patient_info=patient_info,
    filename="doctor_first",
    conversation_mode=ConversationMode.DOCTOR_FIRST
)
```

### 2. 批量处理

#### 串行处理
```python
# 逐个处理患者档案
results = app.process_patient_folder(
    folder_path="patient_profiles",
    is_first_session=True,
    conversation_mode=ConversationMode.PATIENT_FIRST
)
```

#### 并发处理
```python
# 同时处理多个患者档案
results = app.process_patient_folder_concurrent(
    folder_path="patient_profiles",
    max_workers=5,  # 根据系统性能调整
    is_first_session=True,
    conversation_mode=ConversationMode.PATIENT_FIRST
)
```

### 3. 结果分析

#### 查看会话统计
```python
# 获取会话统计信息
statistics = results['statistics']
print(f"总对话轮数: {statistics['total_turns']}")
print(f"推理评估次数: {statistics.get('reasoning_evaluations', 0)}")
print(f"是否正常结束: {results['session_summary']['ended_with_goodbye']}")
```

#### 查看对话历史
```python
# 获取对话历史
dialogue_history = results['dialogue_history']
for i, exchange in enumerate(dialogue_history):
    for role, content in exchange.items():
        print(f"{role}: {content}")
    print()
```

### 4. 文件管理

#### 查看保存的文件
```python
import os

# 检查保存的文件
folders = ["dialogue_files", "reasoning_files", "summary_files", 
           "modification_files", "original_files"]

for folder in folders:
    if os.path.exists(folder):
        files = os.listdir(folder)
        print(f"📁 {folder}/ - {len(files)} 个文件")
        for file in files[:3]:  # 显示前3个文件
            print(f"  - {file}")
```

#### 加载会话结果
```python
from refactored_counseling_system.file_utils import get_session_data_manager

# 加载会话数据
session_data_manager = get_session_data_manager()
session_data = session_data_manager.load_session_results("patient_001")

if session_data:
    print("成功加载会话数据")
    print(f"对话历史: {len(session_data['dialogue_history'])} 轮")
    print(f"推理历史: {len(session_data['reasoning_history'])} 次")
else:
    print("未找到会话数据")
```

## 高级功能

### 1. 自定义配置

#### 调整系统参数
```python
from refactored_counseling_system import config

# 修改系统配置
config.system.MAX_DIALOGUE_LENGTH = 50  # 减少对话长度
config.system.MAX_MODIFICATION_ATTEMPTS = 5  # 增加修改尝试次数

# 修改模型配置
config.model.CONVERSATION_MODEL = "qwen-turbo"
config.model.REASONING_MODEL = "qwen-turbo"
```

#### 自定义提示词
```python
from refactored_counseling_system.prompts import PromptManager

# 创建自定义提示词管理器
prompt_manager = PromptManager()

# 添加自定义提示词
custom_prompt = """
你是一位专业的心理咨询师，请根据患者的情况提供专业的建议。
注意：保持耐心、同理心，避免给出医疗诊断。
"""

# 使用自定义提示词
session = ConversationSession(
    patient_info=patient_info,
    is_first_session=True,
    conversation_mode=ConversationMode.PATIENT_FIRST,
    custom_prompt=custom_prompt
)
```

### 2. 错误处理

#### 处理API错误
```python
try:
    results = app.run_single_session(
        patient_info=patient_info,
        filename="test_patient"
    )
except Exception as e:
    print(f"会话处理失败: {e}")
    # 记录错误日志
    import logging
    logging.error(f"会话处理错误: {e}")
```

#### 处理文件错误
```python
# 检查文件是否存在
import os
if not os.path.exists("patient_profiles"):
    print("患者档案文件夹不存在，创建中...")
    os.makedirs("patient_profiles", exist_ok=True)
```

### 3. 性能监控

#### 监控处理进度
```python
import time
import psutil

def monitor_performance():
    """监控系统性能"""
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
    print(f"CPU使用率: {cpu_percent}%")
    print(f"内存使用率: {memory_percent}%")

# 在处理过程中监控性能
start_time = time.time()
results = app.process_patient_folder_concurrent(...)
end_time = time.time()

print(f"处理时间: {end_time - start_time:.2f} 秒")
monitor_performance()
```

## 实用示例

### 1. 完整的工作流程

```python
def complete_workflow():
    """完整的工作流程示例"""
    
    # 1. 初始化系统
    app = CounselingSystemApp()
    
    # 2. 验证系统
    validation = app.validate_system()
    if not validation.get("overall_status", False):
        print("系统验证失败")
        return
    
    # 3. 准备患者档案
    patient_profiles = [
        {
            "name": "patient_001.txt",
            "content": "患者A：25岁，焦虑症状，工作压力大"
        },
        {
            "name": "patient_002.txt", 
            "content": "患者B：30岁，抑郁情绪，人际关系困扰"
        }
    ]
    
    # 4. 创建患者档案文件夹
    import os
    folder_path = "patient_profiles"
    os.makedirs(folder_path, exist_ok=True)
    
    for profile in patient_profiles:
        with open(os.path.join(folder_path, profile["name"]), 'w', encoding='utf-8') as f:
            f.write(profile["content"])
    
    # 5. 批量处理
    results = app.process_patient_folder_concurrent(
        folder_path=folder_path,
        max_workers=2,
        is_first_session=True
    )
    
    # 6. 输出结果
    print(f"处理完成:")
    print(f"  总文件数: {results['total_files']}")
    print(f"  成功处理: {results['processed']}")
    print(f"  跳过文件: {results['skipped']}")
    print(f"  错误数量: {results['errors']}")
    
    # 7. 查看保存的文件
    for folder in ["dialogue_files", "reasoning_files", "summary_files"]:
        if os.path.exists(folder):
            files = os.listdir(folder)
            print(f"  {folder}/: {len(files)} 个文件")

# 运行完整工作流程
complete_workflow()
```

### 2. 数据分析脚本

```python
def analyze_results():
    """分析处理结果"""
    import json
    import os
    
    # 统计各类型文件数量
    file_stats = {}
    folders = ["dialogue_files", "reasoning_files", "summary_files", 
               "modification_files", "original_files"]
    
    for folder in folders:
        if os.path.exists(folder):
            files = os.listdir(folder)
            file_stats[folder] = len(files)
    
    print("文件统计:")
    for folder, count in file_stats.items():
        print(f"  {folder}: {count} 个文件")
    
    # 分析对话内容
    if os.path.exists("dialogue_files"):
        dialogue_files = os.listdir("dialogue_files")
        total_turns = 0
        
        for file in dialogue_files[:5]:  # 分析前5个文件
            with open(os.path.join("dialogue_files", file), 'r', encoding='utf-8') as f:
                data = json.load(f)
                total_turns += len(data)
        
        avg_turns = total_turns / len(dialogue_files[:5]) if dialogue_files[:5] else 0
        print(f"平均对话轮数: {avg_turns:.1f}")

# 运行分析
analyze_results()
```

### 3. 批量重处理脚本

```python
def reprocess_failed_files():
    """重新处理失败的文件"""
    from refactored_counseling_system.file_utils import get_processing_log
    
    # 获取处理日志
    processing_log = get_processing_log()
    processed_files = processing_log.get_processed_files()
    
    # 获取所有患者档案
    import os
    all_files = os.listdir("patient_profiles")
    
    # 找出未处理的文件
    unprocessed_files = [f for f in all_files if f not in processed_files]
    
    print(f"未处理的文件: {len(unprocessed_files)}")
    for file in unprocessed_files:
        print(f"  - {file}")
    
    # 重新处理
    if unprocessed_files:
        app = CounselingSystemApp()
        results = app.process_patient_folder_concurrent(
            folder_path="patient_profiles",
            max_workers=3
        )
        print(f"重新处理完成: {results['processed']} 个文件")

# 运行重处理
reprocess_failed_files()
```

## 最佳实践

### 1. 性能优化

- **合理设置并发数**: 根据系统性能和API限制调整 `max_workers`
- **监控资源使用**: 定期检查CPU和内存使用情况
- **分批处理**: 对于大量文件，考虑分批处理

### 2. 错误处理

- **验证系统状态**: 在处理前验证系统配置
- **记录错误日志**: 详细记录错误信息便于调试
- **优雅降级**: 单个文件失败不影响整体处理

### 3. 文件管理

- **定期清理**: 定期清理临时文件和日志
- **备份重要数据**: 定期备份重要的会话结果
- **监控磁盘空间**: 确保有足够的存储空间

### 4. 安全考虑

- **保护API密钥**: 不要在代码中硬编码API密钥
- **数据隐私**: 确保患者信息的隐私保护
- **访问控制**: 限制对敏感数据的访问

## 常见问题

### Q: 如何处理API限制问题？
A: 减少并发数，增加重试机制，使用多个API密钥轮换。

### Q: 如何提高处理速度？
A: 增加并发数，使用更快的网络连接，优化系统配置。

### Q: 如何处理大文件？
A: 分批处理，增加内存配置，使用流式处理。

### Q: 如何备份数据？
A: 定期复制重要文件夹，使用版本控制系统，创建数据快照。

---

**提示**: 建议在使用前先在测试环境中验证功能，确保配置正确。 