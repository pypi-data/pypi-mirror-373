from typing import Optional

from seekrai.types.agents.tools.env_model_config import EnvConfig


class RunPythonEnv(EnvConfig):
    run_python_tool_desc: Optional[str] = None
    function_ids: Optional[list[str]] = None
