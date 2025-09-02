# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import dataclasses
import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader, select_autoescape, Template
from langgraph.prebuilt.chat_agent_executor import AgentState

from ..config.configuration import Configuration

# Initialize Jinja2 environment
env = Environment(
    loader=FileSystemLoader(os.path.dirname(__file__)),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)


def get_prompt_template(prompt_name: str) -> str:
    """
    Load and return a prompt template using Jinja2.

    Args:
        prompt_name: Name of the prompt template file (without .md extension)

    Returns:
        The template string with proper variable substitution syntax
    """
    try:
        template = env.get_template(f"{prompt_name}.md")
        return template.render()
    except Exception as e:
        raise ValueError(f"Error loading template {prompt_name}: {e}")


def apply_prompt_template(
    prompt_name: str,
    prompt_template: str = None,
    state: AgentState = None,
    configurable: Configuration = None,
) -> list:
    """
    Apply template variables to a prompt template and return formatted messages.

    Args:
        prompt_name: Name of the prompt template to use
        prompt_template: 如果传入参数则按照prompt_template来
        state: Current agent state containing variables to substitute

    Returns:
        List of messages with the system prompt as the first message
    """
    # Convert state to dict for template rendering
    _state = state or {}

    state_vars = {
        "CURRENT_TIME": datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),
        **_state,
    }

    # Add configurable variables
    if configurable:
        state_vars.update(dataclasses.asdict(configurable))

    try:
        if prompt_template:
            # If prompt_template is a string, convert it to a Jinja2 template
            if isinstance(prompt_template, str):
                template = Template(prompt_template)
            else:
                template = prompt_template
        else:
            template = env.get_template(f"{prompt_name}.md")
        system_prompt = template.render(**state_vars)
        if "messages" in _state:
            return [{"role": "system", "content": system_prompt}] + state["messages"]
        else:
            return [{"role": "system", "content": system_prompt}]
    except Exception as e:
        raise ValueError(f"Error applying template {prompt_name}: {e}")
