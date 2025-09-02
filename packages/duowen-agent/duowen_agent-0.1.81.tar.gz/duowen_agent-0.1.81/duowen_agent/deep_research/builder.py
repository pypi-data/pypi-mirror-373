# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT
from typing import Callable, List

from langgraph.graph import StateGraph, START, END

from .nodes import (
    ReporterNode,
    research_team_node,
    ResearcherNode,
    CoderNode,
    CoordinatorNode,
    BackgroundInvestigationNode,
    PlannerNode,
    HumanFeedbackNode,
)
from .prompts.planner_model import StepType
from .types import State
from ..llm.chat_model import BaseAIChat
from ..tools.base import BaseTool


def continue_to_running_research_team(state: State):
    current_plan = state.get("current_plan")
    if not current_plan or not current_plan.steps:
        return "planner"
    if all(step.execution_res for step in current_plan.steps):
        return "planner"
    for step in current_plan.steps:
        if not step.execution_res:
            break
    if step.step_type and step.step_type == StepType.RESEARCH:
        return "researcher"
    if step.step_type and step.step_type == StepType.PROCESSING:
        return "coder"
    return "planner"


def build_graph(
    llm: BaseAIChat,
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
    """Build and return the base state graph with all nodes and edges."""
    builder = StateGraph(State)
    builder.add_edge(START, "coordinator")
    builder.add_node("coordinator", CoordinatorNode(llm).run)
    builder.add_node(
        "background_investigator",
        BackgroundInvestigationNode(
            llm, background_investigation_tools, background_investigation_prompt, is_interrupt
        ).run,
    )
    builder.add_node("planner", PlannerNode(llm, planner_prompt).run)
    builder.add_node("reporter", ReporterNode(llm, reporter_prompt).run)
    builder.add_node("research_team", research_team_node)
    builder.add_node(
        "researcher",
        ResearcherNode(llm, researcher_tools, researcher_prompt, is_interrupt).run,
    )
    builder.add_node(
        "coder", CoderNode(llm, coder_tools, coder_prompt, is_interrupt).run
    )
    builder.add_node("human_feedback", HumanFeedbackNode(llm, human_feedback_tools).run)
    builder.add_edge("background_investigator", "planner")
    builder.add_conditional_edges(
        "research_team",
        continue_to_running_research_team,
        ["planner", "researcher", "coder"],
    )
    builder.add_edge("reporter", END)

    return builder.compile()
