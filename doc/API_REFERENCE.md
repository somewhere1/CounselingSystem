# API 参考文档

## 核心类和方法

### CounselingSystemApp

主要的应用类，提供心理咨询系统的核心功能。

#### 构造函数
```python
app = CounselingSystemApp()
```

#### 方法

##### run_single_session()
运行单个心理咨询会话。

```python
def run_single_session(self, 
                      patient_info: str,
                      filename: str,
                      is_first_session: bool = True,
                      conversation_mode: str = ConversationMode.PATIENT_FIRST) -> Dict[str, Any]:
```

**参数:**
- `patient_info` (str): 患者信息描述
- `filename` (str): 保存结果的文件名（不含扩展名）
- `is_first_session` (bool): 是否为首次会话，默认True
- `conversation_mode` (str): 对话模式，默认患者先发言

**返回:**
- `Dict[str, Any]`: 包含会话结果的字典

**示例:**
```python
results = app.run_single_session(
    patient_info="患者：张三，28岁，工作压力大...",
    filename="zhang_san",
    is_first_session=True,
    conversation_mode=ConversationMode.PATIENT_FIRST
)
```

##### process_patient_folder()
串行处理患者档案文件夹。

```python
def process_patient_folder(self, 
                         folder_path: str,
                         is_first_session: bool = True,
                         conversation_mode: str = ConversationMode.PATIENT_FIRST) -> Dict[str, Any]:
```

**参数:**
- `folder_path` (str): 患者档案文件夹路径
- `is_first_session` (bool): 是否为首次会话
- `conversation_mode` (str): 对话模式

**返回:**
- `Dict[str, Any]`: 处理结果统计

##### process_patient_folder_concurrent()
并发处理患者档案文件夹。

```python
def process_patient_folder_concurrent(self, 
                                    folder_path: str,
                                    max_workers: int = 3,
                                    is_first_session: bool = True,
                                    conversation_mode: str = ConversationMode.PATIENT_FIRST) -> Dict[str, Any]:
```

**参数:**
- `folder_path` (str): 患者档案文件夹路径
- `max_workers` (int): 最大并发线程数，默认3
- `is_first_session` (bool): 是否为首次会话
- `conversation_mode` (str): 对话模式

**返回:**
- `Dict[str, Any]`: 处理结果统计

##### validate_system()
验证系统配置和连接状态。

```python
def validate_system(self) -> Dict[str, Any]:
```

**返回:**
- `Dict[str, Any]`: 验证结果

##### get_system_status()
获取系统状态信息。

```python
def get_system_status(self) -> Dict[str, Any]:
```

**返回:**
- `Dict[str, Any]`: 系统状态信息

### ConversationSession

管理单个心理咨询会话的类。

#### 构造函数
```python
session = ConversationSession(
    patient_info: str,
    is_first_session: bool = True,
    conversation_mode: str = ConversationMode.PATIENT_FIRST
)
```

#### 方法

##### run_full_session()
运行完整的会话流程。

```python
def run_full_session(self) -> Dict[str, Any]:
```

**返回:**
- `Dict[str, Any]`: 完整的会话结果

##### start_session()
开始会话。

```python
def start_session(self) -> str:
```

**返回:**
- `str`: 开场白

##### get_next_response()
获取下一个回复。

```python
def get_next_response(self) -> Tuple[str, str, AgentResponse]:
```

**返回:**
- `Tuple[str, str, AgentResponse]`: (角色, 内容, 响应对象)

### LLMClient

管理LLM客户端连接的类。

#### 方法

##### generate_response()
生成回复。

```python
def generate_response(self, 
                    model: str, 
                    messages: List[Dict], 
                    temperature: Optional[float] = None,
                    return_reasoning: bool = False) -> Tuple[str, str]:
```

**参数:**
- `model` (str): 模型名称
- `messages` (List[Dict]): 消息列表
- `temperature` (Optional[float]): 温度参数
- `return_reasoning` (bool): 是否返回推理过程

**返回:**
- `Tuple[str, str]`: (回复内容, 推理过程)

##### validate_connection()
验证API连接。

```python
def validate_connection(self) -> Dict[str, bool]:
```

**返回:**
- `Dict[str, bool]`: 各API连接状态

### SessionDataManager

管理会话数据保存和加载的类。

#### 方法

##### save_session_results()
保存会话结果到文件。

```python
def save_session_results(self, 
                       filename: str, 
                       dialogue_history: List[Dict],
                       reasoning_history: List[Dict],
                       summary_history: List[str],
                       modification_history: List[Dict],
                       original_history: List[Dict],
                       reasoning_history_by_round: Optional[List[Dict]] = None) -> bool:
```

**参数:**
- `filename` (str): 基础文件名
- `dialogue_history` (List[Dict]): 对话历史
- `reasoning_history` (List[Dict]): 推理历史
- `summary_history` (List[str]): 摘要历史
- `modification_history` (List[Dict]): 修改历史
- `original_history` (List[Dict]): 原始历史
- `reasoning_history_by_round` (Optional[List[Dict]]): 按轮次分组的推理历史

**返回:**
- `bool`: 保存是否成功

##### load_session_results()
从文件加载会话结果。

```python
def load_session_results(self, filename: str) -> Optional[Dict[str, Any]]:
```

**参数:**
- `filename` (str): 文件名

**返回:**
- `Optional[Dict[str, Any]]`: 会话数据或None

## 配置类

### config.system

系统配置参数。

