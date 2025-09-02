# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import logging
import uuid
from typing import Literal, Callable, List

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.config import get_stream_writer
from langgraph.types import Command

from duowen_agent.agents.react import (
    ReactAgent,
    ReactResult,
    ReactObservation,
    ReactAction,
)
from duowen_agent.deep_research.return_type import (
    ResultInfo,
    ReactStartInfo,
    ReactEndInfo,
    ReactActionInfo,
    ReactObservationInfo,
    PlanInfo,
    HumanFeedbackInfo,
    ReactResultInfo,
)
from duowen_agent.llm import MessagesSet
from duowen_agent.llm.chat_model import BaseAIChat
from duowen_agent.llm.extend import continue_chat
from duowen_agent.tools.base import BaseTool
from duowen_agent.utils.core_utils import stream_to_string, remove_think
from .agents import create_agent
from .config.configuration import Configuration
from .coordinator import Coordinator
from .prompts.planner_model import Plan
from .prompts.template import apply_prompt_template
from .types import State
from .utils.json_utils import repair_json_output
from .utils.message_trans import langchain_to_messageset

logger = logging.getLogger(__name__)

call_back_func = lambda x: get_stream_writer()(x)


class BackgroundInvestigationNode:

    def __init__(
        self,
        llm: BaseAIChat,
        tools: List[BaseTool],
        background_investigation_prompt: str = None,
        is_interrupt: Callable[[], bool] = None,
        **kwargs,
    ):
        """Background Investigation node using React agent architecture.

        Args:
            llm: The language model to use
            tools: List of tools available to the agent
            is_interrupt: Optional interrupt callback function
        """
        self.llm = llm
        self.tools = tools
        self.background_investigation_prompt = background_investigation_prompt
        self.is_interrupt = is_interrupt

    def run(self, state: State, config: RunnableConfig) -> dict:
        """Execute background investigation using React agent."""
        logging.info("Background investigation node is running.")

        configurable = Configuration.from_runnable_config(config)
        query = state.get("research_topic")

        # Create background investigator agent
        agent = create_agent(
            llm=self.llm,
            tools=self.tools,
            prompt_template="background_investigator",
            agent_prompt=self.background_investigation_prompt,
            max_iterations=configurable.react_max_iterations,
            is_interrupt=self.is_interrupt,
        )

        # Prepare the input for the agent
        _prompt = MessagesSet()
        _prompt.add_user(
            f"# 背景调查任务\n\n## 查询主题\n\n{query}\n\n## 语言要求\n\n{state.get('locale', 'zh-CN')}\n\n请对上述主题进行快速背景调查，建立基本认知框架。"
        )

        # Add resource information if available
        if state.get("resources"):
            resources_info = "**用户提到了以下资源文件：**\n\n"
            for resource in state.get("resources"):
                resources_info += f"- {resource.title} ({resource.description})\n"

            _prompt.add_user(
                resources_info
                + "\n\n"
                + "你必须使用 **local_search_tool** 从资源文件中检索信息。"
            )

        logging.info(f"Background investigator input: {_prompt.get_format_messages()}")
        response_content = ""

        node_id = uuid.uuid4().hex
        call_back_func(ReactStartInfo(content="背景调查", node_id=node_id))

        # Execute the agent
        for i in agent.run(instruction=_prompt):
            _data = i.model_dump()
            _data["node_id"] = node_id
            if isinstance(i, ReactObservation):
                call_back_func(ReactObservationInfo(**_data))
            elif isinstance(i, ReactAction):
                call_back_func(ReactActionInfo(**_data))
            elif isinstance(i, ReactResult):
                call_back_func(ReactResultInfo(**_data))
                response_content = i.result

        logging.debug(f"Background investigator full response: {response_content}")
        logging.info("Background investigation completed")
        call_back_func(ReactEndInfo(content="背景调查", node_id=node_id))
        return {"background_investigation_results": response_content}


