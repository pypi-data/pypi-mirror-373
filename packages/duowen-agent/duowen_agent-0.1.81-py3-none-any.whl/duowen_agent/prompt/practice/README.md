### translate

- [翻译](translate.yaml)

### summarize_paper

- [论文总结](summarize_paper.yaml)

### analyze_patent

- [论文分析](analyze_patent.yaml)

### seo_summary

- [面向搜索引擎的文章摘要](seo_summary.yaml)
- 返回格式

```python
from pydantic import BaseModel, Field
from typing import List


class Abstract(BaseModel):
    title: str = Field(..., description="文章标题")
    keywords: List[str] = Field(
        ..., description='["关键词1", "关键词2", "同义词1", "相关短语1",...]'
    )
    entity: List[str] = Field(
        ...,
        description='["人名","组织名","地点","时间表达式","产品","事件",...]',
    )
    abstract: str = Field(
        ..., description="150-200字的摘要，逻辑清晰，简明扼要"
    )
```

### summarize_mindmap

- 基于内容的[脑图总结](summarize_mindmap.yaml)
- 返回格式

```python
from pydantic import BaseModel, Field
from typing import Optional, List


class SubTopic(BaseModel):
    title: str = Field(description="The title of the node, represents the main idea of this subtopic.")
    details: Optional[str] = Field(
        description="An optional description providing more context for the subtopic.")
    sub_topics: Optional[List['SubTopic']] = Field(
        description="List of subtopics, forming a recursive structure for nested nodes.")


class MindMap(BaseModel):
    main_topic: SubTopic
```

### query_translation

- [问题转换](query_translation.yaml)，用于rag场景下的问题增强。
- 返回格式

```python
from pydantic import BaseModel, Field
from typing import List, Literal


class MethodResponse(BaseModel):
    method: Literal["Multi-query", "Decomposition", "Step-back", "HYDE"] = Field(..., description="所选方法")
    analysis: str = Field(..., description="对输入问题的分析结果")
    queries: List[str] = Field(..., description="生成的检索查询或分解问题")
    reasoning: str = Field(..., description="选择方法的逻辑推导过程")
    final_response: str = Field(..., description="最终的回答方式或策略")
```

### merge_contexts

- [会话合并](merge_contexts.yaml), 针对用户与ai对话的上下文进行话合并
- 返回格式

```python

from pydantic import BaseModel, Field
from typing import List


class AnalysisResult(BaseModel):
    theme_switch_points: List[str] = Field(..., description="对话中的主题切换点，通常是一些关键的对话片段")
    filtered_content: str = Field(..., description="经过筛选后与新问题相关的内容")


class NewQuestion(BaseModel):
    new_question: str = Field(..., description="基于筛选内容生成的逻辑连贯的新问题")


class AnalysisOutput(BaseModel):
    analysis_result: AnalysisResult = Field(..., description="分析结果，包含主题切换点和筛选内容")
    new_question: NewQuestion = Field(..., description="基于筛选内容生成的新问题")
```

### summarize_contexts

- [记忆压缩](summarize_contexts.yaml),总结对话内容并提取关键信息，用于后续对话上下文提示.

### summarize_contexts_title

- [会话命名](summarize_contexts_title.yaml),配合summarize_contexts之后只用，通常用于给用户会话取一个好记的名字

### related_questions

- [相关追问](related_questions.yaml),根据用户对话生成问题追问。
- 返回格式

```python
from pydantic import BaseModel, Field
from typing import List


class Questions(BaseModel):
    questions: List[str] = Field(..., description="生成的追问问题")
```

### entity_extract

- [实体抽取](entity_extract.yaml),提取文档内的关键词，服务混合检索提高准确率。
- 返回格式

```python
from pydantic import BaseModel, Field
from typing import List


class Entity(BaseModel):
    entity_type: str = Field(..., description="实体类型")
    context_importance: int = Field(..., description="重要性评分（0-10之间）")
    entity_zh: str = Field(..., description="实体中文名称")
    entity_en: str = Field(..., description="实体英文名称")


class EntitiesOutput(BaseModel):
    entities: List[Entity]
```