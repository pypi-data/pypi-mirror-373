import re

from duowen_agent.agents.component.base import BaseComponent
from duowen_agent.llm import MessagesSet
from duowen_agent.llm.chat_model import BaseAIChat
from duowen_agent.utils.core_utils import stream_to_string, remove_think


class PythonCodeRepair(BaseComponent):
    def __init__(self, llm_instance: BaseAIChat, **kwargs):
        super().__init__(**kwargs)
        self.llm_instance = llm_instance
        self.kwargs = kwargs

    @staticmethod
    def build_prompt() -> MessagesSet:
        return MessagesSet().add_system(
            """修复用户提供的Python代码中的执行错误，仅修改错误相关部分，保持其他代码不变，并全量返回修正后的完整代码。

# 任务要求
1. **最小修改原则**：仅修改导致执行错误的代码行或相关片段  
2. **保持原样**：不优化代码风格/性能，不改动注释，不添加新功能  
3. **完整输出**：返回整个.py文件的完整内容，包括未修改部分  
4. **无解释说明**：输出仅包含Python代码，不添加任何注释或说明文字  

# 处理流程
1. 解析错误信息，精确定位错误代码位置  
2. 识别错误类型（语法/运行时/逻辑错误等）  
3. 实施最低限度修改：  
   - 语法错误：修正缺少的符号（冒号/括号/引号等）  
   - 变量错误：修正未定义或拼写错误的变量  
   - 导入错误：添加缺失的import语句  
   - 类型错误：添加必要类型转换  
   - 索引错误：修正越界访问  
4. 保持文件原有结构（缩进/注释/空行等）  

# 输出格式
返回修正后的完整Python代码（纯文本格式），要求：  
- 首行无空行  
- 保留原始注释和格式  
- 文件结尾不带额外空行  
- 禁用```代码块标记  

# 示例
用户输入：
```python
# 计算阶乘
def factorial(n):
    if n == 0
        return 1
    else:
        return n * factorial(n-1)
    
print(factorial(5))
```
错误：`SyntaxError: expected ':'`

输出：
```python
# 计算阶乘
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)
    
print(factorial(5))
```

# 注意事项
1. 当错误涉及多行时（如括号未闭合），仅修改相关行  
2. 变量名冲突时保持原始命名规范  
3. 运行时错误优先确保通过执行，不深层修复逻辑缺陷  
4. 完全保留未被错误影响的代码段"""
        )

    @staticmethod
    def _extract_python_code(markdown_string: str) -> str:
        # Strip whitespace to avoid indentation errors in LLM-generated code
        markdown_string = markdown_string.strip()

        # Regex pattern to match Python code blocks
        pattern = r"```[\w\s]*python\n([\s\S]*?)```|```([\s\S]*?)```"

        # Find all matches in the markdown string
        matches = re.findall(pattern, markdown_string, re.IGNORECASE)

        # Extract the Python code from the matches
        python_code = []
        for match in matches:
            python = match[0] if match[0] else match[1]
            python_code.append(python.strip())

        if len(python_code) == 0:
            return markdown_string

        return python_code[0]

    def run(self, question: str, *args, **kwargs) -> str:
        _prompt = self.build_prompt()
        _prompt.add_user(question)
        res = stream_to_string(self.llm_instance.chat_for_stream(_prompt))
        res = remove_think(res)
        return self._extract_python_code(res)