class PlannerNode:
    def __init__(self, llm: BaseAIChat, planner_prompt: str = None, **kwargs):
        self.llm = llm
        self.planner_prompt = planner_prompt

    def run(
        self, state: State, config: RunnableConfig
    ) -> Command[Literal["human_feedback", "reporter"]]:
        """Planner node that generate the full plan."""
        logging.info("Planner generating full plan")

        configurable = Configuration.from_runnable_config(config)
        plan_iterations = (
            state["plan_iterations"] if state.get("plan_iterations", 0) else 0
        )

        messages = apply_prompt_template(
            prompt_name="planner",
            prompt_template=self.planner_prompt,
            state=state,
            configurable=configurable,
        )

        if state.get("enable_background_investigation") and state.get(
            "background_investigation_results"
        ):
            messages += [
                {
                    "role": "user",
                    "content": (
                        "background investigation results of user query:\n"
                        + state["background_investigation_results"]
                        + "\n"
                    ),
                }
            ]

        # if the plan iterations is greater than the max plan iterations, return the reporter node
        if plan_iterations >= configurable.max_plan_iterations:
            return Command(goto="reporter")

        full_response = remove_think(
            stream_to_string(
                self.llm.chat_for_stream(langchain_to_messageset(messages))
            )
        )
        logging.debug(f"Current state messages: {state['messages']}")
        logging.info(f"Planner response: {full_response}")

        try:
            curr_plan = json.loads(repair_json_output(full_response))
        except json.JSONDecodeError:
            logging.warning("Planner response is not a valid JSON")
            if plan_iterations > 0:
                return Command(goto="reporter")
            else:
                call_back_func(
                    ResultInfo(type="msg", content="很抱歉，我无法有效生成计划任务。")
                )
                return Command(goto="__end__")
        if curr_plan.get("has_enough_context"):
            logging.info("Planner response has enough context.")
            new_plan = Plan.model_validate(curr_plan)
            return Command(
                update={
                    "messages": [AIMessage(content=full_response, name="planner")],
                    "current_plan": new_plan,
                },
                goto="reporter",
            )

        return Command(
            update={
                "messages": [AIMessage(content=full_response, name="planner")],
                "current_plan": Plan.model_validate(curr_plan),
            },
            goto="human_feedback",
        )


class HumanFeedbackNode:

    def __init__(self, llm: BaseAIChat, human_feedback_tools: BaseTool, **kwargs):
        self.llm = llm
        self.human_feedback_tools = human_feedback_tools

    def run(
        self,
        state: State,
        config: RunnableConfig,
    ) -> Command[Literal["planner", "research_team", "reporter", "__end__"]]:
        current_plan = state.get("current_plan", "")
        # check if the plan is auto accepted
        auto_accepted_plan = state.get("auto_accepted_plan", False)
        if not auto_accepted_plan:
            _human_feedback = f"# <mark>研究计划</mark>\n\n{current_plan.to_markdown()}"
            call_back_func(HumanFeedbackInfo(type="str", content=_human_feedback))
            feedback = self.human_feedback_tools.run(content="发送反馈内容给用户")

            # if the feedback is not accepted, return the planner node
            if feedback and str(feedback).upper().startswith("[EDIT_PLAN]"):
                return Command(
                    update={
                        "messages": [
                            HumanMessage(content=feedback, name="feedback"),
                        ],
                    },
                    goto="planner",
                )
            elif feedback and str(feedback).upper().startswith("[ACCEPTED]"):
                logging.info("Plan is accepted by user.")
            else:
                raise TypeError(f"Interrupt value of {feedback} is not supported.")

        # if the plan is accepted, run the following node
        plan_iterations = (
            state["plan_iterations"] if state.get("plan_iterations", 0) else 0
        )
        goto = "research_team"

        plan_iterations += 1
        if current_plan.has_enough_context:
            goto = "reporter"

        return Command(
            update={
                "current_plan": current_plan,
                "plan_iterations": plan_iterations,
                "locale": current_plan.locale,
            },
            goto=goto,
        )


class CoordinatorNode:

    def __init__(self, llm: BaseAIChat, **kwargs):
        self.llm = llm

    def run(
        self, state: State, config: RunnableConfig
    ) -> Command[Literal["planner", "background_investigator", "__end__"]]:
        """Coordinator node that communicate with customers."""
        logging.info("Coordinator talking.")
        configurable = Configuration.from_runnable_config(config)

        # call_back_func(MsgInfo(content="意图识别..."))

        response = Coordinator(
            llm=self.llm,
            agent_name=configurable.agent_name,
        ).run(langchain_to_messageset(state["messages"]))

        logging.debug(f"Current state messages: {state['messages']}")

        goto = "__end__"
        locale = state.get("locale", "zh-CN")  # Default locale if not specified
        research_topic = state.get("research_topic", "")

        if response.is_function_call is True:

            goto = "planner"
            if state.get("enable_background_investigation"):
                # if the search_before_planning is True, add the web search tool to the planner agent
                goto = "background_investigator"

            locale = response.function_params.locale
            research_topic = response.function_params.research_topic
        else:
            logging.warning(
                "Coordinator response contains no tool calls. Terminating workflow execution."
            )
            logging.debug(f"Coordinator response: {response}")

        if response.is_function_call is False:
            call_back_func(ResultInfo(type="msg", content=response.response))

        return Command(
            update={
                "locale": locale,
                "research_topic": research_topic,
                "resources": configurable.resources,
            },
            goto=goto,
        )


