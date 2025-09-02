import json
import logging
from datetime import date
from os import getenv
from typing import Optional

import requests
from duowen_agent.error import ToolError
from duowen_agent.tools.base import BaseTool
from pydantic import BaseModel, Field, field_validator

from .entity import ToolSearchResult, ToolSearchResultDetails


class BochaParameters(BaseModel):
    """检索查询参数模型"""

    query: str = Field(..., min_length=1, description="用户的搜索词（必填）")
    freshness: Optional[str] = Field(
        default="noLimit",
        description='搜索指定时间范围内的网页。\n可填值：\n- oneDay，一天内\n- oneWeek，一周内\n- oneMonth，一个月内\n- oneYear，一年内\n- noLimit，不限（默认）\n- YYYY-MM-DD..YYYY-MM-DD，搜索日期范围，例如："2025-01-01..2025-04-06"\n- YYYY-MM-DD，搜索指定日期，例如："2025-04-06"',
    )
    summary: Optional[bool] = Field(default=True, description="是否显示文本摘要")
    count: Optional[int] = Field(
        default=10, ge=1, le=50, description="返回结果数量（1-50）"
    )
    page: Optional[int] = Field(default=1, ge=1, description="页码（≥1）")

    @field_validator("freshness")
    def validate_freshness(cls, v):
        """验证时间范围参数"""
        allowed_values = {"oneDay", "oneWeek", "oneMonth", "oneYear", "noLimit"}

        if v in allowed_values:
            return v

        # 验证日期范围格式
        if ".." in v:
            dates = v.split("..")
            if len(dates) != 2:
                raise ToolError("日期范围格式错误，使用 'YYYY-MM-DD..YYYY-MM-DD'")
            start_date, end_date = dates

            try:
                # 验证日期合法性
                date.fromisoformat(start_date)
                date.fromisoformat(end_date)
            except ValueError:
                raise ToolError("非法日期格式，使用 YYYY-MM-DD")

            return v

        # 验证单日期格式
        try:
            date.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError("非法日期格式，使用 YYYY-MM-DD 或预设值")


class Bocha(BaseTool):

    name: str = "bocha-search-api"
    description: str = (
        "专业网络搜索引擎，支持深度内容抓取和定制过滤。"
        "优势：精准的来源控制、时效性筛选、结构化数据输出。"
        "适用场景：新闻追踪、学术研究、市场分析等需要最新网络信息的任务。"
    )
    parameters = BochaParameters

    def __init__(
        self,
        base_url: str = None,
        api_key: str = None,
        token_limit: int = 8000,
        max_results: int = 5,
    ):
        super().__init__()
        self.base_url = base_url or "https://api.bochaai.com/v1/web-search"
        self.api_key = api_key or getenv("BOCHA_API_KEY")
        self.token_limit = token_limit
        self.page = max_results

    def search(self, query: str, **kwargs) -> ToolSearchResult:

        _param = {"query": query}
        _param.update(kwargs)

        _bocha_param = BochaParameters(**_param)
        try:

            payload = json.dumps(_bocha_param.model_dump(), ensure_ascii=False)
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            response = requests.request(
                "POST", self.base_url, headers=headers, data=payload
            )

            if response.status_code == 200:

                data1 = []
                _token_limit = self.token_limit
                for i in response.json()["data"]["webPages"]["value"][: self.page]:
                    _res = ToolSearchResultDetails(
                        url=i["url"],
                        title=i["name"],
                        content=i.get("summary", None) or i.get("snippet", None),
                        date_published=i["datePublished"],
                        site_name=i["siteName"],
                        site_icon=i["siteIcon"],
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
        **kwargs,
    ):
        _data = self.search(query, **kwargs)
        return _data
