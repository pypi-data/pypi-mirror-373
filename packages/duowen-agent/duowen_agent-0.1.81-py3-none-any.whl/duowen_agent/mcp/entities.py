from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from duowen_agent.mcp.session.base_session import BaseSession
from duowen_agent.mcp.types import LATEST_PROTOCOL_VERSION, RequestId, RequestParams

SUPPORTED_PROTOCOL_VERSIONS: list[str] = ["2024-11-05", LATEST_PROTOCOL_VERSION]


SessionT = TypeVar("SessionT", bound=BaseSession[Any, Any, Any, Any, Any])
LifespanContextT = TypeVar("LifespanContextT")


@dataclass
class RequestContext(Generic[SessionT, LifespanContextT]):
    request_id: RequestId
    meta: RequestParams.Meta | None
    session: SessionT
    lifespan_context: LifespanContextT
