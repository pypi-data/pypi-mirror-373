from typing import Optional

from pydantic import BaseModel, Field, computed_field


class Document(BaseModel):
    id: Optional[str] = Field(default=None, description="切片id，唯一")
    page_content: str = Field(..., description="切片文本内容")
    vector_content: Optional[str] = Field(default=None, description="向量计算文本内容")
    vector: Optional[list[float]] = Field(default=None, description="向量")
    page_content_split: Optional[str] = Field(default=None, description="文档切片分词")
    page_content_sm_split: Optional[str] = Field(
        default=None, description="文档切片精细分词"
    )
    file_id: Optional[str] = Field(default=None, description="切片所属文档id")
    title: Optional[str] = Field(default=None, description="文档标题")
    title_split: Optional[str] = Field(default=None, description="文档标题分词")
    title_sm_split: Optional[str] = Field(default=None, description="文档标题精细分词")
    important_keyword: Optional[list[str]] = Field(
        default=None, description="文档关键词"
    )
    important_keyword_split: Optional[list[str]] = Field(
        default=None, description="文档精细关键词分词"
    )
    create_time: Optional[str] = Field(default=None, description="创建时间")
    question: Optional[list[str]] = Field(default=None, description="文档相关问题")
    question_split: Optional[str] = Field(default=None, description="文档相关问题分词")
    authors: Optional[list[str]] = Field(default=None, description="文档作者")
    institution: Optional[list[str]] = Field(default=None, description="文档机构")
    abstract: Optional[str] = Field(default=None, description="文档摘要")
    chunk_index: Optional[int] = Field(default=-1, description="切片索引")
    metadata: Optional[dict] = Field(default=None, description="文档元数据")
    kb_id: Optional[str] = Field(default=None, description="切片所属知识库id")
    kb: Optional[list[str]] = Field(None, description="知识库名称")
    label: Optional[list[str]] = Field(default=None, description="文本所属标签")
    slots: Optional[list[str]] = Field(default=None, description="文本所属槽位")

    def __hash__(self):
        _title = self.title if self.title else ""
        return hash(_title + self.page_content)

    def __eq__(self, other):
        if isinstance(other, Document):
            return self.page_content == other.page_content and self.title == other.title
        return False


class SearchResult(BaseModel):
    result: Document

    token_similarity_score: Optional[float] = None
    vector_similarity_score: Optional[float] = None
    hybrid_similarity_score: Optional[float] = None
    rerank_similarity_score: Optional[float] = None

    @computed_field
    def similarity_score(self) -> float:
        return (
            self.rerank_similarity_score
            or self.hybrid_similarity_score
            or self.vector_similarity_score
            or self.token_similarity_score
        )
