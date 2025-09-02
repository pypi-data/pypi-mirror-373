"""
参考
https://github.com/D-Star-AI/dsRAG
"""

from typing import List, Literal, Callable, Optional

from pydantic import BaseModel, Field
from tqdm import tqdm

from duowen_agent.llm import (
    OpenAIChat,
    SystemMessage,
    UserMessage,
    MessagesSet,
    tokenizer,
)
from duowen_agent.rag.models import Document
from duowen_agent.rag.splitter.separator import SeparatorChunker
from duowen_agent.utils.core_utils import retrying, json_observation, stream_to_string
from .base import BaseChunk


class SectionEnt(BaseModel):
    title: str = Field(
        description="main topic of this section of the document (very descriptive)"
    )
    start_index: int = Field(
        description="line number where the section begins (inclusive)"
    )
    end_index: int = Field(description="line number where the section ends (inclusive)")


class StructuredDocumentEnt(BaseModel):
    """obtains meaningful sections, each centered around a single concept/topic"""

    sections: List[SectionEnt] = Field(description="a list of sections of the document")


class SectionsChunker(BaseChunk):
    def __init__(
        self,
        llm_instance: OpenAIChat,
        token_count_type: Literal["o200k", "cl100k"] = "cl100k",
        chunk_size: int = 512,
        max_characters: int = 80000,
        callback_func: Callable[[str, Optional[float]], None] = None,
        interrupt_func: Callable[[], bool] = None,
    ):
        super().__init__(token_count_type=token_count_type)
        self.llm_instance = llm_instance
        self.chunk_size = chunk_size
        self.max_characters = min(
            max_characters, int((self.llm_instance.token_limit - 4000) * 1.2)
        )
        self.callback_func = callback_func
        self.interrupt_func = interrupt_func
        self.template_str = """Read the document below and extract a StructuredDocument object from it where each section of the document is centered around a single concept/topic. Whenever possible, your sections (and section titles) should match up with the natural sections of the document (i.e. Introduction, Conclusion, References, etc.). Sections can vary in length, but should generally be anywhere from a few paragraphs to a few pages long.
Each line of the document is marked with its line number in square brackets (e.g. [1], [2], [3], etc). Use the line numbers to indicate section start and end.
The start and end line numbers will be treated as inclusive. For example, if the first line of a section is line 5 and the last line is line 10, the start_index should be 5 and the end_index should be 10.
The first section must start at the first line number of the document ({start_line} in this case), and the last section must end at the last line of the document ({end_line} in this case). The sections MUST be non-overlapping and cover the entire document. In other words, they must form a partition of the document.
Section titles should be descriptive enough such that a person who is just skimming over the section titles and not actually reading the document can get a clear idea of what each section is about.
Note: the document provided to you may just be an excerpt from a larger document, rather than a complete document. Therefore, you can't always assume, for example, that the first line of the document is the beginning of the Introduction section and the last line is the end of the Conclusion section (if those section are even present).

Refer to the following TypeScript-defined StructuredDocument and convert it into JSON format for output:

```TypeScript
interface Section {{
    title: string; // main topic of this section of the document (very descriptive)
    start_index: number; // line number where the section begins (inclusive)
    end_index: number; // line number where the section ends (inclusive)
}}

interface StructuredDocument {{
    /** obtains meaningful sections, each centered around a single concept/topic */
    sections: Section[]; // a list of sections of the document
}}
```

Refer to the following JSON format for output:
```json
{{
  "sections": [
        {{
            "title": "简介",
            start_index: 0,
            end_index: 10,
        }},
        ...
    ]
}}
```
[important] Output all in Chinese.
[important] Respond with JSON code only without any explanations and comments. -- just the JSON code."""

    @staticmethod
    def get_document_with_lines(
        document_lines: List[str], start_line: int, max_characters: int
    ) -> (str, int):
        document_with_line_numbers = ""
        character_count = 0
        end_line = None
        for i in range(start_line, len(document_lines)):
            line = document_lines[i]
            document_with_line_numbers += f"[{i}] {line}\n"
            character_count += len(line)
            if character_count > max_characters or i == len(document_lines) - 1:
                end_line = i
                break
        return document_with_line_numbers, end_line

    @staticmethod
    def get_document_lines(document: str) -> List[str]:
        document_lines = document.split("\n")
        return document_lines

    @staticmethod
    def is_valid_partition(sections, a, b):
        if sections[0].start_index != a:
            return False
        if sections[-1].end_index != b:
            return False

        for i in range(1, len(sections)):
            if sections[i].start_index != sections[i - 1].end_index + 1:
                return False

        return True

    @staticmethod
    def get_sections_text(
        sections: List[SectionEnt], document_lines: List[str]
    ) -> List[dict]:
        """
        Takes in a list of Section objects and returns a list of dictionaries containing the attributes of each Section object plus the content of the section.
        """
        section_dicts = []
        for s in sections:
            contents = document_lines[
                s.start_index : s.end_index + 1
            ]  # end_index is inclusive
            section_dicts.append(
                {
                    "title": s.title,
                    "content": "\n".join(contents),
                    "start": s.start_index,
                    "end": s.end_index,
                }
            )
        return section_dicts

    @staticmethod
    def partition_sections(sections, a, b):
        """
        - sections: a list of Section objects, each containing the following attributes:
            - title: str - the main topic of this section of the document
            - start_index: int - line number where the section begins (inclusive)
            - end_index: int - line number where the section ends (inclusive)
        """
        if len(sections) == 0:
            return [SectionEnt(title="", start_index=a, end_index=b)]

        # Filter out sections that are completely outside the range [a, b]
        sections = [s for s in sections if s.start_index <= b and s.end_index >= a]

        # Filter out any sections where the end index is less than the start index
        sections = [s for s in sections if s.start_index <= s.end_index]

        if len(sections) == 0:
            return [SectionEnt(title="", start_index=a, end_index=b)]

        # Adjust sections that partially overlap with the range [a, b]
        for s in sections:
            if s.start_index < a:
                s.start_index = a
                s.title = ""
            if s.end_index > b:
                s.end_index = b
                s.title = ""

        # Sort the intervals by their start value
        sections.sort(key=lambda x: x.start_index)

        # Remove any sections that are completely contained within another section
        i = 0
        while i < len(sections) - 1:
            if sections[i].end_index >= sections[i + 1].end_index:
                sections.pop(i + 1)
            else:
                i += 1

        if len(sections) == 0:
            return [SectionEnt(title="", start_index=a, end_index=b)]

        # Ensure the first section starts at a
        if sections[0].start_index > a:
            sections.insert(
                0,
                SectionEnt(
                    title="", start_index=a, end_index=sections[0].start_index - 1
                ),
            )

        # Ensure the last section ends at b
        if sections[-1].end_index < b:
            sections.append(
                SectionEnt(
                    title="", start_index=sections[-1].end_index + 1, end_index=b
                )
            )

        # Ensure there are no gaps or overlaps between sections
        completed_sections = []
        for i in range(0, len(sections)):
            if i == 0:
                # Automatically add the first sectoin
                completed_sections.append(sections[i])
            else:
                if sections[i].start_index > sections[i - 1].end_index + 1:
                    # There is a gap between sections[i-1] and sections[i]
                    completed_sections.append(
                        SectionEnt(
                            title="",
                            start_index=sections[i - 1].end_index + 1,
                            end_index=sections[i].start_index - 1,
                        )
                    )
                elif sections[i].start_index <= sections[i - 1].end_index:
                    # There is an overlap between sections[i-1] and sections[i]
                    completed_sections[-1].end_index = sections[i].start_index - 1
                    completed_sections[-1].title = ""
                # Always add the current iteration's section
                completed_sections.append(sections[i])

        return completed_sections

    def get_structured_document(self, document_with_line_numbers, start_line, end_line):
        if self.interrupt_func and self.interrupt_func():
            raise InterruptedError("用户中断")
        return retrying(
            func=self._get_structured_document,
            func_params=dict(
                document_with_line_numbers=document_with_line_numbers,
                start_line=start_line,
                end_line=end_line,
            ),
        )

    def _get_structured_document(
        self, document_with_line_numbers, start_line, end_line
    ):

        _sys_msg = self.template_str.format(start_line=start_line, end_line=end_line)
        _usr_msg = document_with_line_numbers

        _data = stream_to_string(
            self.llm_instance.chat_for_stream(
                messages=MessagesSet([SystemMessage(_sys_msg), UserMessage(_usr_msg)]),
                temperature=0,
                max_tokens=4000,
            )
        )

        return json_observation(_data, StructuredDocumentEnt)

    def chunk_with_title(self, document: str, **kwargs):
        # print(f"<text>{repr(document)}<text>")
        max_iterations = 2 * (len(document) // self.max_characters + 1)
        document_lines = self.get_document_lines(document)
        start_line = 0
        all_sections = []

        with tqdm(total=max_iterations, desc="Chunking document") as pbar:

            for _ in range(max_iterations):
                document_with_line_numbers, end_line = self.get_document_with_lines(
                    document_lines, start_line, self.max_characters
                )
                structured_doc = self.get_structured_document(
                    document_with_line_numbers, start_line, end_line
                )
                new_sections = structured_doc.sections
                all_sections.extend(new_sections)

                if end_line >= len(document_lines) - 1:
                    # reached the end of the document
                    break
                else:
                    if len(new_sections) > 1:
                        # remove last section since it's assumed to be incomplete (but only if we added more than one section in this iteration)
                        all_sections.pop()
                    start_line = (
                        all_sections[-1].end_index + 1
                    )  # start from the next line after the last section
                pbar.update(1)
                self.callback_func("分段中...", pbar.n / pbar.total)

        # fix the sections so that they form a partition of the document
        a = 0
        b = len(document_lines) - 1

        # the fact that this is in a loop is a complete hack to deal with the fact that the partitioning function is not perfect
        all_sections = self.partition_sections(all_sections, a, b)

        # Verify that the sections are non-overlapping and cover the entire document

        if not self.is_valid_partition(all_sections, a, b):
            raise AssertionError("Invalid partition")

        # get the section text
        section_dicts = self.get_sections_text(all_sections, document_lines)

        section_dicts = [i for i in section_dicts if i["content"].strip()]

        return section_dicts

    def chunk(self, document: str, **kwargs) -> List[Document]:

        _doc = []

        def _chunk(text):
            if self.token_len(text) <= self.chunk_size:
                _doc.append(text)
                return

            if len(self.get_document_lines(text)) == 1:
                _doc.append(text)
                return

            _data = [i["content"] for i in self.chunk_with_title(text)]

            if len(_data) == 1:
                _doc.append(text)
                return

            _current_doc = []

            for i in _data:

                if self.token_len(i) > self.chunk_size:

                    if _current_doc:
                        _doc.append("\n\n".join(_current_doc))
                        _current_doc = []

                    self.callback_func("与预定切割长度不同，开始递归切割")
                    _chunk(i)

                else:
                    _merge_str = "\n\n".join(_current_doc + [i])
                    if self.token_len(_merge_str) <= self.chunk_size:
                        _current_doc.append(i)
                    else:
                        _doc.append("\n\n".join(_current_doc))
                        _current_doc = []
                        _current_doc.append(i)

            _doc.append("\n\n".join(_current_doc))
            _current_doc = []

        self.callback_func("开始分段")

        _chunk(document)

        self.callback_func("分段结束")

        return [
            Document(
                page_content=i,
                metadata=dict(token_count=self.token_len(i), chunk_index=idx),
            )
            for idx, i in enumerate(_doc)
            if len(i.strip()) > 0
        ]


class MetaChunker(BaseChunk):
    TRUNCATION_MESSAGE = """
Also note that the document text provided below is just the first ~{num_words} words of the document. That should be plenty for this task. Your response should still pertain to the entire document, not just the text provided below.
""".strip()

    DOCUMENT_TITLE_PROMPT = """
INSTRUCTIONS
What is the title of the following document?

Your response MUST be the title of the document, and nothing else. DO NOT respond with anything else.

{document_title_guidance}

{truncation_message}

DOCUMENT
{document_text}

[important] Output all in Chinese.
""".strip()

    DOCUMENT_SUMMARIZATION_PROMPT = """
INSTRUCTIONS
What is the following document, and what is it about? 

Your response should be a single sentence, and it shouldn't be an excessively long sentence. DO NOT respond with anything else.

Your response should take the form of "This document is about: X". For example, if the document is a book about the history of the United States called A People's History of the United States, your response might be "This document is about: 从1776年至今的美国历史。" If the document is the 2023 Form 10-K for Apple Inc., your response might be "This document is about: 2023财年苹果公司的财务表现和运营状况。"

{document_summarization_guidance}

{truncation_message}

DOCUMENT
Document name: {document_title}

{document_text}

[important] Output all in Chinese.
""".strip()

    SECTION_SUMMARIZATION_PROMPT = """
INSTRUCTIONS
What is the following section about? 

Your response should be a single sentence, and it shouldn't be an excessively long sentence. DO NOT respond with anything else.

Your response should take the form of "This section is about: X". For example, if the section is a balance sheet from a financial report about Apple, your response might be "This section is about: 苹果在财年结束时的财务状态。" If the section is a chapter from a book on the history of the United States, and this chapter covers the Civil War, your response might be "This section is about: 美国内战的其原因和其后果。"

{section_summarization_guidance}

SECTION
Document name: {document_title}
Section name: {section_title}

{section_text}

[important] Output all in Chinese.
    """.strip()

    def __init__(
        self,
        llm_instance: OpenAIChat,
        token_count_type: Literal["o200k", "cl100k"] = "cl100k",
    ):
        super().__init__(token_count_type=token_count_type)
        self.llm_instance = llm_instance

    @staticmethod
    def split_into_chunks(text: str, chunk_size: int):
        return [
            i.page_content
            for i in SeparatorChunker(chunk_size=chunk_size, chunk_overlap=0).chunk(
                text
            )
        ]

    @staticmethod
    def get_chunk_header(
        document_title: str = "",
        document_summary: str = "",
        section_title: str = "",
        section_summary: str = "",
    ):
        """
        The chunk header is what gets prepended to each chunk before embedding or reranking. At the very least, it should contain the document title.
        """
        chunk_header = ""
        if document_title:
            chunk_header += f"Document context: the following excerpt is from a document titled '{document_title}'. {document_summary}"
        if section_title:
            chunk_header += f"\n\nSection context: this excerpt is from the section titled '{section_title}'. {section_summary}"
        return chunk_header

    def get_document_title(
        self,
        document: str,
        max_content_tokens: int = 4000,
        document_title_guidance: str = None,
    ):

        document_text = tokenizer.truncate_emb(document, max_content_tokens)
        if self.token_len(document_text) < max_content_tokens:
            truncation_message = ""
        else:
            truncation_message = self.TRUNCATION_MESSAGE.format(num_words=3000)

        prompt = self.DOCUMENT_TITLE_PROMPT.format(
            document_title_guidance=document_title_guidance,
            document_text=document_text,
            truncation_message=truncation_message,
        )

        document_title = stream_to_string(
            self.llm_instance.chat_for_stream(prompt, temperature=0.2, max_tokens=1000)
        )
        return document_title

    def get_document_summary(
        self,
        document: str,
        document_title: str,
        max_content_tokens=8000,
        document_summarization_guidance: str = None,
    ):
        # if this number changes, also update num_words in the truncation message below
        document_text = tokenizer.truncate_emb(document, max_content_tokens)
        if self.token_len(document_text) < max_content_tokens:
            truncation_message = ""
        else:
            truncation_message = self.TRUNCATION_MESSAGE.format(num_words=6000)

        prompt = self.DOCUMENT_SUMMARIZATION_PROMPT.format(
            document_summarization_guidance=document_summarization_guidance,
            document_text=document_text,
            document_title=document_title,
            truncation_message=truncation_message,
        )

        document_summary = stream_to_string(
            self.llm_instance.chat_for_stream(prompt, temperature=0.2, max_tokens=1000)
        )
        return document_summary

    def get_section_summary(
        self,
        section_text,
        section_title,
        document_title,
        section_summarization_guidance,
    ):
        prompt = self.SECTION_SUMMARIZATION_PROMPT.format(
            section_summarization_guidance=section_summarization_guidance,
            section_text=section_text,
            document_title=document_title,
            section_title=section_title,
        )
        section_summary = stream_to_string(
            self.llm_instance.chat_for_stream(prompt, temperature=0.2, max_tokens=1000)
        )
        return section_summary

    def chunk(
        self,
        document: str,
        chunk_size: int = 600,
        split_max_characters: int = 80000,
        document_title: str = None,
        min_length_for_chunking: int = 600,
        document_summary_max_tokens: int = 8000,
        document_summarization_guidance="Make sure the summary is concise and informative.",
        document_title_guidance="Make sure the title is nice and human readable.",
        section_summarization_guidance="Make sure the summary is concise and informative.",
        **kwargs,
    ):
        sections = SectionsChunker(
            llm_instance=self.llm_instance, max_characters=split_max_characters
        ).chunk_with_title(document)

        if not document_title:
            _document_title = self.get_document_title(
                document, document_summary_max_tokens, document_title_guidance
            ).strip()
        else:
            _document_title = document_title

        _document_summary = self.get_document_summary(
            document,
            _document_title,
            document_summary_max_tokens,
            document_summarization_guidance,
        ).strip()

        chunks = []
        for section in sections:
            section_text = section["content"]
            section_title = section["title"]
            section_summary = self.get_section_summary(
                section_text,
                section_title,
                _document_title,
                section_summarization_guidance,
            )

            if self.token_len(section_text) < min_length_for_chunking:
                chunks.append(
                    {
                        "chunk_text": section_text,
                        "document_title": _document_title,
                        "document_summary": _document_summary,
                        "section_title": section_title,
                        "section_summary": section_summary,
                    }
                )
            else:

                section_chunks = self.split_into_chunks(
                    section_text, chunk_size=chunk_size
                )

                for chunk in section_chunks:
                    chunks.append(
                        {
                            "chunk_text": chunk,
                            "document_title": _document_title,
                            "document_summary": _document_summary,
                            "section_title": section_title,
                            "section_summary": section_summary,
                        }
                    )

        res = []
        for index, chunk in enumerate(chunks):
            _chunk_header = self.get_chunk_header(
                document_title=chunk["document_title"],
                document_summary=chunk["document_summary"],
                section_title=chunk["section_title"],
                section_summary=chunk["section_summary"],
            )
            page_content = f"{_chunk_header}\n\n{chunk['chunk_text']}"
            if len(page_content.strip()) > 0:
                res.append(
                    Document(
                        page_content=page_content,
                        metadata={
                            "doc_id": _document_title,
                            "chunk_index": index,
                            "chunk_text": chunk["chunk_text"],
                            "chunk_header": _chunk_header,
                            "document_title": chunk["document_title"],
                            "document_summary": chunk["document_summary"],
                            "section_title": chunk["section_title"],
                            "section_summary": chunk["section_summary"],
                        },
                    )
                )

        return res
