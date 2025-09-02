import logging
from abc import ABC, abstractmethod
from typing import Dict, Type, Any

from pydantic import BaseModel


class BaseToolResult(BaseModel, ABC):

    @abstractmethod
    def to_str(self) -> str:
        raise NotImplementedError("必须实现 to_str() 方法, 该方法用于返回给语言模型")

    @abstractmethod
    def to_view(self) -> dict | str:
        raise NotImplementedError(
            "必须实现 to_view() 方法, 该方法用于返回应用程序的视图"
        )


def _pydantic_to_refined_schema(pydantic_obj: type(BaseModel)) -> Dict[str, Any]:
    """Get refined schema(OpenAI function call type schema) from pydantic object."""
    # Remove useless fields.
    refined_schema = pydantic_obj.model_json_schema()

    if "title" in refined_schema:
        del refined_schema["title"]
    for k, v in refined_schema["properties"].items():
        if "title" in v:
            del v["title"]

    return refined_schema


def _validate_refined_schema(schema: Dict) -> bool:
    """Validate refined schema(OpenAI function call type schema).

    Args:
        schema: any dict

    Returns:
        bool: True if schema is openai function call type schema, False otherwise.
    """
    if "name" not in schema or "description" not in schema:
        return False

    if "properties" not in schema:
        return False

    return True


class BaseTool(ABC):
    """Abstract base class for tools. All tools must implement this interface."""

    name: str
    """Tool name"""
    description: str
    """Tool description"""
    parameters: Type[BaseModel]
    """Tool parameters"""

    def __init__(self, *args, **kwargs):
        self.check_params()

    def check_params(self):
        """Check parameters when initialization."""
        if (
            not getattr(self, "name", None)
            or not getattr(self, "description", None)
            and not getattr(self, "parameters", None)
        ):
            raise TypeError(
                f"{self.__class__.__name__} required parameters 'name', 'description' and 'parameters'."
            )

    def run(self, **kwargs) -> type(BaseToolResult):
        """run the tool including specified function and hooks"""
        result: Any = self._run(**kwargs)
        logging.debug(f"[dw tool response] name: {self.name} result: {result}")
        return result

    @abstractmethod
    def _run(self, **kwargs) -> BaseToolResult | str | int | float:
        """Run detail business, implemented by subclass."""
        raise NotImplementedError()

    def to_schema(self) -> Dict[str, Any]:
        """
        Converts the Tool instance to a OpenAI function call type JSON schema.

        Returns:
            dict: A dictionary representing the JSON schema of the Tool instance.
        """
        # If there are no parameters, return the basic schema.
        if not self.parameters:
            return {
                "name": self.name,
                "description": self.description,
            }

        # If parameters are defined by a Pydantic BaseModel, convert to schema.
        if isinstance(self.parameters, type) and issubclass(self.parameters, BaseModel):
            return {
                "name": self.name,
                "description": self.description,
                "parameters": _pydantic_to_refined_schema(self.parameters),
            }

        # If parameters are neither a BaseModel nor a dictionary, raise an error.
        raise TypeError(
            f"The 'parameters' attribute of {self.__class__.__name__} must be either a subclass of BaseModel or a dictionary representing a schema."
            # noqa: E501
        )

    def _args_to_kwargs(self, *args, **kwargs) -> Dict:
        """Converts positional arguments to keyword arguments based on tool parameters.

        This method takes in both positional and keyword arguments. It then attempts to
        match the positional arguments to the tool's parameters, converting them to
        keyword arguments. Any additional keyword arguments are also included in the
        final dictionary.

        Returns:
            Dict: A dictionary containing the converted keyword arguments.
        """
        all_kwargs = {}

        if isinstance(self.parameters, type) and issubclass(self.parameters, BaseModel):
            all_kwargs.update(dict(zip(self.parameters.model_fields.keys(), args)))

        all_kwargs.update(kwargs)

        return all_kwargs
