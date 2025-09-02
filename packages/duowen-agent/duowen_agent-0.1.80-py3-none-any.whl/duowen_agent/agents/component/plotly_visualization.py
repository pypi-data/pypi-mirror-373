import json
import re
import traceback
from typing import Optional

import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
from pandas import DataFrame
from pydantic import BaseModel, Field, ConfigDict

from duowen_agent.llm import MessagesSet
from duowen_agent.utils.core_utils import stream_to_string, remove_think
from .base import BaseComponent
from .code_repair import PythonCodeRepair
from ...llm.chat_model import BaseAIChat


def generate_dataframe_metadata(df: pd.DataFrame) -> dict:
    """生成 DataFrame 的元数据字典，供模型理解"""
    metadata = {
        "shape": {"rows": df.shape[0], "columns": df.shape[1]},
        "columns": [],
        "stats": {},
    }

    # 列元数据
    for col in df.columns:
        col_meta = {
            "name": col,
            "dtype": str(df[col].dtype),
            "missing_values": int(df[col].isna().sum()),
            "unique_values": int(df[col].nunique()),
            "example_values": df[col].dropna().head(5).tolist(),
        }
        metadata["columns"].append(col_meta)

    # 数值列统计信息
    numeric_cols = df.select_dtypes(include="number").columns
    if not numeric_cols.empty:
        stats = df[numeric_cols].describe().round(2).to_dict()
        metadata["stats"] = stats

    return metadata


class VisualizationModel(BaseModel):
    figure: Optional[plotly.graph_objs.Figure | None] = Field(
        None, description="图表对象"
    )
    question: Optional[str] = Field(None, description="用户问题")
    sql: Optional[str] = Field(None, description="SQL查询")
    df: Optional[pd.DataFrame] = Field(None, description="数据结果")
    code: Optional[str] = Field(None, description="生成的代码")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # def to_image(self, format="png", width=720, height=330, **kwargs):
    #     if self.figure is None:
    #         raise ValueError("figure is None")
    #     plotly.io.defaults.mathjax = None  # 禁用 mathjax
    #     return self.figure.to_image(
    #         format=format, width=width, height=height, **kwargs
    #     )  # engine="kaleido"
    #

    # def to_html(self, **kwargs):
    #     if self.figure is None:
    #         raise ValueError("figure is None")
    #     return self.figure.to_html(
    #         include_plotlyjs=False, include_mathjax=False, **kwargs
    #     )


class PlotlyVisualization(BaseComponent):
    """需要 执行 plotly_get_chrome 用于图片生成"""

    def __init__(self, llm_instance: BaseAIChat, **kwargs):
        super().__init__(**kwargs)
        self.llm_instance = llm_instance
        self.kwargs = kwargs

    def submit_prompt(self, prompt: MessagesSet, **kwargs) -> str:
        # print(prompt.get_format_messages())
        resp = remove_think(
            stream_to_string(self.llm_instance.chat_for_stream(prompt, **kwargs))
        )
        # print(resp)
        return resp

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

    @staticmethod
    def _sanitize_plotly_code(raw_plotly_code: str) -> str:
        # Remove the fig.show() statement from the plotly code
        plotly_code = raw_plotly_code.replace("fig.show()", "")
        return plotly_code

    def generate_plotly_code(
        self,
        df: DataFrame,
        question: str = None,
        sql: str = None,
        note: str = None,
        **kwargs,
    ) -> str:

        df_metadata = json.dumps(
            generate_dataframe_metadata(df), ensure_ascii=False, indent=2
        )
        if question is not None:
            _user_prompt = (
                f"以下是包含用户问题 '{question}' 查询结果的 pandas DataFrame"
            )
        else:
            _user_prompt = "以下是一个 pandas DataFrame"

        if sql is not None:
            _user_prompt += f"\n\n该DataFrame由以下SQL查询生成:\n{sql}\n"

        _user_prompt += f"\n以下是DataFrame 'df' 的元数据信息:\n{df_metadata}"

        _user_prompt += "\n以下是DataFrame 'df' 的数据样本:\n"
        _user_prompt += df.head(100).to_markdown(index=False)

        if note is not None:
            _user_prompt += f"\n\n注意事项:\n{note}"

        _prompt = _build_prompt().add_user(_user_prompt)

        plotly_code = self.submit_prompt(_prompt, **kwargs)

        return self._sanitize_plotly_code(self._extract_python_code(plotly_code))

    def _code_repair(self, code, error):
        _code = PythonCodeRepair(self.llm_instance).run(
            f"""
# 运行代码
```python
{code}
```

# 错误日志
```
{error}
```

# 注意事项
- 'df'变量已在环境中定义, 不是错误
"""
        )
        return _code

    def get_plotly_figure(
        self, plotly_code: str, df: pd.DataFrame
    ) -> plotly.graph_objs.Figure:

        ldict = {"df": df, "px": px, "go": go}

        _plotly_code = plotly_code

        def _run_code(plotly_code, ldict):
            try:
                exec(plotly_code, globals(), ldict)
                fig = ldict.get("fig", None)
                return fig
            except Exception as e:
                raise ValueError(
                    f"Error executing Plotly code: {e},traceback: {traceback.format_exc()}"
                )

        fig = None
        for i in range(3):
            try:
                fig = _run_code(_plotly_code, ldict)
            except ValueError as e:
                _plotly_code = self._code_repair(_plotly_code, str(e))
        return fig

    def run(
        self,
        question: str,
        sql: str,
        df: pd.DataFrame,
        **kwargs,
    ) -> VisualizationModel:
        plotly_code = self.generate_plotly_code(
            df=df, question=question, sql=sql, **kwargs
        )
        fig = self.get_plotly_figure(plotly_code, df)

        return VisualizationModel(
            figure=fig, question=question, sql=sql, df=df, code=plotly_code
        )