class ReporterNode:
    def __init__(self, llm: BaseAIChat, reporter_prompt: str = None, **kwargs):
        self.llm = llm
        self.reporter_prompt = reporter_prompt

    def run(self, state: State, config: RunnableConfig):
        """Reporter node that write a final report."""
        logging.info("Reporter write final report")
        configurable = Configuration.from_runnable_config(config)
        current_plan = state.get("current_plan")
        input_ = {
            "messages": [
                HumanMessage(
                    f"# Research Requirements\n\n## Task\n\n{current_plan.title}\n\n## Description\n\n{current_plan.thought}"
                )
            ],
            "locale": state.get("locale", "en-US"),
        }
        invoke_messages = apply_prompt_template(
            prompt_name="reporter",
            prompt_template=self.reporter_prompt,
            state=input_,
            configurable=configurable,
        )
        observations = state.get("observations", [])

        # Add a reminder about the new report format, citation style, and table usage
        invoke_messages.append(
            HumanMessage(
                content="IMPORTANT: Structure your report according to the format in the prompt. Remember to include:\n\n1. Key Points - A bulleted list of the most important findings\n2. Overview - A brief introduction to the topic\n3. Detailed Analysis - Organized into logical sections\n4. Survey Note (optional) - For more comprehensive reports\n5. Key Citations - List all references at the end\n\nFor citations, DO NOT include inline citations in the text. Instead, place all citations in the 'Key Citations' section at the end using the format: `- [Source Title](URL)`. Include an empty line between each citation for better readability.\n\nPRIORITIZE USING MARKDOWN TABLES for data presentation and comparison. Use tables whenever presenting comparative data, statistics, features, or options. Structure tables with clear headers and aligned columns. Example table format:\n\n| Feature | Description | Pros | Cons |\n|---------|-------------|------|------|\n| Feature 1 | Description 1 | Pros 1 | Cons 1 |\n| Feature 2 | Description 2 | Pros 2 | Cons 2 |",
                name="system",
            )
        )

        for observation in observations:
            invoke_messages.append(
                HumanMessage(
                    content=f"Below are some observations for the research task:\n\n{observation}",
                    name="observation",
                )
            )
        logging.debug(f"Current invoke messages: {invoke_messages}")

        response_content = continue_chat(
            self.llm, langchain_to_messageset(invoke_messages)
        )
        # response_content = remove_think(
        #     stream_to_string(
        #         self.llm.chat_for_stream(langchain_to_messageset(invoke_messages))
        #     )
        # )

        logging.info(f"reporter response: {response_content}")
        call_back_func(
            ResultInfo(
                type="markdown",
                file_name=response_content.strip()
                .split("\n")[0]
                .lstrip("# "),  # 暂时简单处理后续，需要使用模型来编写名称
                content=response_content,
            )
        )
        return {"final_report": response_content}


def research_team_node(state: State):
    """Research team node that collaborates on tasks."""
    logging.info("Research team is collaborating on tasks.")

    _plan = state.get("current_plan")
    if isinstance(_plan, Plan):
        call_back_func(PlanInfo(content=_plan.to_plan_status_markdown()))
    pass


