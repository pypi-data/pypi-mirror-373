from typing import Literal

from seekrai.types.agents.tools.schemas.web_search_env import WebSearchEnv
from seekrai.types.agents.tools.tool import ToolBase, ToolType


class WebSearch(ToolBase[WebSearchEnv]):
    name: Literal[ToolType.WEB_SEARCH] = ToolType.WEB_SEARCH
    tool_env: WebSearchEnv
