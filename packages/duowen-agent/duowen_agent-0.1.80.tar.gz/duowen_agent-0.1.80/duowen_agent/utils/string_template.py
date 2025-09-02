import datetime
import re
from typing import List

from jinja2 import Environment, meta
from jinja2.sandbox import SandboxedEnvironment
from typing_extensions import Literal


def _get_jinja2_variables(template: str) -> List[str]:
    env = Environment()
    ast = env.parse(template)
    variables = meta.find_undeclared_variables(ast)
    return list(variables)


def _jinja2_format(template: str, **kwargs) -> str:
    return SandboxedEnvironment().from_string(template).render(**kwargs)


class StringTemplate:
    """String Template for llm. It can generate a complex prompt."""

    def __init__(
        self, template: str, template_format: Literal["f-string", "jinja2"] = "f-string"
    ):
        self.template: str = template
        self.template_format: str = template_format
        self.variables: List[str] = []

        if template_format == "f-string":
            self.variables = re.findall(r"\{(\w+)\}", self.template)
        elif template_format == "jinja2":
            self.variables = _get_jinja2_variables(template)
        else:
            raise ValueError(
                f"template_format must be one of 'f-string' or 'jinja2'. Got: {template_format}"
            )

    def format(self, **kwargs) -> str:
        """Enter variables and return the formatted string."""

        current_date = datetime.date.today()

        # 获取星期几
        weekday = current_date.strftime("%A")

        # 中文星期几
        weekday_zh = {
            "Monday": "星期一",
            "Tuesday": "星期二",
            "Wednesday": "星期三",
            "Thursday": "星期四",
            "Friday": "星期五",
            "Saturday": "星期六",
            "Sunday": "星期日",
        }

        formatted_date = (
            current_date.strftime("今天是%Y年%m月%d日，") + weekday_zh[weekday] + "。"
        )

        time_defaults = {
            "_currentYear_": current_date.year,
            "_currentMonth_": current_date.month,
            "_currentDay_": current_date.day,
            "_formattedDay_": formatted_date,
        }

        for key, value in time_defaults.items():
            if key not in kwargs:
                kwargs[key] = value

        if self.template_format == "f-string":
            return self.template.format(**kwargs)
        elif self.template_format == "jinja2":
            return _jinja2_format(self.template, **kwargs)