```python
class SystemConfig:
    MAX_DIALOGUE_LENGTH = 70
    MAX_MODIFICATION_ATTEMPTS = 3
    LOG_FILE = "processed_file.log"
    CBT_WITH_SUGGESTION_THRESHOLD = 100
    CBT_WITHOUT_SUGGESTION_THRESHOLD = 200
```

### config.model

模型配置参数。

```python
class ModelConfig:
    CONVERSATION_MODEL = "qwen-turbo"
    REASONING_MODEL = "qwen-turbo"
    SUMMARY_MODEL = "qwen-turbo"
    DEFAULT_TEMPERATURE = 0.8
```

### config.api

API配置参数。

```python
class APIConfig:
    ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")
    QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
    MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY", "")
    OPENAI_PROXY_API_KEY = os.getenv("OPENAI_PROXY_API_KEY", "")
    OPENAI_PROXY_BASE_URL = os.getenv("OPENAI_PROXY_BASE_URL", "")
```

## 枚举类

### ConversationMode

对话模式枚举。

```python
class ConversationMode:
    PATIENT_FIRST = "patient_first"  # 患者先发言
    DOCTOR_FIRST = "doctor_first"    # 咨询师先发言
```

## 数据结构

### 会话结果结构

```python
{
    "dialogue_history": [  # 对话历史
        {"求助者": "我最近感到很焦虑..."},
        {"咨询师": "我理解你的感受..."}
    ],
    "session_data": {  # 会话数据
        "reasoning_history": [...],  # 推理历史
        "reasoning_history_by_round": [...],  # 按轮次分组的推理
        "summary_history": [...],  # 摘要历史
        "modification_history": [...],  # 修改历史
        "original_dialogue_history": [...]  # 原始对话
    },
    "statistics": {  # 统计信息
        "total_turns": 10,
        "reasoning_evaluations": 5
    },
    "session_summary": {  # 会话摘要
        "ended_with_goodbye": True,
        "final_summary": "..."
    }
}
```

### 处理结果结构

```python
{
    "total_files": 100,  # 总文件数
    "processed": 95,      # 成功处理数
    "skipped": 3,         # 跳过文件数
    "errors": 2,          # 错误数
    "session_results": {   # 会话结果
        "patient_001": {...},
        "patient_002": {...}
    },
    "concurrent_workers": 3  # 并发线程数
}
```

## 错误处理

### 常见异常

#### LLMClientError
LLM客户端错误。

```python
from refactored_counseling_system.llm_client import LLMClientError

try:
    response = client.generate_response(...)
except LLMClientError as e:
    print(f"LLM客户端错误: {e}")
```

#### 配置错误
配置参数错误。

```python
try:
    app = CounselingSystemApp()
except Exception as e:
    print(f"配置错误: {e}")
```

### 错误处理最佳实践

```python
def safe_session_run(app, patient_info, filename):
    """安全的会话运行函数"""
    try:
        # 验证系统
        validation = app.validate_system()
        if not validation.get("overall_status", False):
            print("系统验证失败")
            return None
        
        # 运行会话
        results = app.run_single_session(
            patient_info=patient_info,
            filename=filename
        )
        
        return results
        
    except Exception as e:
        print(f"会话运行失败: {e}")
        # 记录错误日志
        import logging
        logging.error(f"会话错误: {e}")
        return None
```

## 工具函数

### 全局函数

#### get_llm_client()
获取全局LLM客户端实例。

```python
from refactored_counseling_system.llm_client import get_llm_client

client = get_llm_client()
```

#### get_session_data_manager()
获取全局会话数据管理器。

```python
from refactored_counseling_system.file_utils import get_session_data_manager

manager = get_session_data_manager()
```

#### get_processing_log()
获取全局处理日志管理器。

```python
from refactored_counseling_system.file_utils import get_processing_log

log = get_processing_log()
```

## 示例代码

### 基本使用示例

```python
from refactored_counseling_system import CounselingSystemApp, ConversationMode

# 初始化应用
app = CounselingSystemApp()

# 验证系统
validation = app.validate_system()
if not validation.get("overall_status", False):
    print("系统验证失败")
    exit()

# 运行单个会话
patient_info = "患者：张三，28岁，工作压力大..."
results = app.run_single_session(
    patient_info=patient_info,
    filename="zhang_san",
    is_first_session=True,
    conversation_mode=ConversationMode.PATIENT_FIRST
)

# 查看结果
print(f"对话轮数: {results['statistics']['total_turns']}")
print(f"推理次数: {results['statistics'].get('reasoning_evaluations', 0)}")
```

### 批量处理示例

```python
# 并发处理多个患者
results = app.process_patient_folder_concurrent(
    folder_path="patient_profiles",
    max_workers=3,
    is_first_session=True,
    conversation_mode=ConversationMode.PATIENT_FIRST
)

print(f"处理完成:")
print(f"  总文件: {results['total_files']}")
print(f"  成功: {results['processed']}")
print(f"  跳过: {results['skipped']}")
print(f"  错误: {results['errors']}")
```

### 自定义配置示例

```python
from refactored_counseling_system import config

# 修改系统配置
config.system.MAX_DIALOGUE_LENGTH = 50
config.system.MAX_MODIFICATION_ATTEMPTS = 5

# 修改模型配置
config.model.CONVERSATION_MODEL = "qwen-turbo"
config.model.DEFAULT_TEMPERATURE = 0.7

# 重新初始化应用
app = CounselingSystemApp()
```

---

**注意**: 所有API方法都包含详细的类型注解和文档字符串，建议使用IDE的自动补全功能来获得更好的开发体验。 