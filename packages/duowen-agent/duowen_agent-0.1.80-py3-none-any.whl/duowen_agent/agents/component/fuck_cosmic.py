from pathlib import Path

from duowen_agent.agents.component.base import BaseComponent
from duowen_agent.llm import MessagesSet
from duowen_agent.llm.chat_model import BaseAIChat
from duowen_agent.utils.core_utils import stream_to_string, remove_think


def get_all_files(root_dir):
    """使用pathlib递归获取目录下所有文件的路径列表"""
    root_path = Path(root_dir)
    # 使用rglob递归匹配所有文件
    return [str(file) for file in root_path.rglob("*") if file.is_file()]


def read_file(file_path: str) -> str:
    with open(file_path, "r") as f:
        return f.read()


def read_code_dir(
    file_path: str, endswith: list[str] = None, exclude: list[str] = None
) -> dict[str, str]:

    data = {}
    for i in get_all_files(file_path):

        if exclude and any([ext in i for ext in exclude]):
            continue

        if endswith and not any([i.endswith(ext) for ext in endswith]):
            continue

        try:
            data[i] = read_file(i)
        except:
            pass
    return data


class CodeExplain(BaseComponent):
    """ """

    def __init__(self, llm_instance: BaseAIChat, **kwargs):
        super().__init__(**kwargs)
        self.llm_instance = llm_instance
        self.kwargs = kwargs
        self._system_prompt = """对代码文件进行全面结构化摘要，输出包含文件概要的Markdown文档

**摘要要求：**
1. **语言支持**：自动识别并适配Go/Java/Python/JavaScript/TypeScript语法  
2. **核心要素**：
   - ⭐ **文件概要**（100字以内核心功能概述）
   - 文件路径与基础信息（语言类型、行数）
   - 模块/包声明
   - 依赖项导入（精确到具体对象）
   - 类/结构体定义（包含继承关系）
   - 接口/协议声明
   - 函数/方法清单（含参数类型、返回值类型）
   - 关键常量与全局变量
   - 主要控制流逻辑（用自然语言简述）  
3. **深度要求**：
   - 识别装饰器（Python/TS）、注解（Java）、标签（Go）
   - 标注异步方法（async/await/Promise）
   - 提取泛型类型参数（TS/Go/Java）
   - 记录异常处理机制（try-catch/throws）

**处理规范：**
- 文件概要置于标题下方首行，用`> [!NOTE]`高亮显示
- 对>500行代码优先摘要核心结构
- 忽略具体实现细节，聚焦架构设计
- 用`>` 引用重要代码片段（不超过3行）
- 保留原始符号命名（不转义特殊字符）

**输出格式：**
```markdown
# [文件名].[后缀]
**路径**: `[完整文件路径]`  
**语言**: [检测到的语言] | **行数**: [代码行数]
> [!NOTE]
> ⭐ 文件概要：[50字以内功能概述]

## 依赖项
- `import [包路径]` → 使用对象: {类/函数}

## 数据结构
### [类名/结构体名]
- 继承: [父类] | 实现: [接口]
- 字段:  
  `[修饰符][类型] [字段名]`  
  ...

## 接口
### [接口名]
- 方法:  
  `[返回值] [方法名]([参数列表])`

## 函数
### [函数名]
- 作用域: [public/private]
- 参数: `[类型] [参数名]`
- 返回: `[类型]`
- 逻辑摘要: [1句话说明核心流程]
```

**示例片段：**
```markdown
# utils.py
**路径**: `/src/helpers/utils.py`  
**语言**: Python | **行数**: 127
> [!NOTE]
> ⭐ 文件概要：提供时间转换和目录扫描工具函数集合

## 依赖项
- `import os` → 使用对象: {path.join, listdir}
- `from datetime import datetime` → 使用对象: {datetime}

## 函数
### format_timestamp
- 作用域: public
- 参数: `datetime dt`, `str fmt="%Y%m%d"`
- 返回: `str`
- 逻辑摘要: 将datetime对象转换为指定格式字符串

### scan_directory
- 作用域: private
- 参数: `str path`
- 返回: `List[str]`
- 逻辑摘要: 递归扫描目录返回文件路径列表，跳过隐藏文件
```

**注意事项：**
1. 文件概要需满足：  
   - 概括性：避免具体函数细节  
   - 功能性：说明模块核心价值  
   - 独立性：不依赖其他模块说明  
2. 对TSX/JSX文件额外解析组件树  
3. Java需记录`@Override`/`@FunctionalInterface`等注解  
4. Go需标注`goroutine`使用和`channel`操作  
5. 若检测到测试文件，在标题追加`[TEST]`标识"""

    def run(self, code_path: str, code: str = None) -> str:
        if not code:
            with open(code_path, "r") as f:
                _code = f.read()
        else:
            _code = code
        _prompt = MessagesSet().add_system(self._system_prompt)
        _prompt.add_user(f"文件路径: {code_path}\n\n文件内容:\n{_code}")
        return remove_think(
            stream_to_string(self.llm_instance.chat_for_stream(_prompt))
        )


