from typing import Optional, List

from duowen_agent.agents.base import BaseToolResult
from duowen_agent.llm import tokenizer
from pydantic import BaseModel, computed_field


class ToolSearchResultDetails(BaseModel):
    url: Optional[str] = None
    title: Optional[str] = None
    content: str
    site_name: Optional[str] = None
    site_icon: Optional[str] = None
    date_published: Optional[str] = None
    content_split: Optional[str] = None
    content_vector: Optional[list[float]] = None

    @computed_field
    @property
    def content_with_weight(self) -> str:
        return f"URL:{self.url}\nTITLE: {self.title}\nDATE PUBLISHED: {self.date_published}\nCONTENT: {self.content}"

    @computed_field
    @property
    def chat_token(self) -> int:
        return tokenizer.chat_len(self.content_with_weight)

    @computed_field
    @property
    def emb_token(self) -> int:
        return tokenizer.emb_len(self.content_with_weight)


class ToolSearchResult(BaseToolResult):
    result: Optional[List[ToolSearchResultDetails]] = []

    @computed_field
    @property
    def content_with_weight(self) -> str:
        clean_result = []
        for index, data in enumerate(self.result):
            _date_published = (
                "\n**发布日期**：" + data.date_published
                if data.date_published
                else "\n"
            )

            _tmp = f"""#### 参考资料 {index + 1}  

**标题**：{data.title}

**链接**：[{data.url}]({data.url})  
{_date_published if _date_published else ""}
**摘要**：{data.content}
"""
            clean_result.append(_tmp)

        return "### 参考资料列表\n\n" + "\n\n".join(clean_result)

    def to_str(self) -> str:
        return self.content_with_weight

    def to_view(self) -> dict | str:
        if self.result:
            return {
                "search_result": [
                    {
                        "title": data.title,
                        "url": data.url,
                        "content": data.content,
                        "date_published": data.date_published,
                    }
                    for data in self.result
                ]
            }
        else:
            return {"search_result": None}