def _execute_agent_step(
    state: State, agent: ReactAgent, agent_name: str
) -> Command[Literal["research_team"]]:
    """Helper function to execute a step using the specified agent."""
    current_plan = state.get("current_plan")
    observations = state.get("observations", [])

    # Find the first unexecuted step
    current_step = None
    completed_steps = []
    for step in current_plan.steps:
        if not step.execution_res:
            current_step = step
            break
        else:
            completed_steps.append(step)

    if not current_step:
        logging.warning("No unexecuted step found")
        return Command(goto="research_team")

    logging.info(f"Executing step: {current_step.title}, agent: {agent_name}")

    # Format completed steps information
    completed_steps_info = ""
    if completed_steps:
        completed_steps_info = "# Existing Research Findings\n\n"
        for i, step in enumerate(completed_steps):
            completed_steps_info += f"## Existing Finding {i + 1}: {step.title}\n\n"
            completed_steps_info += f"<finding>\n{step.execution_res}\n</finding>\n\n"

    # Prepare the input for the agent with completed steps info
    _prompt = MessagesSet()
    _prompt.add_user(
        f"{completed_steps_info}# Current Task\n\n## Title\n\n{current_step.title}\n\n## Description\n\n{current_step.description}\n\n## Locale\n\n{state.get('locale', 'en-US')}"
    )

    # Add citation reminder for researcher agent
    if agent_name == "researcher":
        if state.get("resources"):
            resources_info = "**The user mentioned the following resource files:**\n\n"
            for resource in state.get("resources"):
                resources_info += f"- {resource.title} ({resource.description})\n"

            _prompt.add_user(
                resources_info
                + "\n\n"
                + "You MUST use the **local_search_tool** to retrieve the information from the resource files."
            )

        _prompt.add_user(
            "IMPORTANT: DO NOT include inline citations in the text. Instead, track all sources and include a References section at the end using link reference format. Include an empty line between each citation for better readability. Use this format for each reference:\n- [Source Title](URL)\n\n- [Another Source](URL)",
        )

    logging.info(f"Agent input: {_prompt.get_format_messages()}")
    response_content = ""

    node_id = uuid.uuid4().hex
    call_back_func(ReactStartInfo(content=current_step.title, node_id=node_id))

    for i in agent.run(instruction=_prompt):
        _data = i.model_dump()
        _data["node_id"] = node_id
        if isinstance(i, ReactObservation):
            call_back_func(ReactObservationInfo(**_data))
        elif isinstance(i, ReactAction):
            call_back_func(ReactActionInfo(**_data))
        elif isinstance(i, ReactResult):
            call_back_func(ReactResultInfo(**_data))
            response_content = i.result

    logging.debug(f"{agent_name.capitalize()} full response: {response_content}")

    # Update the step with the execution result
    current_step.execution_res = response_content
    logging.info(f"Step '{current_step.title}' execution completed by {agent_name}")

    call_back_func(ReactEndInfo(content=current_step.title, node_id=node_id))

    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name=agent_name,
                )
            ],
            "observations": observations + [response_content],
        },
        goto="research_team",
    )


def _setup_and_execute_agent_step(
    llm: BaseAIChat,
    state: State,
    config: RunnableConfig,
    agent_type: str,
    tools: list,
    agent_prompt: str = None,
    is_interrupt: Callable[[], bool] = None,
) -> Command[Literal["research_team"]]:
    """Helper function to set up an agent with appropriate tools and execute a step.

    This function handles the common logic for both researcher_node and coder_node:
    1. Configures MCP servers and tools based on agent type
    2. Creates an agent with the appropriate tools or uses the default agent
    3. Executes the agent on the current step

    Args:
        state: The current state
        config: The runnable config
        agent_type: The type of agent ("researcher" or "coder")
        default_tools: The default tools to add to the agent

    Returns:
        Command to update state and go to research_team
    """
    configurable = Configuration.from_runnable_config(config)

    agent = create_agent(
        llm=llm,
        tools=tools,
        prompt_template=agent_type,
        agent_prompt=agent_prompt,
        max_iterations=configurable.react_max_iterations,
        is_interrupt=is_interrupt,
    )
    return _execute_agent_step(state, agent, agent_type)


class ResearcherNode:

    def __init__(
        self,
        llm: BaseAIChat,
        tools: List[BaseTool],
        researcher_prompt: str = None,
        is_interrupt: Callable[[], bool] = None,
        **kwargs,
    ):
        self.llm = llm
        self.tools = tools
        self.researcher_prompt = researcher_prompt
        self.is_interrupt = is_interrupt

    def run(
        self, state: State, config: RunnableConfig
    ) -> Command[Literal["research_team"]]:
        """Researcher node that do research"""
        logging.info("Researcher node is researching.")

        return _setup_and_execute_agent_step(
            llm=self.llm,
            state=state,
            config=config,
            agent_type="researcher",
            tools=self.tools,
            is_interrupt=self.is_interrupt,
        )


class CoderNode:

    def __init__(
        self,
        llm: BaseAIChat,
        tools: List[BaseTool],
        coder_prompt: str = None,
        is_interrupt: Callable[[], bool] = None,
        **kwargs,
    ):
        self.llm = llm
        self.tools = tools
        self.coder_prompt = coder_prompt
        self.is_interrupt = is_interrupt

    def run(
        self, state: State, config: RunnableConfig
    ) -> Command[Literal["research_team"]]:
        """Coder node that do code analysis."""
        logging.info("Coder node is coding.")

        return _setup_and_execute_agent_step(
            llm=self.llm,
            state=state,
            config=config,
            agent_type="coder",
            agent_prompt=self.coder_prompt,
            tools=self.tools,
            is_interrupt=self.is_interrupt,
        )
