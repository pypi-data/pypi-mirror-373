from typing import Literal, Optional

from duowen_agent.agents.react import ReactObservation, ReactAction, ReactResult
from pydantic import BaseModel


class MsgInfo(BaseModel):
    content: str


class HumanFeedbackInfo(BaseModel):
    type: Literal["str"] = "str"
    content: str


class PlanInfo(BaseModel):
    content: str


class ReactStartInfo(BaseModel):
    content: str
    node_id: str


class ReactObservationInfo(ReactObservation):
    node_id: str


class ReactActionInfo(ReactAction):
    node_id: str


class ReactResultInfo(ReactResult):
    node_id: str


class ReactEndInfo(BaseModel):
    content: str
    node_id: str


class ResultInfo(BaseModel):
    type: Literal["msg", "markdown"]
    file_name: Optional[str] = None
    content: str
