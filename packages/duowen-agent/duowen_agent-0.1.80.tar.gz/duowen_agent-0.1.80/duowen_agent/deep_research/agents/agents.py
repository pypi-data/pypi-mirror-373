# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT
from typing import Optional, Callable

from duowen_agent.agents.react import ReactAgent
from duowen_agent.llm.chat_model import BaseAIChat
from ..prompts import apply_prompt_template


# Create agents using configured LLM types
def create_agent(
    llm: BaseAIChat,
    tools: list,
    prompt_template: str,
    agent_prompt: str = None,
    max_iterations: Optional[int] = 15,
    is_interrupt: Callable[[], bool] = None,
) -> ReactAgent:
    """Factory function to create agents with consistent configuration."""

    return ReactAgent(
        llm=llm,
        tools=tools,
        max_iterations=max_iterations,
        prefix_prompt=agent_prompt
        or apply_prompt_template(prompt_template)[0]["content"],
        is_interrupt=is_interrupt,
    )
