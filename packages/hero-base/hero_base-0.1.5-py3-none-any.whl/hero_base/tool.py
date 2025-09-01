from typing import AsyncGenerator, Callable, Any, Coroutine, Dict, List, Optional, TypeVar, Type, cast, Generic
from dataclasses import dataclass, field

from pydantic import BaseModel
from hero_base.state import State


@dataclass
class ToolCall:
    tool: str
    params: Dict[str, Any]


type ToolResult = ToolSuccess | ToolFailed | ToolError | ToolEnd


@dataclass
class ToolSuccess:
    content: str
    additional_context: str = ""
    additional_images: list[str] = field(default_factory=list)
    next: Optional[str] = None

    def __post_init__(self):
        self.status = "success"


@dataclass
class ToolFailed:
    content: str
    next: Optional[str] = None

    def __post_init__(self):
        self.status = "failed"


@dataclass
class ToolEnd:
    content: str
    additional_outputs: Optional[List[str]] = None

    def __post_init__(self):
        self.status = "end"


@dataclass
class ToolError:
    content: str
    next: Optional[str] = None

    def __post_init__(self):
        self.status = "error"


T = TypeVar('T')


class CommonToolWrapper(Generic[T]):
    def __init__(self, prefix: str, name: str, params: type[BaseModel], tool_tips: list[str], memory_hint: str, options: T | None, func: Callable[..., ToolResult | Coroutine[Any, Any, ToolResult] | AsyncGenerator[Any, ToolResult]], options_type: Optional[Type[T]] = None):
        if prefix:
            self.name = prefix + "_" + name
        else:
            self.name = name
        self.params = params
        self.memory_hint = memory_hint
        self.tool_tips = tool_tips
        self.options: T | None = options
        self.func = func
        self.options_type = options_type

    def get_name(self) -> str:
        return self.name

    def get_memory_hint(self) -> str:
        return self.memory_hint

    def get_tool_tips(self) -> list[str]:
        return self.tool_tips

    def get_params(self) -> type[BaseModel]:
        return self.params

    def custom(self, options: Optional[T] = None) -> "CommonToolWrapper[T]":

        if options is None:
            return self

        if isinstance(options, dict):
            result: Dict[str, Any] = options.copy()
        else:
            # 如果不是字典，使用cast进行类型转换
            result: Dict[str, Any] = cast(Dict[str, Any], options)

        if self.options is not None:
            if isinstance(self.options, dict):
                self.options.update(result)
            else:
                self.options = cast(T, result)
        return self

    def invoke(self, params: Dict[str, Any], state: Optional[State]) -> ToolResult | Coroutine[Any, Any, ToolResult] | AsyncGenerator[Any, ToolResult]:
        """
            invoke the tool
        """
        params = params.copy()
        call_params = {}
        # filter return type
        func_params = {k: v for k,
                       v in self.func.__annotations__.items() if k != "return"}
        for param in func_params:
            if param in params:
                call_params[param] = params[param]
            else:
                call_params[param] = None
        if "options" in func_params:
            call_params["options"] = self.options
        if "state" in func_params:
            call_params["state"] = state
        return self.func(**call_params)


class Tool:
    def __init__(self, prefix: str = ""):
        self.prefix = prefix

    def __call__(self, params: type[BaseModel], name: str = "", tool_tips: list[str] = [], memory_hint: str = "", options: T | None = None, options_type: Optional[Type[T]] = None):
        def decorator(func: Callable[..., (ToolSuccess | ToolFailed | ToolError | ToolEnd) | Coroutine[Any, Any, (ToolSuccess | ToolFailed | ToolError | ToolEnd)] | AsyncGenerator[Any, (ToolSuccess | ToolFailed | ToolError | ToolEnd)]]) -> CommonToolWrapper[T]:
            common_tool_wrapper = CommonToolWrapper[T](
                prefix=self.prefix,
                name=name or func.__name__,
                params=params,
                tool_tips=tool_tips,
                memory_hint=memory_hint,
                options=options,
                options_type=options_type,
                func=func,
            )
            return common_tool_wrapper

        return decorator
