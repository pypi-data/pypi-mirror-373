from typing import Optional


class EmptyMessageSetError(Exception):
    pass


class MissingAttributionError(Exception):
    def __init__(self, key_type: str):
        super().__init__(f"<{key_type}> is not provided. Please set it correctly.")


class OpenAIError(Exception):
    def __init__(self, msg: str):
        super().__init__(f"<OpenAI> could not get data correctly, reasons: {msg}")


class NetWorkError(Exception):
    def __init__(self, origin: str, reason: Optional[str] = None):
        msg = f"<{origin}> could not get data"
        if reason:
            msg += f", reason: {reason}"
        super().__init__(msg)


class OutputParserError(Exception):
    def __init__(self, reason: str, llm_output: str):
        msg = f"{reason}\n[LLM response]: {llm_output}"
        super().__init__(msg)


class ObserverException(Exception):
    """观察者校验异常"""

    def __init__(
        self,
        question: str = None,
        predict_value: str = None,
        expect_value: str = None,
        err_msg: str = None,
    ):
        self.question = question if question else ""
        self.predict_value = predict_value if predict_value else ""
        self.expect_value = expect_value if expect_value else ""
        self.err_msg = err_msg if err_msg else ""

    def __str__(self):
        return f"预期结果异常 {self.err_msg} 问题: {self.question}; 预测值: {self.predict_value[:100]}; 期望值: {self.expect_value}"


class MissObjError(Exception):
    """数据对象获取异常"""

    def __init__(self, obj_type: str, name: str, msg: str = None):
        self.name = name
        self.obj_type = obj_type
        self.msg = msg if msg else "数据对象缺失"

    def __str__(self):
        return f"{self.msg}, 类型:{self.obj_type} 名称:{self.name}"


class PromptBuildError(Exception):
    """流程完整性异常，内部错误"""

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return f"提示词构建异常: {self.msg}"


class LLMError(Exception):
    """语言模型调用异常"""

    def __init__(
        self, msg: str, base_url: str = None, model_name: str = None, message=None
    ):
        self.msg = msg
        self.base_url = base_url
        self.model_name = model_name
        self.message = message

    def __str__(self):
        return f"语言模型调用异常: {self.msg} base_url:{self.base_url} model_name:{self.model_name},messages:{str(self.message[:20])}"


class LengthLimitExceededError(Exception):
    def __init__(
        self, message="长度限制，回答被截断", content=None, reasoning_content=None
    ):
        self.message = message
        self.content = content
        self.reasoning_content = reasoning_content
        super().__init__(self.message)


class MaxTokenExceededError(Exception):
    def __init__(
        self, message="MaxToken限制，回答被截断", content=None, reasoning_content=None
    ):
        self.message = message
        self.content = content
        self.reasoning_content = reasoning_content
        super().__init__(self.message)


class EmbeddingError(Exception):
    """Embedding模型调用异常"""

    def __init__(self, msg, base_url, model_name):
        self.msg = msg
        self.base_url = base_url
        self.model_name = model_name

    def __str__(self):
        return f"Embedding模型调用异常: {self.msg} base_url:{self.base_url} model_name:{self.model_name}"


class RerankError(Exception):
    """Rerank模型调用异常"""

    def __init__(self, msg, base_url, model_name):
        self.msg = msg
        self.base_url = base_url
        self.model_name = model_name

    def __str__(self):
        return f"Rerank模型调用异常: {self.msg} base_url:{self.base_url} model_name:{self.model_name}"


class ToolError(Exception):
    """Raised when a tool encounters an error."""

    def __init__(self, message):
        self.message = message
