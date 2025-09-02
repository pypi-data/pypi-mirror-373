# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT
import logging
from typing import List, Callable

from duowen_agent.deep_research.config.configuration import Configuration
from duowen_agent.deep_research.types import State
from duowen_agent.llm.chat_model import BaseAIChat
from duowen_agent.tools.base import BaseTool
from .builder import build_graph


def run_agent_workflow(
    llm: BaseAIChat,
    initial_state: dict,
    config: dict,
    researcher_tools: List[BaseTool],
    coder_tools: List[BaseTool],
    human_feedback_tools: BaseTool,
    background_investigation_tools: List[BaseTool],
    is_interrupt: Callable[[], bool] = None,  # 外部中断函数
    background_investigation_prompt: str = None,
    planner_prompt: str = None,
    researcher_prompt: str = None,
    coder_prompt: str = None,
    reporter_prompt: str = None,
):
    logging.info("workflow start")
    graph = build_graph(
        llm=llm,
        researcher_tools=researcher_tools,
        coder_tools=coder_tools,
        human_feedback_tools=human_feedback_tools,
        background_investigation_tools=background_investigation_tools,
        is_interrupt=is_interrupt,
        background_investigation_prompt=background_investigation_prompt,
        planner_prompt=planner_prompt,
        researcher_prompt=researcher_prompt,
        coder_prompt=coder_prompt,
        reporter_prompt=reporter_prompt,
    )

    for s in graph.stream(input=initial_state, config=config, stream_mode="custom"):
        if is_interrupt and is_interrupt():
            raise InterruptedError("用户终止")
        yield s

    logging.info("workflow completed successfully")
