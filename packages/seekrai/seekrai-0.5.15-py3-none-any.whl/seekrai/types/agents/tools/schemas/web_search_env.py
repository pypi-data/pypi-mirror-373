from typing import Optional

from seekrai.types.agents.tools.env_model_config import EnvConfig


class WebSearchEnv(EnvConfig):
    web_search_tool_description: Optional[str] = None
