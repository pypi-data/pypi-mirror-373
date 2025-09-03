from pydantic import Field

from seekrai.types.agents.tools.env_model_config import EnvConfig


# TODO: figure out better way of creating tool environment models (within tool ideally), but retaining separate model_configs
class FileSearchEnv(EnvConfig):
    file_search_index: str = Field(min_length=1)
    document_tool_desc: str = Field(min_length=1)
    top_k: int = Field(
        default=10, ge=1, le=100, description="Top K must be >= 1 and <= 100"
    )
    score_threshold: float = Field(
        default=0, ge=0, lt=1.0, description="Score must be ≥ 0.0 and < 1.0"
    )
