from typing import Callable

from pydantic import BaseModel, Field

from .base import BaseTool


class FeedbackParams(BaseModel):
    content: str = Field(
        ..., description="The content to be presented for human feedback"
    )


def _print_func(llm_question: str) -> None:
    """Default way to show llm question when llm using HumanFeedBackTool."""
    print(f"[Agent ask] {llm_question}")


class HumanFeedBackTool(BaseTool):
    """A tool for human feedback"""

    name: str = "human_feedback"
    description: str = (
        "Human feedback tools are used to collect human feedback information."
        "Please only use this tool in situations where relevant contextual information"
        "is lacking or reasoning cannot continue. Please enter the content you wish for"
        "human feedback and interaction, but do not ask for knowledge or let humans reason."  # noqa
    )
    parameters = FeedbackParams

    def __init__(
        self,
        output_func: Callable[[str], None] = _print_func,
        input_func: Callable[[], str] = lambda: input("input> "),
        *args,
        **kwargs,
    ):
        """
        :param output_func: 发送反馈内容给用户
        :param input_func: 获取人类反馈的结果
        """
        super().__init__(*args, **kwargs)
        self.output_func = output_func
        self.input_func = input_func

    def _run(self, content: str, *args, **kwargs) -> str:
        self.output_func(content)
        return self.input_func()
