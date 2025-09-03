import enum
from typing import Generic, TypeVar

from pydantic import BaseModel

from seekrai.types.agents.tools.env_model_config import EnvConfig


class ToolType(str, enum.Enum):
    FILE_SEARCH = "file_search"
    WEB_SEARCH = "web_search"
    RUN_PYTHON = "run_python"


TEnv = TypeVar("TEnv", bound=EnvConfig)


class ToolBase(BaseModel, Generic[TEnv]):
    name: ToolType
    tool_env: TEnv