class FeaturePointSplitter(BaseComponent):

    def __init__(self, llm_instance: BaseAIChat, **kwargs):
        super().__init__(**kwargs)
        self.llm_instance = llm_instance
        self._system_prompt = f"""分析提供的一批代码摘要内容，深入理解系统功能，生成一个层次化的功能拆分结构，使用Markdown格式，按一级到五级延伸。

### 步骤
1. **摘要内容分析**：
   - 仔细阅读每个代码摘要，识别核心功能、组件和关键操作。
   - 提取摘要中的术语、模块和行为描述。
2. **联系分析**：
   - 比较摘要之间的依赖关系、数据流动或功能重叠。
   - 识别模式：如共享模块、调用链或层级继承。
3. **系统整体理解**：
   - 综合摘要内容，推断系统的主要目标、范围和架构。
   - 基于分析，抽象出系统功能的顶层分类。
4. **功能拆分生成**：
   - 构建层次结构：从一级（整体功能）开始，逐级分解到五级（细节实现）。
   - 每个功能点名称应简洁；说明用一句话概括角色和行为。
   - 确保层级一致：高级点逻辑包含低级点，且延伸到五级。
   - 基于实际摘要内容推导功能点，避免猜测。

### 输出格式
- 严格遵守用户指定的Markdown结构：
  - `# 一级功能点名称`
  - `一级功能点说明（一句话说明）`
  - `## 二级功能点名称`
  - `二级功能点说明（一句话说明）`
  - `### 三级功能点名称`
  - `三级功能点说明（一句话说明）`
  - `#### 四级功能点名称`
  - `四级功能点说明（一句话说明）`
  - `##### 五级功能点名称`
  - `五级功能点说明（一句话说明）`
  - `##### 六级功能点名称`
  - `六级功能点说明（一句话说明）`
- 输出为一个连贯的Markdown文档，从一级开始逐级展开。
- 根据系统复杂度，一个一级功能点可能连接多个二级点，延续到六级；功能点数目基于实际摘要内容调整。

### 例子
（基于示例摘要输入：[摘要1: 用户登录认证模块，包括验证用户凭证和生成会话]。）
输出：
```
# 用户认证
处理用户身份的验证和访问控制

## 登录流程
实现用户输入到系统访问的全过程

### 凭证验证
检查用户名和密码的有效性

#### 输入验证
处理用户输入的格式和基本检查

##### 密码强度检查
通过算法评估密码是否符合安全标准
```
（实际输出必须基于输入摘要内容构建更长链条；示例较短时，需扩展到多组功能点以覆盖六级。）

### 注意事项
- **延伸到六级**：如果摘要内容不足，必须通过合理推断添加细节（真实场景示例应更详细）。
- **内容依赖性**：功能点名称和说明必须源自摘要内容，不引入外部假设。摘要内容使用文字描述，不使用代码或假设。
- **格式精度**：只使用指定Markdown标题级别；避免额外注释或空行。
- **错误处理**：如果摘要矛盾或模糊，优先标注不确定性但生成完整结构。"""

    def run(self, content: str) -> str:
        _prompt = MessagesSet().add_system(self._system_prompt)
        _prompt.add_user(f"代码摘要如下:\n\n{content}")
        return remove_think(
            stream_to_string(self.llm_instance.chat_for_stream(_prompt))
        )
