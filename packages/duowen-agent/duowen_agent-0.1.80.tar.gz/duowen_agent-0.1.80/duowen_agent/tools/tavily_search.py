import logging
from os import getenv
from typing import Literal, Optional, Sequence

from duowen_agent.error import ToolError
from duowen_agent.tools.base import BaseTool
from pydantic import BaseModel, Field
from tavily import TavilyClient

from .entity import ToolSearchResult, ToolSearchResultDetails


class TavilyParameters(BaseModel):
    """Parameters definition for Tavily Search API"""

    query: str = Field(description="用户需要搜索的查询字符串")
    search_depth: Literal["basic", "advanced"] = Field(
        default="basic",
        description="搜索深度模式，basic=基础搜索（快速响应），advanced=高级搜索（更深入分析）",
    )
    topic: Literal["general", "news"] = Field(
        default="general", description="搜索主题类型，general=综合信息，news=时效性新闻"
    )
    days: int = Field(
        default=3,
        ge=1,
        description="搜索结果时间范围（仅限news主题），单位天数，默认最近3天",
    )
    max_results: int = Field(
        default=5, ge=1, le=20, description="最大返回结果数量（1-20之间）"
    )
    include_domains: Optional[Sequence[str]] = Field(
        default=None, description="指定需要搜索的域名列表（如['wikipedia.org']）"
    )
    exclude_domains: Optional[Sequence[str]] = Field(
        default=None, description="需要排除的域名列表（如['twitter.com']）"
    )
    include_answer: bool = Field(
        default=False, description="是否在结果中包含AI生成的答案摘要"
    )
    include_raw_content: bool = Field(
        default=False, description="是否包含网页原始内容（可能影响响应速度）"
    )
    include_images: bool = Field(default=False, description="是否在结果中返回图片链接")


class Tavily(BaseTool):

    name: str = "tavily-search-api"
    description: str = (
        "专业网络搜索引擎，支持深度内容抓取和定制过滤。"
        "优势：精准的来源控制、时效性筛选、结构化数据输出。"
        "适用场景：新闻追踪、学术研究、市场分析等需要最新网络信息的任务。"
    )
    parameters = TavilyParameters

    def __init__(
        self, api_key: str = None, max_results: int = 5, token_limit: int = 8000
    ):
        super().__init__()
        self.tavily_client = TavilyClient(api_key or getenv("TAVILY_API_KEY"))
        self.token_limit = token_limit
        self.max_results = max_results

    def search(
        self,
        query: str,
        search_depth: Literal["basic", "advanced"] = "advanced",
        **kwargs,
    ) -> ToolSearchResult:
        try:
            response = self.tavily_client.search(
                query=query, search_depth=search_depth, **kwargs
            )
            data1 = []
            _token_limit = self.token_limit
            for res in response["results"][: self.max_results]:
                _res = ToolSearchResultDetails(
                    url=res["url"],
                    title=res["title"],
                    content=res["content"],
                )
                if _res.chat_token <= _token_limit:
                    data1.append(_res)
                    _token_limit -= _res.chat_token
                else:
                    break

            return ToolSearchResult(result=data1)
        except Exception as e:
            logging.exception(e)
            raise ToolError(str(e))

    def _run(
        self,
        query: str,
        search_depth: Literal["basic", "advanced"] = "advanced",
        **kwargs,
    ):
        _data = self.search(query, **kwargs)
        return _data.content_with_weight, _data
