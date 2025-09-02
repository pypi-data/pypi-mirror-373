import json
import os
from typing import List, Dict, Any, TypedDict

from duowen_agent.llm import OpenAIChat, OpenAIEmbedding
from duowen_agent.llm.tokenizer import tokenizer
from duowen_agent.rag.nlp import LexSynth
from .base import BaseMemory
from ...utils.core_utils import stream_to_string


class ConversationMessage(TypedDict):
    role: str
    content: str
    content_split: str
    content_vector: list[float]


class ConversationMemory(BaseMemory):
    """
    Memory system for storing and summarizing conversation history.
    """

    def __init__(
        self,
        llm: OpenAIChat,
        lex_synth: LexSynth,
        emb: OpenAIEmbedding,
        summarize_threshold: int = 4000,
        path: str = None,
    ):
        self.llm = llm
        self.lex_synth = lex_synth
        self.emb = emb
        self.summarize_threshold = summarize_threshold
        self.messages: List[ConversationMessage] = []
        self.summary = ""
        self.summary_split = ""
        self.last_summarized = 0  # Index of last summarized message
        self.path = path

    def _dump(self) -> Dict[str, Any]:
        return {
            "messages": self.messages,
            "summary": self.summary,
            "summary_split": self.summary_split,
            "last_summarized": self.last_summarized,
        }

    def _load(self, data: Dict[str, Any]) -> None:
        self.messages = data["messages"]
        self.summary = data["summary"]
        self.summary_split = data["summary_split"]
        self.last_summarized = data["last_summarized"]

    def save_to_disk(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(json.dumps(self._dump(), ensure_ascii=False))

    def load_from_disk(
        self,
    ) -> None:
        if self.path and os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._load(data)

    def _add_message(self, role: str, message: str) -> None:
        self.messages.append(
            ConversationMessage(
                role=role,
                content=message,
                content_split=self.lex_synth.content_cut(message),
                content_vector=self.emb.get_embedding(
                    tokenizer.truncate_emb(message, self.emb.max_token)
                )[0],
            )
        )

    def add_user_message(self, message: str) -> None:
        self._add_message("user", message)
        self._check_and_summarize()

    def add_assistant_message(self, message: str) -> None:
        self._add_message("assistant", message)
        self._check_and_summarize()

    def add_system_message(self, message: str) -> None:
        for msg in self.messages:
            if msg["role"] == "system" and msg["content"] == message:
                return  # Skip if identical system message exists

        # Insert at beginning to maintain system message priority
        self.messages.insert(0, {"role": "system", "content": message})

    def get_messages(self, token_limit: int = 10240) -> List[Dict[str, str]]:
        _messages = [
            {"role": m["role"], "content": m["content"]} for m in self.messages
        ]
        if self.summary:
            system_messages = [
                {"role": "system", "content": m["content"]}
                for m in _messages
                if m["role"] == "system"
            ]
            token_limit -= tokenizer.messages_len(system_messages)

            summary_message = {
                "role": "system",
                "content": f"Conversation summary: {self.summary}",
            }
            token_limit -= tokenizer.messages_len([summary_message])

            last_message = _messages[self.last_summarized :]
            token_limit -= tokenizer.messages_len(last_message)

            truncated_other = []
            for i in reversed(
                [m for m in _messages if m["role"] != "system"][: self.last_summarized]
            ):
                if tokenizer.messages_len([i]) <= token_limit:
                    truncated_other.insert(0, i)
                    token_limit -= tokenizer.messages_len([i])
                else:
                    break
            return system_messages + [summary_message] + truncated_other + last_message
        else:
            system_messages = [
                {"role": "system", "content": m["content"]}
                for m in _messages
                if m["role"] == "system"
            ]
            token_limit -= tokenizer.messages_len(system_messages)
            truncated_other = []
            for i in reversed([m for m in self.messages if m["role"] != "system"]):
                if tokenizer.messages_len([i]) <= token_limit:
                    truncated_other.insert(0, i)
                    token_limit -= tokenizer.messages_len([i])
                else:
                    break
            return system_messages + truncated_other

    def get_chat_history(self) -> str:
        """
        Get a formatted string of the chat history.

        Returns:
            Formatted chat history
        """
        history = []

        # Add summary if available
        if self.summary:
            history.append(f"Summary: {self.summary}\n")

        # Add messages (excluding system messages)
        for msg in self.messages:
            if msg["role"] != "system":
                history.append(f"{msg['role'].capitalize()}: {msg['content']}")

        return "\n".join(history)

    def clear(self) -> None:
        """Clear all messages from memory except system messages."""
        system_messages = [msg for msg in self.messages if msg["role"] == "system"]
        self.messages = system_messages
        self.summary = ""
        self.summary_split = ""
        self.last_summarized = 0

    def search(
        self,
        query: str,
        tkweight: float = 0.7,
        vtweight: float = 0.3,
        threshold: float = 0.5,
    ) -> List[Dict[str, Any]]:

        results = []
        msg = [msg for msg in self.messages if msg["role"] != "system"]

        _relevance_score = self.lex_synth.hybrid_similarity(
            question=query,
            question_vector=self.emb.get_embedding(query)[0],
            docs_vector=[i["content_vector"] for i in msg],
            docs_sm=[i["content_split"] for i in msg],
            tkweight=tkweight,
            vtweight=vtweight,
            qa=True,
        )

        for index, relevance in enumerate(_relevance_score):
            results.append(
                {
                    "role": msg[index]["role"],
                    "content": msg[index]["content"],
                    "relevance": relevance,
                }
            )

        if self.summary and self.summary_split:

            results.insert(
                0,
                {
                    "content": f"From summary: {self.summary}",
                    "role": "system",
                    "relevance": self.lex_synth.query_text_similarity(
                        question=query, docs_sm=[self.summary_split]
                    )[0],
                },
            )

        return [i for i in results if i["relevance"] > threshold]

    def _check_and_summarize(self) -> None:
        """Check if summarization is needed and summarize if necessary."""
        # Count tokens in non-system messages
        non_system_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in self.messages
            if m["role"] != "system"
        ]
        token_count = tokenizer.messages_len(non_system_messages)
        # print(f"token_count: {token_count}")
        if token_count > self.summarize_threshold:
            self._summarize_conversation()

    def _summarize_conversation(self) -> None:
        """Summarize the conversation and remove older messages."""
        # Get non-system messages for summarization
        non_system_messages = [m for m in self.messages if m["role"] != "system"]

        # Keep the most recent messages
        keep_count = min(10, len(non_system_messages) // 3)
        keep_count = max(keep_count, 3)  # 保留最近3轮的不进行摘要

        # Messages to summarize (only those not previously summarized)
        to_summarize = (
            non_system_messages[self.last_summarized : -keep_count]
            if keep_count > 0
            else non_system_messages[self.last_summarized :]
        )

        if not to_summarize:
            return

        # Format conversation for summarization
        conversation = "\n".join(
            [f"{msg['role'].capitalize()}: {msg['content']}" for msg in to_summarize]
        )

        # Create summarization prompt
        prompt = f"""
对下列对话进行总结，提取最重要的信息、关键事实以及达成的任何决定或结论。保持未来对话所需的基本上下文。

历史摘要: {self.summary if self.summary else "None"}

需总结的对话内容:
{conversation}

请提供一个全面、详尽的摘要，涵盖所有关键信息。
"""
        # print(prompt)
        # Generate summary
        new_summary = stream_to_string(
            self.llm.chat_for_stream(messages=prompt, max_new_tokens=800)
        )

        # Update summary
        if self.summary:
            self.summary = f"{self.summary}\n\nUpdated with: {new_summary}"
        else:
            self.summary = new_summary

        self.summary_split = self.lex_synth.content_cut(self.summary)

        self.last_summarized = len(non_system_messages) - keep_count
