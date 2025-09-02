import math
import re

from pydantic import BaseModel, Field

from duowen_agent.llm import OpenAIChat
from duowen_agent.prompt.prompt_build import GeneralPromptBuilder
from .base import BaseTool
from ..error import ObserverException, ToolError
from ..utils.core_utils import json_observation, remove_think, stream_to_string


class Expression(BaseModel):
    expression: str = Field(description="the expression need to calculate")


prompt = GeneralPromptBuilder(
    instruction="You are provided a math problem, you should transalte it into a math expression.",
    output_format=Expression,
    sample="""## sample_1
Question: What is 37593 * 67?

Output:
```json
{"expression": "37593 * 67"}
```

## sample_2
Question: What is 37593^(1/5)?

Output:
```json
{"expression": "37593**(1/5)"}
```
""",
    note="""
- Built-in mathematical constants：pi、e
- Built-in mathematical functions：sqrt、 exp、 log、 log10、 sin、 cos、 tan、 abs 、arcsin、 arccos、 arctan 、sinh、 cosh、 tanh、 arctanh、 log1p、 factorial""",
)


def _evaluate_expression(expression: str) -> str:
    """
    使用原生 Python 实现数学表达式计算（替代 numexpr）

    改造点：
    1. 替换 ^ 为 ** 以支持 Python 的指数语法
    2. 使用 eval() 配合安全限制的符号表
    3. 添加常用数学函数和常量（如 sqrt, pi 等）
    """
    # 预处理表达式：替换 ^ 为 **
    expr = re.sub(r"\^", "**", expression.strip())
    expr = re.sub(r"(\d+)!", r"math.factorial(\1)", expr)

    # 构建安全符号表（仅允许数学相关函数和常量）
    safe_dict = {
        # 数学常量
        "pi": math.pi,
        "e": math.e,
        # 数学函数
        "sqrt": math.sqrt,
        "exp": math.exp,
        "log": math.log,
        "log10": math.log10,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "abs": abs,
        # 补充反三角函数
        "arcsin": math.asin,
        "arccos": math.acos,
        "arctan": math.atan,
        # 补充双曲函数
        "sinh": math.sinh,
        "cosh": math.cosh,
        "tanh": math.tanh,
        # 可选补充
        "arctanh": math.atanh,
        "log1p": math.log1p,
        "factorial": math.factorial,
        # 保留字（避免变量注入）
        "__builtins__": None,  # 禁用所有内置函数
    }

    try:
        # 使用 eval 计算表达式
        result = eval(expr, {"__builtins__": None}, safe_dict)
        return str(result)
    except Exception as e:
        raise ToolError(
            f'Calculator._evaluate_expression("{expression}") raised error: {e}.'
            " Please try again with a valid numerical expression"
        )


def _is_valid_expression(expression: str) -> bool:
    """检查表达式是否合法（改造后不再依赖 numexpr）"""
    try:
        _evaluate_expression(expression)
        return True
    except ValueError:
        return False


class Calculator(BaseTool):
    """
    A Math operator.

    This class is a tool for evaluating mathematical expressions. It uses the
    _evaluate_expression and _is_valid_expression functions to evaluate expressions
    and check their validity. It also uses the BaseLLM class to generate prompts
    for the user.

    Attributes:
        name (str): The name of the tool.
        description (str): A description of the tool.
        llm (BaseLLM): An instance of the BaseLLM class.
    """

    name: str = "math-calculator"
    description: str = (
        "Useful for when you need to answer questions about math.You input is a nature"
        "language of math expression. Attention: Expressions can not exist variables!"
        "eg: (current age)^0.43 is wrong, you should use 18^0.43 instead."
    )

    parameters = Expression

    def __init__(self, llm: OpenAIChat, **kwargs):
        """
        Initialize the Calculator class.

        This method initializes the Calculator class with an instance of the BaseLLM
        class and any additional keyword arguments.

        Args:
            llm (BaseLLM, optional): An instance of the BaseLLM class. Defaults to None.
        """
        super().__init__(**kwargs)
        self.llm = llm

    def _run(self, expression: str) -> str:
        """
        Run the Calculator tool.

        This method takes a prompt from the user, checks if it is a valid expression,
        and evaluates it if it is. If it is not a valid expression, it generates a
        new prompt using the BaseLLM class and evaluates the resulting expression.

        Args:
            expression (str): The math problem of user.

        Returns:
            str: The result of the evaluation.

        Raises:
            ValueError: If the evaluation fails.
        """
        if _is_valid_expression(expression):
            return _evaluate_expression(expression)

        llm_output = "Unset"

        try:
            _prompt = prompt.get_instruction(user_input=f"Question: {expression}")
            llm_output: str = stream_to_string(self.llm.chat_for_stream(_prompt))
            res = json_observation(llm_output, Expression)
            return _evaluate_expression(res.expression)
        except ObserverException as e:
            raise ToolError(str(e))
        except Exception as e:
            raise ToolError(
                f"Unknown format from LLM: {remove_think(llm_output)}, error: {e}"
            )


def calculator(expression: str):
    """Evaluate a mathematical expression.

    This function takes a string expression, evaluates it like `numexpr.evaluate`,
    and returns the result as a string. It also handles exceptions and raises a
    ValueError with a custom error message if the evaluation fails.

    Args:
        expression: A mathematical expression, eg: 18^0.43

    Attention:
        Expressions can not exist variables!
        bad example: (current age)^0.43, (number)^(1/5)
        good example: 18^0.43, 37593**(1/5)

    Returns:
        The result of the evaluation.
    """
    return _evaluate_expression(expression)
