from typing import Literal

from seekrai.types.agents.tools.schemas.file_search_env import FileSearchEnv
from seekrai.types.agents.tools.tool import ToolBase, ToolType


class FileSearch(ToolBase[FileSearchEnv]):
    name: Literal[ToolType.FILE_SEARCH] = ToolType.FILE_SEARCH
    tool_env: FileSearchEnv
