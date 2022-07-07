from typing import TypeVar, Any, TYPE_CHECKING

from gobexec.model.base import Result

if TYPE_CHECKING:
    from gobexec.model.tool import Tool

R = TypeVar('R', bound=Result)


class ExecutionContext:
    async def get_tool_result(self, tool: 'Tool[Any, R]') -> R:
        ...