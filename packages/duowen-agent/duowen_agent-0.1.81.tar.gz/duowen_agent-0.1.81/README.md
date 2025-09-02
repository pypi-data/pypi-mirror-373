# 多闻(Duowen) - 企业级AI Agent开发框架

多闻(Duowen)是一个功能强大的企业级AI Agent开发框架，提供了完整的大语言模型(LLM)集成、检索增强生成(RAG)、智能体(Agent)构建和工具调用能力。

## 目录

- [✨ 核心特性](#-核心特性)
- [🚀 快速开始](#-快速开始)
  - [安装](#安装)
  - [环境配置](#环境配置)
- [📊 项目结构](#-项目结构)
- [📖 使用指南](#-使用指南)
  - [语言模型](#1-语言模型)
  - [嵌入模型](#2-嵌入模型)
  - [多模态嵌入](#3-多模态嵌入)
  - [重排序模型](#4-重排序模型)
- [🔍 RAG系统](#-rag系统)
  - [文档解析](#文档解析)
  - [文本切割](#文本切割)
  - [向量数据库](#向量数据库)
- [🤖 Agent框架](#-agent框架)
  - [ReAct Agent](#react-agent)
  - [记忆系统](#记忆系统)
- [🔧 工具生态](#-工具生态)
  - [内置工具](#内置工具)
  - [自定义工具](#自定义工具)
- [🌐 MCP协议支持](#-mcp协议支持)
- [🚀 高级特性](#-高级特性)
  - [批量处理](#批量处理)
  - [音频处理](#音频处理)
- [知识图谱 (Graph)](#知识图谱-graph)

## ✨ 核心特性

- 🤖 **多模型支持**: 支持OpenAI协议的大语言模型
- 🧠 **智能推理**: 内置推理模型支持，提供思维链推理能力
- 📚 **RAG系统**: 完整的文档解析、文本切割、向量检索和重排序功能
- 🔧 **工具生态**: 丰富的内置工具和自定义工具支持
- 🎯 **Agent框架**: 基于ReAct模式的智能体构建能力
- 💾 **记忆系统**: 对话记忆和长期记忆管理
- 🌐 **MCP协议**: 支持Model Context Protocol客户端
- 📊 **多模态**: 支持文本、图像、音频等多模态处理

## 🚀 快速开始

### 安装

```bash
pip install duowen-agent
```


### 环境配置

> **注意**: 以下环境配置主要用于运行测试用例，SDK本身不强制依赖这些配置。在实际使用中，您可以根据需要灵活配置相应的API密钥和服务地址。

如需运行项目测试用例，请创建 `.env` 文件并配置相关API密钥:

```env
SILICONFLOW_API_KEY=your_api_key_here
TAVILY_API_KEY=your_tavily_key_here
REDIS_ADDR=127.0.0.1:6379
REDIS_PASSWORD=your_redis_password
```

## 📊 项目结构

```
duowen-agent/
├── duowen_agent/              # 核心包
│   ├── agents/                # Agent实现
│   │   ├── react.py          # ReAct Agent
│   │   ├── memories/         # 记忆系统
│   │   └── ...
│   ├── llm/                  # 大语言模型
│   │   ├── chat_model.py     # 对话模型
│   │   ├── embedding_model.py # 嵌入模型
│   │   ├── rerank_model.py   # 重排序模型
│   │   └── ...
│   ├── rag/                  # RAG系统
│   │   ├── extractor/        # 文档解析
│   │   ├── splitter/         # 文本切割
│   │   ├── retrieval/        # 向量检索
│   │   └── ...
│   ├── tools/                # 工具生态
│   │   ├── base.py          # 工具基类
│   │   ├── tavily_search.py # 搜索工具
│   │   ├── python_repl.py   # Python执行器
│   │   └── ...
│   ├── mcp/                  # MCP协议
│   ├── prompt/               # 提示词管理
│   └── utils/                # 工具函数
├── test/                     # 测试用例
├── pyproject.toml           # 项目配置
└── README.md               # 项目文档
```

## 📖 使用指南

### 1. 语言模型

#### 基础对话模型

```python
from duowen_agent.llm import OpenAIChat
from os import getenv

llm_cfg = {
    "model": "THUDM/glm-4-9b-chat", 
    "base_url": "https://api.siliconflow.cn/v1",
    "api_key": getenv("SILICONFLOW_API_KEY")
}

llm = OpenAIChat(**llm_cfg)

# 同步调用
response = llm.chat("你好，请介绍一下自己")
print(response)

# 流式调用
for chunk in llm.chat_for_stream("讲一个有趣的故事"):
    print(chunk, end="")
```

#### 推理模型

```python
from duowen_agent.llm import OpenAIChat
from duowen_agent.utils.core_utils import separate_reasoning_and_response

llm_cfg = {
    "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
    "base_url": "https://api.siliconflow.cn/v1",
    "api_key": getenv("SILICONFLOW_API_KEY"),
    "is_reasoning": True,
}

llm = OpenAIChat(**llm_cfg)
content = llm.chat('9.9和9.11哪个数字更大？')

# 分离推理过程和最终答案
reasoning, response = separate_reasoning_and_response(content)
print(f"推理过程: {reasoning}")
print(f"最终答案: {response}")
```

### 2. 嵌入模型

#### 基础使用

```python
from duowen_agent.llm import OpenAIEmbedding
from os import getenv

emb_cfg = {
    "model": "BAAI/bge-large-zh-v1.5", 
    "base_url": "https://api.siliconflow.cn/v1",
    "api_key": getenv("SILICONFLOW_API_KEY")
}

emb = OpenAIEmbedding(**emb_cfg)

# 单个文本嵌入
vector = emb.get_embedding('这是一个测试文本')
print(f"向量维度: {len(vector)}")

# 批量文本嵌入
vectors = emb.get_embedding(['文本1', '文本2', '文本3'])
print(f"批量嵌入结果: {len(vectors)} 个向量")
```

#### 嵌入缓存

```python
from duowen_agent.llm import OpenAIEmbedding, EmbeddingCache
from duowen_agent.utils.cache import InMemoryCache
from os import getenv

# 配置嵌入模型
emb_cfg = {
    "model": "BAAI/bge-large-zh-v1.5", 
    "base_url": "https://api.siliconflow.cn/v1",
    "api_key": getenv("SILICONFLOW_API_KEY")
}
emb = OpenAIEmbedding(**emb_cfg)

# 使用内存缓存
cache = InMemoryCache()
embedding_cache = EmbeddingCache(cache, emb)

# 首次调用会计算嵌入
vector1 = embedding_cache.get_embedding('测试文本')
# 第二次调用会从缓存获取
vector2 = embedding_cache.get_embedding('测试文本')

print(f"两次结果相同: {vector1 == vector2}")
```

### 3. 多模态嵌入

#### 图文向量模型

```python
from duowen_agent.llm.embedding_vl_model import JinaClipV2Embedding, EmbeddingVLCache
from duowen_agent.utils.cache import InMemoryCache
from os import getenv

# 配置多模态嵌入模型
embedding_vl_model = JinaClipV2Embedding(
    base_url='http://127.0.0.1:8000',
    model_name='jina-clip-v2',
    api_key=getenv('JINA_API_KEY'),
    dimension=512
)

# 混合输入：文本和图像
input_data = [
    {'text': '一只可爱的小猫'}, 
    {'text': '美丽的风景照片'}, 
    {'image': 'https://example.com/cat.jpg'}
]

# 获取多模态嵌入
embedding_data = embedding_vl_model.get_embedding(input_data)
print(f"生成了 {len(embedding_data)} 个嵌入向量")

# 使用缓存提升性能
embedding_cache = EmbeddingVLCache(InMemoryCache(), embedding_vl_model)
cached_embeddings = embedding_cache.get_embedding(input_data)
```

### 4. 重排序模型

```python
from duowen_agent.llm import GeneralRerank
from duowen_agent.llm.tokenizer import tokenizer
from os import getenv

# 配置重排序模型
rerank_cfg = {
    "model": "BAAI/bge-reranker-v2-m3",
    "base_url": "https://api.siliconflow.cn/v1/rerank",
    "api_key": getenv("SILICONFLOW_API_KEY")
}

rerank = GeneralRerank(
    model=rerank_cfg["model"],
    api_key=rerank_cfg["api_key"],
    base_url=rerank_cfg["base_url"],
    encoding=tokenizer.chat_encoder
)

# 重排序示例
query = '苹果公司的最新产品'
documents = [
    "苹果公司发布了新款iPhone",
    "香蕉是一种热带水果", 
    "苹果手机销量创新高",
    "水果市场价格波动"
]

# 获取重排序结果
results = rerank.rerank(query=query, documents=documents, top_n=3)
for result in results:
    print(f"相关度: {result['relevance_score']}, 文档: {result['document']}")
```

## 🔍 RAG系统

多闻提供了完整的检索增强生成(RAG)系统，包括文档解析、文本切割和向量检索等功能。

### 文档解析

多闻支持多种文档格式的解析，将各种格式转换为Markdown格式便于后续处理。

#### Word文档解析

```python
from duowen_agent.rag.extractor.simple import word2md

# 解析Word文档
markdown_content = word2md("./documents/report.docx")
print(markdown_content)
```

#### PDF文档解析

```python
from duowen_agent.rag.extractor.simple import pdf2md

# 解析PDF文档
markdown_content = pdf2md("./documents/whitepaper.pdf")
print(markdown_content)
```

#### PowerPoint解析

```python
from duowen_agent.rag.extractor.simple import ppt2md

# 解析PPT文档
markdown_content = ppt2md("./documents/presentation.pptx")
print(markdown_content)
```

#### HTML网页解析

```python
from duowen_agent.rag.extractor.simple import html2md
import requests

# 获取网页内容
url = "https://example.com/article"
response = requests.get(url)
response.raise_for_status()

# 转换为Markdown
markdown_content = html2md(response.text)
print(markdown_content)
```

#### Excel表格解析

```python
from duowen_agent.rag.extractor.simple import excel_parser

# 解析Excel文件，支持.xlsx和.xls格式
for sheet_content in excel_parser("./documents/data.xlsx"):
    print(f"工作表内容: {sheet_content}")
    print("---")
```

### 文本切割

多闻提供了多种文本切割策略，适应不同的应用场景和文档类型。

#### Token切割

基于语言模型的token进行切割，确保每个块不超过模型的输入限制。

```python
from duowen_agent.rag.splitter import TokenChunker

# 配置token切割器
chunker = TokenChunker(
    chunk_size=512,      # 每块最大token数
    chunk_overlap=50     # 块之间的重叠token数
)

text = "这是一段很长的文本内容..."
for chunk in chunker.chunk(text):
    print(f"块大小: {len(chunk.page_content)} 字符")
    print(f"内容: {chunk.page_content[:100]}...")
    print("---")
```

#### 分隔符切割

根据指定的分隔符进行文本分割，适合结构化文档。

```python
from duowen_agent.rag.splitter import SeparatorChunker

# 按段落分割
chunker = SeparatorChunker(
    separator="\n\n",     # 分隔符
    chunk_size=1000,     # 最大块大小
    chunk_overlap=100    # 重叠大小
)

text = "段落1\n\n段落2\n\n段落3..."
for chunk in chunker.chunk(text):
    print(chunk.page_content)
    print("---")
```

#### 递归切割

智能地尝试多种分隔符，优先使用语义边界进行切割。

```python
from duowen_agent.rag.splitter import RecursiveChunker

# 配置递归切割器
chunker = RecursiveChunker(
    splitter_breaks=["\n\n", "。", "？", "！", ".", "?", "!"],
    chunk_size=800,
    chunk_overlap=80
)

text = "长篇文档内容..."
for chunk in chunker.chunk(text):
    print(f"块内容: {chunk.page_content}")
    print("---")
```

#### 语义切割

基于语义相似性进行智能切割，保持内容的语义连贯性。

```python
from duowen_agent.llm import OpenAIEmbedding
from duowen_agent.rag.splitter import SemanticChunker
from os import getenv

# 配置嵌入模型
emb_cfg = {
    "model": "BAAI/bge-large-zh-v1.5", 
    "base_url": "https://api.siliconflow.cn/v1",
    "api_key": getenv("SILICONFLOW_API_KEY")
}
emb = OpenAIEmbedding(**emb_cfg)

# 语义切割器
chunker = SemanticChunker(
    llm_embeddings_instance=emb,
    buffer_size=1,           # 缓冲区大小
    breakpoint_threshold_type="percentile",  # 阈值类型
    breakpoint_threshold_amount=95          # 阈值百分位
)

text = "包含多个主题的长文档..."
for chunk in chunker.chunk(text):
    print(f"语义块: {chunk.page_content}")
    print("---")
```

#### 快速混合切割

集成多种切割策略的高效切割器，适合大多数应用场景。

```python
from duowen_agent.rag.splitter import FastMixinChunker

# 快速混合切割器
chunker = FastMixinChunker(
    chunk_size=1000,
    chunk_overlap=100
)

text = "包含标题、段落、表格等多种元素的文档..."
for chunk in chunker.chunk(text):
    print(f"混合切割块: {chunk.page_content}")
    print("---")
```

### 向量数据库

多闻内置了轻量级的内存向量数据库`KDTreeVector`，适用于小型应用的快速原型开发和测试。对于大型生产环境，建议基于`BaseVector`抽象类开发自定义的向量数据库扩展。

#### 内置向量库使用

```python
from duowen_agent.rag.retrieval.kdtree import KDTreeVector
from duowen_agent.llm import OpenAIEmbedding
from duowen_agent.rag.nlp import LexSynth
from duowen_agent.rag.models import Document
from os import getenv

# 配置嵌入模型
emb_cfg = {
    "model": "BAAI/bge-large-zh-v1.5",
    "base_url": "https://api.siliconflow.cn/v1",
    "api_key": getenv("SILICONFLOW_API_KEY"),
}
emb = OpenAIEmbedding(**emb_cfg)
lex_synth = LexSynth()

# 创建向量数据库
vdb = KDTreeVector(
    llm_embeddings_instance=emb, 
    lex_synth=lex_synth, 
    db_file="./knowledge_base.svdb"
)

# 添加文档
documents = [
    "苹果公司于2023年9月发布iPhone 15 Pro，新增钛合金机身、A17 Pro芯片和USB-C接口。",
    "iPhone 15 Pro支持4K ProRes视频录制，配备48MP主摄像头。",
    "新款iPhone采用Action Button替代静音开关，提供更多自定义功能。"
]

for doc_text in documents:
    vdb.add_document(Document(page_content=doc_text))

# 保存到磁盘
vdb.save_to_disk()

# 查询示例
query = "iPhone 15 Pro有什么新功能？"

print("=== 语义检索 ===")
for result in vdb.semantic_search(query, top_k=3):
    print(f"相似度: {result.similarity_score:.4f}")
    print(f"内容: {result.result.page_content}")
    print("---")

print("\n=== 全文检索 ===")
for result in vdb.full_text_search(query, top_k=3):
    print(f"相似度: {result.similarity_score:.4f}")
    print(f"内容: {result.result.page_content}")
    print("---")

print("\n=== 混合检索 ===")
for result in vdb.hybrid_search(query, top_k=3):
    print(f"相似度: {result.similarity_score:.4f}")
    print(f"内容: {result.result.page_content}")
    print("---")
```

#### 自定义向量数据库扩展

对于大型生产环境，您可以基于`BaseVector`抽象类开发自定义的向量数据库实现：

```python
from duowen_agent.rag.retrieval.base import BaseVector
from duowen_agent.rag.models import Document, SearchResult
from typing import List

class CustomVectorDB(BaseVector):
    """自定义向量数据库实现"""
    
    def __init__(self, connection_string: str):
        # 初始化您的向量数据库连接
        self.connection = self._connect(connection_string)
    
    def add_document(self, document: Document) -> None:
        """添加文档到向量数据库"""
        # 实现文档添加逻辑
        pass
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """语义检索实现"""
        # 实现语义检索逻辑
        pass
    
    def hybrid_search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """混合检索实现"""
        # 实现混合检索逻辑
        pass

# 使用自定义向量数据库
custom_vdb = CustomVectorDB("your_connection_string")
```

## 🤖 Agent框架

多闻提供了强大的智能体(Agent)框架，支持基于ReAct模式的推理和行动能力，以及完善的记忆系统。

### ReAct Agent

基于ReAct（Reasoning and Acting）模式的智能体，能够进行推理和行动。

```python
from duowen_agent.agents.react import ReactAgent
from duowen_agent.llm import OpenAIChat
from duowen_agent.tools.base import BaseTool
from pydantic import BaseModel, Field
from os import getenv

# 配置语言模型
llm_cfg = {
    "model": "THUDM/glm-4-9b-chat",
    "base_url": "https://api.siliconflow.cn/v1",
    "api_key": getenv("SILICONFLOW_API_KEY"),
}
llm = OpenAIChat(**llm_cfg)

# 定义自定义工具
class CalculatorParameters(BaseModel):
    expression: str = Field(description="数学表达式")

class Calculator(BaseTool):
    name: str = "计算器"
    description: str = "执行数学计算"
    parameters = CalculatorParameters
    
    def _run(self, expression: str) -> str:
        try:
            result = eval(expression)
            return f"计算结果: {result}"
        except Exception as e:
            return f"计算错误: {str(e)}"

# 创建Agent
agent = ReactAgent(
    llm=llm,
    tools=[Calculator()],
    max_iterations=5
)

# 运行Agent
result = agent.run("请帮我计算 (25 + 75) * 3 的结果")
print(result)
```

### 记忆系统

```python
from duowen_agent.agents.memories.conversation import ConversationMemory
from duowen_agent.llm import OpenAIChat, OpenAIEmbedding
from duowen_agent.rag.nlp import LexSynth
from os import getenv

# 配置模型
llm_cfg = {
    "model": "THUDM/glm-4-9b-chat",
    "base_url": "https://api.siliconflow.cn/v1",
    "api_key": getenv("SILICONFLOW_API_KEY"),
}
llm = OpenAIChat(**llm_cfg)

emb_cfg = {
    "model": "BAAI/bge-large-zh-v1.5",
    "base_url": "https://api.siliconflow.cn/v1",
    "api_key": getenv("SILICONFLOW_API_KEY"),
}
emb = OpenAIEmbedding(**emb_cfg)

# 创建对话记忆
memory = ConversationMemory(
    llm=llm,
    emb=emb,
    lex_synth=LexSynth(),
    summarize_threshold=1000  # 超过1000字符时进行总结
)

# 添加对话历史
memory.add_system_message("你是一个有用的AI助手")
memory.add_user_message("我叫张三，是一名软件工程师")
memory.add_assistant_message("你好张三！很高兴认识你这位软件工程师。")
memory.add_user_message("我最近在学习机器学习")

# 获取相关记忆
relevant_memories = memory.get_relevant_memories("我的职业是什么？")
for memory_item in relevant_memories:
    print(memory_item)
```

## 🔧 工具生态

多闻提供了丰富的工具生态系统，包括内置工具和自定义工具支持，方便开发者扩展Agent的能力。

### 内置工具

#### 网络搜索工具

```python
from duowen_agent.tools.tavily_search import Tavily
from duowen_agent.tools.bocha_search import Bocha

# Tavily搜索
tavily = Tavily()
result, view = tavily._run(query="2024年人工智能发展趋势")
print(f"搜索结果: {result}")
print(f"详细信息: {view}")

# Bocha搜索
bocha = Bocha()
result, view = bocha._run(query="最新的AI技术突破")
print(f"搜索结果: {result}")
```

#### 文件处理工具

```python
from duowen_agent.tools.file import FileManager

# 文件管理工具
file_manager = FileManager()

# 读取文件
content = file_manager.read_file("./documents/report.txt")
print(content)

# 写入文件
file_manager.write_file("./output/summary.txt", "这是总结内容")
```

#### Python代码执行

```python
from duowen_agent.tools.python_repl import PythonREPL

# Python代码执行器
repl = PythonREPL()

# 执行Python代码
code = """
import numpy as np
data = np.array([1, 2, 3, 4, 5])
result = np.mean(data)
print(f"平均值: {result}")
"""

output = repl._run(code)
print(output)
```

### 自定义工具

```python
from duowen_agent.tools.base import BaseTool
from pydantic import BaseModel, Field
import requests

class WeatherParameters(BaseModel):
    city: str = Field(description="城市名称")

class WeatherTool(BaseTool):
    name: str = "天气查询"
    description: str = "查询指定城市的天气信息"
    parameters = WeatherParameters
    
    def _run(self, city: str) -> str:
        # 这里可以调用真实的天气API
        return f"{city}今天天气晴朗，温度25°C"

# 使用自定义工具
weather_tool = WeatherTool()
result = weather_tool._run("北京")
print(result)
```

## 🌐 MCP协议支持

多闻支持Model Context Protocol(MCP)协议，可以方便地与支持该协议的服务进行交互。

```python
from duowen_agent.mcp.mcp_client import MCPClient

# 连接MCP服务
with MCPClient("https://mcp.example.com/sse", authed=False) as client:
    # 列出可用工具
    tools = client.list_tools()
    print(f"可用工具: {tools}")
    
    # 调用工具
    result = client.invoke_tool(
        tool_name="search", 
        tool_args={"query": "人工智能"}
    )
    print(f"工具执行结果: {result}")
```


## 🚀 高级特性

多闻提供了一系列高级特性，包括批量处理和音频处理等功能，满足更复杂的应用场景需求。

### 批量处理

```python
from duowen_agent.llm.batch import BatchProcessor
from duowen_agent.llm import OpenAIChat

# 批量处理大量文本
batch_processor = BatchProcessor(llm=OpenAIChat(**llm_cfg))

texts = ["文本1", "文本2", "文本3"]
results = batch_processor.process_batch(texts, "请总结这段文本")

for i, result in enumerate(results):
    print(f"文本{i+1}总结: {result}")
```

### 音频处理

```python
from duowen_agent.llm.audio import AudioProcessor

# 音频转文字
audio_processor = AudioProcessor()
transcript = audio_processor.transcribe("./audio/speech.mp3")
print(f"转录结果: {transcript}")

# 文字转音频
audio_data = audio_processor.text_to_speech("你好，欢迎使用多闻框架")
```

## 知识图谱 (Graph)

Duowen Graph 是 Duowen Agent 框架中的知识图谱模块，用于从文本中提取实体和关系，构建知识图谱，并支持基于图谱的查询和可视化。

### 功能概述

- **知识提取**：从文本中自动提取实体和关系
- **图谱构建**：基于提取的实体和关系构建知识图谱
- **社区发现**：对图谱进行社区划分，生成社区报告
- **语义查询**：支持基于语义的图谱查询，包括局部查询和全局查询
- **可视化**：支持知识图谱的可视化展示

### 初始化图谱

```python
from duowen_agent.llm import OpenAIChat, OpenAIEmbedding
from duowen_agent.rag.graph import Graph, QueryParam
from duowen_agent.rag.graph.storage.vdb_kdtree import KdTreeVectorStorage
from duowen_agent.rag.nlp import LexSynth
from duowen_agent.rag.splitter import RecursiveChunker

# 初始化语言模型
llm = OpenAIChat(
    model="your_model_name",
    base_url="your_api_base_url",
    api_key="your_api_key",
    token_limit=1024 * 128,
    max_tokens=1024 * 4,
)

# 初始化嵌入模型
emb = OpenAIEmbedding(
    model="your_embedding_model",
    base_url="your_api_base_url",
    api_key="your_api_key",
    dimension=1024,
    max_token=32 * 1024,
)

# 初始化词法分析器
lex_synth = LexSynth()

# 初始化图谱
graph = Graph(
    llm_instance=llm,
    chunk_func=RecursiveChunker(),
    extractor_concurrent_num=36,  # 实体提取并发数
    community_concurrent_num=36,  # 社区发现并发数
    entity_vdb=KdTreeVectorStorage(
        namespace="entity", embedding=emb, lex_synth=lex_synth
    ),
    community_vdb=KdTreeVectorStorage(
        namespace="community", embedding=emb, lex_synth=lex_synth
    ),
)
```

### 插入文档

```python
# 插入文档
docs = {
    "doc_id_1": "文档内容1",
    "doc_id_2": "文档内容2",
    # 更多文档...
}
graph.insert(docs)
```

### 构建社区

```python
# 构建社区
graph.build_community()
```

### 查询图谱

```python
# 局部查询
local_result = graph.query(
    "你的查询问题", 
    QueryParam(mode="local")
)

# 全局查询
global_result = graph.query(
    "你的查询问题", 
    QueryParam(mode="global")
)

# 只获取上下文，不生成回答
context_only = graph.query(
    "你的查询问题", 
    QueryParam(mode="global", only_need_context=True)
)
```

### 获取和保存图谱

```python
from duowen_agent.rag.graph import dump_graph

# 获取图谱
graph_data = graph.get_graph()

# 保存图谱到文件
with open("graph.json", "w") as f:
    f.write(dump_graph(graph_data))
```

### 图谱可视化

```python
from duowen_agent.rag.graph.utils import create_styled_graph

# 生成HTML可视化
with open("graph.html", "w") as f:
    f.write(create_styled_graph(graph.get_graph()))
```

### 高级配置

QueryParam 类提供了丰富的查询参数配置：

```python
from duowen_agent.rag.graph import QueryParam

# 局部查询参数
local_param = QueryParam(
    mode="local",                        # 查询模式：local/global/naive
    only_need_context=False,           # 是否只返回上下文
    response_type="Multiple Paragraphs", # 回答类型
    level=2,                           # 社区层级
    top_k=20,                          # 检索数量
    local_max_token_for_text_unit=4000, # 文本单元最大token数
    local_max_token_for_local_context=4800, # 局部上下文最大token数
    local_max_token_for_community_report=3200, # 社区报告最大token数
    local_community_single_one=False,   # 是否只使用一个社区
)

# 全局查询参数
global_param = QueryParam(
    mode="global",
    global_concurrent_num=4,           # 全局查询并发数
    global_min_community_rating=0,     # 社区最低评分
    global_max_consider_community=512, # 最大考虑社区数
    global_max_token_for_community_report=16384, # 社区报告最大token数
)
```

### 图谱工具类

```python
from duowen_agent.rag.graph.utils import NetworkXUtils, similarity_node

# 获取邻居图
neighbors_graph = NetworkXUtils(graph_data).get_neighbors_graph(
    "实体名称",
    4,  # 深度
    top_k_neighbors=5,
    top_k_node=5,
)

# 分析节点相似性
similar_nodes = similarity_node(
    node_names,  # 节点名称列表
    node_vectors,  # 节点向量列表
    sim_threshold=0.9  # 相似度阈值
)
```