def _build_prompt():
    _prompt = """生成专业美观的Plotly代码可视化数据。数据存储在名为'df'的pandas DataFrame中（已在环境中定义）。

### 输入数据说明
1. 用户问题：（如提供）
2. SQL查询：（如提供）
3. 元数据信息：（如提供）
4. 数据样本（前100行）：（如提供）


### 核心约束
- ✖️ 禁止定义`df`变量（已存在）
- ✅ 只生成单张图表
- 📊 使用plotly_express或plotly.graph_objects
- 🖥️ Ubuntu Server环境专用设置：
- 中文字体：'DejaVu Sans'或'WenQuanYi Micro Hei'
- 无GUI渲染兼容
- 避免额外字体依赖
- 🔄 Plotly 6.x语法要求：
- 使用最新API方法
- 弃用方法如`plotly.offline.plot`禁止使用
- 输出必须包含`fig.show()`

### 图表设计规范
1. **图表选择**：
- 根据数据特性和用户问题选择最优类型
- 核心原则：清晰传达数据洞察
2. **视觉设计**：
- 主题：`plotly_white`
- 标题：反映用户问题核心
- 坐标轴/图例：完整标签体系
- 色系：Blues柔和方案
- **配色稳定性**（关键强化）  
| 数据类型       | 方案                          | 锁定机制                |
|----------------|-------------------------------|------------------------|
| 离散数据(≤24类) | `qualitative.Dark24`          | 全局常量引用           |
| 离散数据(>24类) | `cyclical.Twilight`           | 循环映射               |

3. **交互功能**：
- 悬停提示显示关键字段
- 支持缩放/平移操作
- 响应式元素尺寸

### 开发流程
1. 分析数据结构（参考元数据/样本）
2. 确定图表类型决策：
```mermaid
graph LR
A[数据特性] --> B{图表选择}
B -->|类别比较| C[柱状图/条形图]
B -->|时间趋势| D[折线图/面积图]
B -->|分布关系| E[散点图/箱线图]
B -->|比例构成| F[饼图/旭日图]
```
3. 设计视觉元素：
- 标题文案：直接关联用户问题
- 颜色映射：离散/连续数据处理
- 中文兼容：全局字体统一设置
4. 代码实现检查：
- 无df重复定义
- 单图表输出
- 完整交互功能
- 无弃用方法

### 输出要求
返回纯Python代码块，禁止任何解释文本。示例格式：
```python
import plotly.express as px
import plotly.graph_objects as go
# 中文兼容设置
font_setting = {'family': 'DejaVu Sans, WenQuanYi Micro Hei'}  

...

fig.show()
```

### 关键注意事项
❗ 当数据包含中文时：
```python
# 必须添加全局字体设置
fig.update_layout(font={'family':'DejaVu Sans, WenQuanYi Micro Hei'})
```
❗ 服务器渲染特殊处理：
```python
# 禁用默认浏览器调用
import plotly.io as pio
pio.renderers.default = 'png' 
```
❗ 返回纯Python代码块，禁止任何解释文本"""

    return MessagesSet().add_system(_prompt)
